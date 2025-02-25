import tkinter as tk
from tkinter import messagebox
import socket
from threading import Thread
import json

class CameraControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Godot Camera Controller")

        # Frame principal
        self.frame = tk.Frame(root, padx=20, pady=20)
        self.frame.pack()

        # Label e campo de entrada para o IP
        self.ip_label = tk.Label(self.frame, text="IP do Dispositivo Godot:")
        self.ip_label.grid(row=0, column=0, sticky="w")

        self.ip_entry = tk.Entry(self.frame, width=15)
        self.ip_entry.insert(0, "192.168.0.")  # Valor padrão
        self.ip_entry.grid(row=0, column=1, padx=10, pady=10)

        # Botão para enviar o comando "reset"
        self.reset_button = tk.Button(
            self.frame,
            text="Resetar Rotação",
            command=self.on_reset_click,
            height=2,
            width=20
        )
        self.reset_button.grid(row=1, column=0, columnspan=2, pady=10)

    def send_reset(self, ip, port=5005):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, port))
                s.sendall("reset".encode("utf-8"))  # Envia o comando "reset"
            print("Sinal de reset enviado com sucesso!")
            messagebox.showinfo("Sucesso", "Sinal enviado com Sucesso!")
        except Exception as e:
            print(f"Erro na conexão: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao comunicar com a Aplicação!\n{e}")

    def on_reset_click(self):
        ip = self.ip_entry.get()  # Obtém o IP do campo de entrada
        if not ip:
            messagebox.showwarning("Aviso", "Por favor, insira um IP válido.")
            return

        # Usa uma thread para enviar o comando sem travar a interface
        Thread(target=self.send_reset, args=(ip,)).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraControllerApp(root)
    root.mainloop()