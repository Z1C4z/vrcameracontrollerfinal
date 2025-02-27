import sys
import os
import json
import socket
import cv2
import mediapipe as mp
import numpy as np
from threading import Thread

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox, QTabWidget, QStatusBar
)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

# Cria o socket UDP que será compartilhado
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

##############################################
# Estilos Minimalistas para Tema Claro e Escuro
##############################################
light_stylesheet = """
QMainWindow, QWidget {
    background-color: #ffffff;
    color: #000;
    font-family: "Segoe UI", sans-serif;
    font-size: 10pt;
}
QPushButton {
    background-color: #e6e6e6;
    border: 1px solid #ccc;
    border-radius: 3px;
    padding: 5px 10px;
}
QPushButton:hover {
    background-color: #d9d9d9;
}
QLineEdit, QComboBox, QSlider {
    background-color: #ffffff;
    border: 1px solid #ccc;
    border-radius: 3px;
    padding: 3px;
}
QLabel {
    color: #000;
}
QTabWidget::pane {
    border: none;
    background-color: #ffffff;
}
QTabBar::tab {
    background: #e6e6e6;
    padding: 8px;
    margin: 2px;
    border-radius: 3px;
    color: #000;
}
QTabBar::tab:selected {
    background: #ffffff;
    border-bottom: 2px solid #0078d7;
}
"""

dark_stylesheet = """
QMainWindow, QWidget {
    background-color: #121212;
    color: #e0e0e0;
    font-family: "Segoe UI", sans-serif;
    font-size: 10pt;
}
QPushButton {
    background-color: #2a2a2a;
    border: 1px solid #333;
    border-radius: 3px;
    padding: 5px 10px;
}
QPushButton:hover {
    background-color: #333333;
}
QLineEdit, QComboBox, QSlider {
    background-color: #1e1e1e;
    border: 1px solid #333;
    border-radius: 3px;
    padding: 3px;
    color: #e0e0e0;
}
QLabel {
    color: #e0e0e0;
}
QTabWidget::pane {
    border: none;
    background-color: #121212;
}
QTabBar::tab {
    background: #1e1e1e;
    padding: 8px;
    margin: 2px;
    border-radius: 3px;
    color: #e0e0e0;
}
QTabBar::tab:selected {
    background: #121212;
    border-bottom: 2px solid #0078d7;
}
"""

##############################################
# Painel de Controle - Versão Minimalista
##############################################
class CameraControllerApp(QWidget):
    message_signal = pyqtSignal(str, str)  # (tipo, mensagem)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Godot Camera Controller")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.message_signal.connect(self.show_message)

        # Combobox de predefinições e botões (sem sombras ou ícones)
        top_layout = QHBoxLayout()
        self.preset_combobox = QtWidgets.QComboBox()
        self.preset_combobox.addItem("Selecione Predefinição")
        self.preset_combobox.currentIndexChanged.connect(self.load_preset)
        top_layout.addWidget(self.preset_combobox)

        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_preset)
        top_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Excluir")
        self.delete_button.clicked.connect(self.delete_preset)
        top_layout.addWidget(self.delete_button)
        layout.addLayout(top_layout)

        # Campo para IP do dispositivo Godot
        layout.addWidget(QLabel("IP do Dispositivo Godot:"))
        self.ip_entry = QtWidgets.QLineEdit("127.0.0.1")
        layout.addWidget(self.ip_entry)

        # Botão de reset
        self.reset_button = QPushButton("Resetar Rotação")
        self.reset_button.clicked.connect(self.on_reset_click)
        layout.addWidget(self.reset_button)

        # Slider IPD
        self.ipd_label = QLabel("Distância IPD: 2.0")
        layout.addWidget(self.ipd_label)
        self.ipd_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.ipd_scale.setRange(0, 200)
        self.ipd_scale.setValue(20)
        self.ipd_scale.valueChanged.connect(self.update_ipd_label)
        layout.addWidget(self.ipd_scale)

        # Slider Subviewport Scale
        self.svs_label = QLabel("Subviewport Scale: 1.5")
        layout.addWidget(self.svs_label)
        self.svs_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.svs_scale.setRange(10, 30)  # 10 -> 1.0, 30 -> 3.0
        self.svs_scale.setValue(15)
        self.svs_scale.valueChanged.connect(self.update_svs_label)
        layout.addWidget(self.svs_scale)

        # Slider Gyro Sensitive
        self.gs_label = QLabel("Gyro Sensitive: 50")
        layout.addWidget(self.gs_label)
        self.gs_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.gs_scale.setRange(0, 100)
        self.gs_scale.setValue(50)
        self.gs_scale.valueChanged.connect(self.update_gs_label)
        layout.addWidget(self.gs_scale)

        # Botão para enviar valores
        self.send_values_button = QPushButton("Enviar Valores")
        self.send_values_button.clicked.connect(self.on_send_values_click)
        layout.addWidget(self.send_values_button)

        self.load_presets()

    def show_message(self, msg_type, message):
        if msg_type == "info":
            QMessageBox.information(self, "Sucesso", message)
        elif msg_type == "error":
            QMessageBox.critical(self, "Erro", message)

    def update_ipd_label(self):
        self.ipd_label.setText(f"Distância IPD: {self.ipd_scale.value() / 10:.1f}")

    def update_svs_label(self):
        self.svs_label.setText(f"Subviewport Scale: {self.svs_scale.value() / 10:.1f}")

    def update_gs_label(self):
        self.gs_label.setText(f"Gyro Sensitive: {self.gs_scale.value()}")

    def load_presets(self):
        if os.path.exists("presets.json"):
            with open("presets.json", "r") as f:
                presets = json.load(f)
            for preset in presets:
                self.preset_combobox.addItem(preset)

    def save_presets(self, preset_name, values):
        presets = self.load_presets_from_file()
        presets[preset_name] = values
        with open("presets.json", "w") as f:
            json.dump(presets, f)

    def load_presets_from_file(self):
        if os.path.exists("presets.json"):
            with open("presets.json", "r") as f:
                return json.load(f)
        return {}

    def save_preset(self):
        preset_name, ok = QInputDialog.getText(self, "Salvar Predefinição", "Nome da predefinição:")
        if ok and preset_name:
            values = {
                "ipd": self.ipd_scale.value() / 10,
                "subviewport_scale": self.svs_scale.value() / 10,
                "gyro_sensitive": self.gs_scale.value()
            }
            self.save_presets(preset_name, values)
            self.preset_combobox.addItem(preset_name)
            self.message_signal.emit("info", "Predefinição salva com sucesso!")

    def delete_preset(self):
        preset_name = self.preset_combobox.currentText()
        if preset_name == "Selecione Predefinição":
            self.message_signal.emit("error", "Selecione uma predefinição para excluir.")
            return

        presets = self.load_presets_from_file()
        if preset_name in presets:
            del presets[preset_name]
            with open("presets.json", "w") as f:
                json.dump(presets, f)
            self.preset_combobox.removeItem(self.preset_combobox.currentIndex())
            self.message_signal.emit("info", "Predefinição excluída com sucesso!")

    def load_preset(self):
        preset_name = self.preset_combobox.currentText()
        if preset_name == "Selecione Predefinição":
            return
        presets = self.load_presets_from_file()
        if preset_name in presets:
            values = presets[preset_name]
            self.ipd_scale.setValue(int(values["ipd"] * 10))
            self.svs_scale.setValue(int(values["subviewport_scale"] * 10))
            self.gs_scale.setValue(values["gyro_sensitive"])

    def send_reset(self, ip, port=5005):
        self.send_message({"reset": 0}, ip, port)

    def send_message(self, message, ip, port=5005):
        try:
            data = json.dumps(message)
            sock.sendto(data.encode("utf-8"), (ip, port))
            self.message_signal.emit("info", "Sinal enviado com sucesso!")
        except Exception as e:
            self.message_signal.emit("error", f"Erro na conexão: {str(e)}")

    def on_reset_click(self):
        ip = self.ip_entry.text()
        if ip:
            Thread(target=self.send_reset, args=(ip,)).start()

    def on_send_values_click(self):
        ip = self.ip_entry.text()
        data = {
            "ipd": self.ipd_scale.value() / 10,
            "subviewport_scale": self.svs_scale.value() / 10,
            "gyro_sensitive": self.gs_scale.value()
        }
        Thread(target=self.send_message, args=(data, ip)).start()

##############################################
# Área de Hand Tracking - Versão Minimalista
##############################################
class HandTrackingWidget(QWidget):
    def __init__(self, ip_getter):
        """
        ip_getter: função que retorna o valor atual do IP (do campo ip_entry)
        """
        super().__init__()
        self.setWindowTitle("Hand Pose Detection")
        self.ip_getter = ip_getter
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Área de vídeo com placeholder
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.set_placeholder()
        layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        
        # Rótulo de pose detectada
        self.pose_label = QLabel("Pose da Mão: Desconhecida")
        self.pose_label.setAlignment(Qt.AlignCenter)
        self.pose_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.pose_label)
        
        # Botões de controle
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.start_tracking)
        buttons_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Parar")
        self.stop_button.clicked.connect(self.stop_tracking)
        buttons_layout.addWidget(self.stop_button)
        layout.addLayout(buttons_layout)
        
        # Variáveis de controle
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        # Configuração do MediaPipe
        self.sock = sock
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def set_placeholder(self):
        placeholder_color = QtGui.QColor("#cccccc")
        image = QImage(640, 480, QImage.Format_RGB888)
        image.fill(placeholder_color)
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def start_tracking(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(30)

    def update_frame(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                return
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            pose = "Desconhecida"
            hand_data = {}
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    label = handedness.classification[0].label
                    pose = self.detect_gesture(hand_landmarks)
                    landmarks = [{"x": lm.x, "y": lm.y} for lm in hand_landmarks.landmark]
                    hand_data[label] = {"landmarks": landmarks}

            if hand_data:
                message = json.dumps(hand_data)
                udp_ip = self.ip_getter()
                self.sock.sendto(message.encode(), (udp_ip, 5005))

            self.pose_label.setText(f"Pose da Mão: {pose}")
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(self.video_label.size(), Qt.KeepAspectRatio))

    def stop_tracking(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.set_placeholder()

    def is_finger_extended(self, hand_landmarks, finger_tip, finger_dip):
        return hand_landmarks.landmark[finger_tip].y < hand_landmarks.landmark[finger_dip].y

    def detect_gesture(self, hand_landmarks):
        indicador = self.is_finger_extended(hand_landmarks, 8, 6)
        medio = self.is_finger_extended(hand_landmarks, 12, 10)
        anelar = self.is_finger_extended(hand_landmarks, 16, 14)
        mindinho = self.is_finger_extended(hand_landmarks, 20, 18)
        
        if indicador and not medio and not anelar and not mindinho:
            return "Apontando"
        elif indicador and medio and anelar and mindinho:
            return "Mão Aberta"
        elif not indicador and not medio and not anelar and not mindinho:
            return "Mão Fechada"
        elif indicador and medio and not anelar and not mindinho:
            return "Número 2"
        else:
            return "Desconhecida"

##############################################
# Janela Principal Minimalista com Abas e Status Bar
##############################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicativo Unificado")
        self.setFixedSize(800, 600)

        # Aplica o tema claro como padrão
        self.current_theme = "light"
        QApplication.instance().setStyleSheet(light_stylesheet)

        # Cria abas simples para os módulos
        self.tabs = QTabWidget()
        self.camera_controller = CameraControllerApp()
        self.hand_tracking = HandTrackingWidget(ip_getter=lambda: self.camera_controller.ip_entry.text())
        self.tabs.addTab(self.camera_controller, "Controles")
        self.tabs.addTab(self.hand_tracking, "Hand Tracking")
        self.setCentralWidget(self.tabs)

        # Menu de opções minimalista
        self.create_menu()

        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_menu(self):
        menu_bar = self.menuBar()
        theme_menu = menu_bar.addMenu("Tema")
        light_action = theme_menu.addAction("Tema Claro")
        dark_action = theme_menu.addAction("Tema Escuro")
        light_action.triggered.connect(self.set_light_theme)
        dark_action.triggered.connect(self.set_dark_theme)
        help_menu = menu_bar.addMenu("Ajuda")
        about_action = help_menu.addAction("Sobre")
        about_action.triggered.connect(self.show_about)

    def set_light_theme(self):
        QApplication.instance().setStyleSheet(light_stylesheet)
        self.current_theme = "light"
        self.status_bar.showMessage("Tema claro ativado", 3000)

    def set_dark_theme(self):
        QApplication.instance().setStyleSheet(dark_stylesheet)
        self.current_theme = "dark"
        self.status_bar.showMessage("Tema escuro ativado", 3000)

    def show_about(self):
        QMessageBox.information(self, "Sobre", "Aplicativo Unificado\nVersão 1.0\nDesenvolvido com PyQt5.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
