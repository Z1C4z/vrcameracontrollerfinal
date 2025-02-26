import cv2
import mediapipe as mp
import numpy as np
import socket
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

# Configuração do socket UDP
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Inicializa o MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Função para verificar se um dedo está esticado
def is_finger_extended(hand_landmarks, finger_tip, finger_dip):
    return hand_landmarks.landmark[finger_tip].y < hand_landmarks.landmark[finger_dip].y

# Função para calcular a distância entre dois pontos
def distance(a, b):
    return np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

# Função para identificar gestos
def detect_gesture(hand_landmarks):
    indicador = is_finger_extended(hand_landmarks, 8, 6)
    medio = is_finger_extended(hand_landmarks, 12, 10)
    anelar = is_finger_extended(hand_landmarks, 16, 14)
    mindinho = is_finger_extended(hand_landmarks, 20, 18)
    
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    thumb_index_dist = distance(thumb_tip, index_tip)

    if indicador and not medio and not anelar and not mindinho:
        return "Apontando"
    elif indicador and medio and anelar and mindinho:
        return "Mão Aberta"
    elif not indicador and not medio and not anelar and not mindinho:
        return "Mão Fechada"
    elif indicador and medio and not anelar and not mindinho:
        return "Número 2"
    else:
        return "Desconhecido"

class MainWindow(QMainWindow):
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
        
        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addWidget(self.pose_label)
        main_layout.addLayout(button_layout)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Variáveis de controle
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        # Configurações de socket e MediaPipe
        self.UDP_IP = UDP_IP
        self.UDP_PORT = UDP_PORT
        self.sock = sock
        self.mp_hands = mp_hands
        self.mp_drawing = mp_drawing
        self.mp_drawing_styles = mp_drawing_styles
        self.hands = hands

    def start_tracking(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        self.timer.start(30)  # Atualiza a cada 30ms (~33 FPS)
    
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
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                                                   self.mp_drawing_styles.get_default_hand_landmarks_style(),
                                                   self.mp_drawing_styles.get_default_hand_connections_style())
                    label = handedness.classification[0].label
                    pose = detect_gesture(hand_landmarks)
                    
                    landmarks = []
                    for lm in hand_landmarks.landmark:
                        landmarks.append({"x": lm.x, "y": lm.y})
                    hand_data[label] = {"landmarks": landmarks}
                    
                    pos = (50, 50 if label == "Right" else 100)
                    cv2.putText(frame, f"{label}: {pose}", pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Envia os dados via UDP
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

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
