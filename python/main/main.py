import sys
import os
import json
import socket
import cv2
import mediapipe as mp
import numpy as np
from threading import Thread

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

# Cria o socket UDP que será compartilhado
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

###############################
# Painel de Controle - Código 1
###############################
class CameraControllerApp(QWidget):
    message_signal = pyqtSignal(str, str)  # (tipo, mensagem)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Godot Camera Controller")
        self.layout = QVBoxLayout(self)
        self.message_signal.connect(self.show_message)

        # Barra superior com combobox e botões
        self.top_bar_layout = QHBoxLayout()
        self.preset_combobox = QtWidgets.QComboBox()
        self.preset_combobox.addItem("Selecione Predefinição")
        self.preset_combobox.currentIndexChanged.connect(self.load_preset)
        self.top_bar_layout.addWidget(self.preset_combobox)

        self.save_button = QtWidgets.QPushButton("Salvar Predefinição")
        self.save_button.clicked.connect(self.save_preset)
        self.delete_button = QtWidgets.QPushButton("Excluir Predefinição")
        self.delete_button.clicked.connect(self.delete_preset)
        self.top_bar_layout.addWidget(self.save_button)
        self.top_bar_layout.addWidget(self.delete_button)
        self.layout.addLayout(self.top_bar_layout)

        # Campo para IP
        self.ip_entry = QtWidgets.QLineEdit("127.0.0.1")
        self.layout.addWidget(QtWidgets.QLabel("IP do Dispositivo Godot:"))
        self.layout.addWidget(self.ip_entry)

        # Botão de reset
        self.reset_button = QtWidgets.QPushButton("Resetar Rotação")
        self.reset_button.clicked.connect(self.on_reset_click)
        self.layout.addWidget(self.reset_button)

        # Slider IPD
        self.ipd_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.ipd_scale.setRange(0, 200)
        self.ipd_scale.setValue(20)
        self.ipd_label = QtWidgets.QLabel(f"Distância IPD: {self.ipd_scale.value() / 10}")
        self.ipd_scale.valueChanged.connect(self.update_ipd_label)
        self.layout.addWidget(self.ipd_label)
        self.layout.addWidget(self.ipd_scale)

        # Slider Subviewport Scale
        self.svs_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.svs_scale.setRange(10, 30)
        self.svs_scale.setValue(15)
        self.svs_label = QtWidgets.QLabel(f"Subviewport Scale: {self.svs_scale.value()}")
        self.svs_scale.valueChanged.connect(self.update_svs_label)
        self.layout.addWidget(self.svs_label)
        self.layout.addWidget(self.svs_scale)

        # Slider Vr Filter Strength
        self.vfs_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.vfs_scale.setRange(0, 100)
        self.vfs_scale.setValue(0)
        self.vfs_label = QtWidgets.QLabel(f"Vr Filter Strength: {self.vfs_scale.value()}")
        self.vfs_scale.valueChanged.connect(self.update_vfs_label)
        self.layout.addWidget(self.vfs_label)
        self.layout.addWidget(self.vfs_scale)

        # Slider Gyro Sensitive
        self.gs_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.gs_scale.setRange(0, 100)
        self.gs_scale.setValue(50)
        self.gs_label = QtWidgets.QLabel(f"Gyro Sensitive: {self.gs_scale.value()}")
        self.gs_scale.valueChanged.connect(self.update_gs_label)
        self.layout.addWidget(self.gs_label)
        self.layout.addWidget(self.gs_scale)

        # Botão para enviar valores ajustados
        self.send_values_button = QtWidgets.QPushButton("Enviar Valores Ajustados")
        self.send_values_button.clicked.connect(self.on_send_values_click)
        self.layout.addWidget(self.send_values_button)

        self.load_presets()

    def show_message(self, msg_type, message):
        if msg_type == "info":
            QMessageBox.information(self, "Sucesso", message)
        elif msg_type == "error":
            QMessageBox.critical(self, "Erro", message)

    def update_ipd_label(self):
        self.ipd_label.setText(f"Distância IPD: {self.ipd_scale.value() / 10}")

    def update_svs_label(self):
        self.svs_label.setText(f"Subviewport Scale: {self.svs_scale.value()}")

    def update_vfs_label(self):
        self.vfs_label.setText(f"Vr Filter Strength: {self.vfs_scale.value()}")

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
                "subviewport_scale": self.svs_scale.value(),
                "vr_filter_strength": self.vfs_scale.value(),
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
            self.svs_scale.setValue(values["subviewport_scale"])
            self.vfs_scale.setValue(values["vr_filter_strength"])
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
            "subviewport_scale": self.svs_scale.value(),
            "vr_filter_strength": self.vfs_scale.value(),
            "gyro_sensitive": self.gs_scale.value()
        }
        Thread(target=self.send_message, args=(data, ip)).start()

#######################################
# Área de Hand Tracking - Código 2 (Adaptado)
#######################################
class HandTrackingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hand Pose Detection")

        # Widgets
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.pose_label = QLabel("Pose da Mão: Desconhecida")
        self.pose_label.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton("Iniciar Rastreamento")
        self.stop_button = QPushButton("Parar Rastreamento")
        self.start_button.clicked.connect(self.start_tracking)
        self.stop_button.clicked.connect(self.stop_tracking)

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addWidget(self.pose_label)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Variáveis de controle
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # Configurações de socket e MediaPipe
        self.UDP_IP = "127.0.0.1"
        self.UDP_PORT = 5005
        self.sock = sock
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def start_tracking(self):
        if self.cap is None:
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

            pose = "unknow"
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
                    
                    landmarks = []
                    for lm in hand_landmarks.landmark:
                        landmarks.append({"x": lm.x, "y": lm.y})
                    hand_data[label] = {"landmarks": landmarks, "pose":pose}
                    
                    pos = (50, 50 if label == "Right" else 100)
                    cv2.putText(frame, f"{label}: {pose}", pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if hand_data:
                message = json.dumps(hand_data)
                self.sock.sendto(message.encode(), (self.UDP_IP, self.UDP_PORT))

            self.pose_label.setText(f"Pose da Mão: {pose}")

            # Converte a imagem para QImage e atualiza o QLabel
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def stop_tracking(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.video_label.clear()

    def is_finger_extended(self, hand_landmarks, finger_tip, finger_dip):
        return hand_landmarks.landmark[finger_tip].y < hand_landmarks.landmark[finger_dip].y

    def distance(self, a, b):
        return np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    def detect_gesture(self, hand_landmarks):
        indicador = self.is_finger_extended(hand_landmarks, 8, 6)
        medio = self.is_finger_extended(hand_landmarks, 12, 10)
        anelar = self.is_finger_extended(hand_landmarks, 16, 14)
        mindinho = self.is_finger_extended(hand_landmarks, 20, 18)
        
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        thumb_index_dist = self.distance(thumb_tip, index_tip)

        if indicador and not medio and not anelar and not mindinho:
            return "pointer"
        elif indicador and medio and anelar and mindinho:
            return "open"
        elif not indicador and not medio and not anelar and not mindinho:
            return "close"
        elif indicador and medio and not anelar and not mindinho:
            return "two"
        else:
            return "unknow"

#######################################
# Janela Principal com Layout Horizontal
#######################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicativo Unificado")

        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        self.camera_controller = CameraControllerApp()
        self.hand_tracking = HandTrackingWidget()

        layout.addWidget(self.camera_controller)
        layout.addWidget(self.hand_tracking)

        self.setCentralWidget(central_widget)
        self.resize(900, 500)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())