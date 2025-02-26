from PyQt5 import QtWidgets, QtCore
import socket
from threading import Thread
import json
import os

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class CameraControllerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Godot Camera Controller")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.top_bar_layout = QtWidgets.QHBoxLayout()

        # ComboBox for presets
        self.preset_combobox = QtWidgets.QComboBox()
        self.preset_combobox.addItem("Selecione Predefinição")
        self.preset_combobox.currentIndexChanged.connect(self.load_preset)
        self.top_bar_layout.addWidget(self.preset_combobox)

        # Save and Delete buttons
        self.save_button = QtWidgets.QPushButton("Salvar Predefinição")
        self.save_button.clicked.connect(self.save_preset)
        self.delete_button = QtWidgets.QPushButton("Excluir Predefinição")
        self.delete_button.clicked.connect(self.delete_preset)
        self.top_bar_layout.addWidget(self.save_button)
        self.top_bar_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.top_bar_layout)

        # IP Field
        self.ip_entry = QtWidgets.QLineEdit("127.0.0.1")
        self.layout.addWidget(QtWidgets.QLabel("IP do Dispositivo Godot:"))
        self.layout.addWidget(self.ip_entry)

        # Reset Button
        self.reset_button = QtWidgets.QPushButton("Resetar Rotação")
        self.reset_button.clicked.connect(self.on_reset_click)
        self.layout.addWidget(self.reset_button)

        # IPD as Scale
        self.ipd_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.ipd_scale.setRange(0, 200)  # 0 to 20.0 as scale
        self.ipd_scale.setValue(20)  # Default 2.0
        self.ipd_label = QtWidgets.QLabel(f"Distância IPD: {self.ipd_scale.value() / 10}")
        self.ipd_scale.valueChanged.connect(self.update_ipd_label)
        self.layout.addWidget(self.ipd_label)
        self.layout.addWidget(self.ipd_scale)

        # SubviewportScale
        self.svs_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.svs_scale.setRange(10, 30)
        self.svs_scale.setValue(15)
        self.svs_label = QtWidgets.QLabel(f"Subviewport Scale: {self.svs_scale.value()}")
        self.svs_scale.valueChanged.connect(self.update_svs_label)
        self.layout.addWidget(self.svs_label)
        self.layout.addWidget(self.svs_scale)

        # Vr Filter Strength
        self.vfs_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.vfs_scale.setRange(0, 100)
        self.vfs_scale.setValue(0)
        self.vfs_label = QtWidgets.QLabel(f"Vr Filter Strength: {self.vfs_scale.value()}")
        self.vfs_scale.valueChanged.connect(self.update_vfs_label)
        self.layout.addWidget(self.vfs_label)
        self.layout.addWidget(self.vfs_scale)

        # Gyro Sensitive
        self.gs_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.gs_scale.setRange(0, 100)
        self.gs_scale.setValue(50)
        self.gs_label = QtWidgets.QLabel(f"Gyro Sensitive: {self.gs_scale.value()}")
        self.gs_scale.valueChanged.connect(self.update_gs_label)
        self.layout.addWidget(self.gs_label)
        self.layout.addWidget(self.gs_scale)

        # Send Values Button
        self.send_values_button = QtWidgets.QPushButton("Enviar Valores Ajustados")
        self.send_values_button.clicked.connect(self.on_send_values_click)
        self.layout.addWidget(self.send_values_button)

        self.load_presets()

    def update_ipd_label(self):
        """Atualiza o valor do IPD mostrado na label quando a escala for alterada."""
        self.ipd_label.setText(f"Distância IPD: {self.ipd_scale.value() / 10}")

    def update_svs_label(self):
        """Atualiza o valor do Subviewport Scale mostrado na label quando a escala for alterada."""
        self.svs_label.setText(f"Subviewport Scale: {self.svs_scale.value()}")

    def update_vfs_label(self):
        """Atualiza o valor do Vr Filter Strength mostrado na label quando a escala for alterada."""
        self.vfs_label.setText(f"Vr Filter Strength: {self.vfs_scale.value()}")

    def update_gs_label(self):
        """Atualiza o valor do Gyro Sensitive mostrado na label quando a escala for alterada."""
        self.gs_label.setText(f"Gyro Sensitive: {self.gs_scale.value()}")

    def load_presets(self):
        """Carregar predefinições do arquivo JSON."""
        if os.path.exists("presets.json"):
            with open("presets.json", "r") as f:
                presets = json.load(f)
            for preset in presets:
                self.preset_combobox.addItem(preset)

    def save_presets(self, preset_name, values):
        """Salvar predefinições em um arquivo JSON."""
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
        """Salvar a predefinição atual com um nome especificado."""
        preset_name, ok = QtWidgets.QInputDialog.getText(self, "Salvar Predefinição", "Nome da predefinição:")
        if ok and preset_name:
            values = {
                "ipd": self.ipd_scale.value() / 10,  # Transformando o valor da escala para valor real
                "subviewport_scale": self.svs_scale.value(),
                "vr_filter_strength": self.vfs_scale.value(),
                "gyro_sensitive": self.gs_scale.value()
            }
            self.save_presets(preset_name, values)
            self.preset_combobox.addItem(preset_name)
            QtWidgets.QMessageBox.information(self, "Sucesso", "Predefinição salva com sucesso!")

    def delete_preset(self):
        """Excluir a predefinição selecionada."""
        preset_name = self.preset_combobox.currentText()
        if preset_name == "Selecione Predefinição":
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione uma predefinição para excluir.")
            return

        presets = self.load_presets_from_file()
        if preset_name in presets:
            del presets[preset_name]
            with open("presets.json", "w") as f:
                json.dump(presets, f)

            self.preset_combobox.removeItem(self.preset_combobox.currentIndex())
            QtWidgets.QMessageBox.information(self, "Sucesso", "Predefinição excluída com sucesso!")

    def load_preset(self):
        """Carregar os valores de uma predefinição selecionada."""
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

    def send_ipd(self, ip, ipd_value, port=5005):
        self.send_message({"ipd": ipd_value}, ip, port)

    def send_subviewport_scale(self, ip, svs_value, port=5005):
        self.send_message({"subviewport_scale": svs_value}, ip, port)

    def send_vr_filter_strength(self, ip, vfs_value, port=5005):
        self.send_message({"vr_filter_strength": vfs_value}, ip, port)

    def send_gyro_sensitive(self, ip, gs_value, port=5005):
        self.send_message({"gyro_sensitive": gs_value}, ip, port)

    def send_message(self, message, ip, port=5005):
        try:
            data = json.dumps(message)
            sock.sendto(data.encode("utf-8"), (ip, port))
            QtWidgets.QMessageBox.information(self, "Sucesso", f"Sinal enviado com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro na conexão: {str(e)}")

    def on_reset_click(self):
        ip = self.ip_entry.text()
        if ip:
            Thread(target=self.send_reset, args=(ip,)).start()

    def on_send_values_click(self):
        ip = self.ip_entry.text()
        svs_value = self.svs_scale.value()
        vfs_value = self.vfs_scale.value()
        gs_value = self.gs_scale.value()

        Thread(target=self.send_subviewport_scale, args=(ip, svs_value)).start()
        Thread(target=self.send_vr_filter_strength, args=(ip, vfs_value)).start()
        Thread(target=self.send_gyro_sensitive, args=(ip, gs_value)).start()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = CameraControllerApp()
    window.resize(400, 400)
    window.show()
    app.exec_()
