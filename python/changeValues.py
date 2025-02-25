import tkinter as tk
from tkinter import ttk, messagebox
import socket
from threading import Thread
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class CameraControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Godot Camera Controller")

        # Frame principal
        self.frame = ttk.Frame(root, padding="20")
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Label e campo de entrada para o IP
        self.ip_label = ttk.Label(self.frame, text="IP do Dispositivo Godot:")
        self.ip_label.grid(row=0, column=0, sticky="w")

        self.ip_entry = ttk.Entry(self.frame, width=20)
        self.ip_entry.insert(0, "127.0.0.1")  # Valor padrão
        self.ip_entry.grid(row=0, column=1, padx=10, pady=10)

        # Botão para enviar o comando "reset"
        self.reset_button = ttk.Button(
            self.frame,
            text="Resetar Rotação",
            command=self.on_reset_click,
            width=20
        )
        self.reset_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Label e campo de entrada para a distância de divisão dos olhos (IPD)
        self.ipd_label = ttk.Label(self.frame, text="Distância IPD (valor padrão: 2):")
        self.ipd_label.grid(row=2, column=0, sticky="w", pady=10)

        self.ipd_entry = ttk.Entry(self.frame, width=10)
        self.ipd_entry.insert(0, "2")  # Valor padrão
        self.ipd_entry.grid(row=2, column=1, padx=10)

        # Botão para enviar o valor IPD
        self.ipd_button = ttk.Button(
            self.frame,
            text="Enviar Distância IPD",
            command=self.on_ipd_click,
            width=20
        )
        self.ipd_button.grid(row=3, column=0, columnspan=2, pady=10)

    def send_reset(self, ip, port=5005):
        try:
            message = {"reset": 0}
            data = json.dumps(message)
            sock.sendto(data.encode("utf-8"), (ip, port))
            print("Sinal de reset enviado com sucesso!")
            messagebox.showinfo("Sucesso", "Sinal de reset enviado com sucesso!")
        except Exception as e:
            print(f"Erro na conexão: {str(e)}")
            messagebox.showerror("Erro", f"Erro na conexão: {str(e)}")

    def send_ipd(self, ip, ipd_value, port=5005):
        try:
            message = {"ipd": ipd_value}
            data = json.dumps(message)
            sock.sendto(data.encode("utf-8"), (ip, port))
            print(f"Sinal de IPD ({ipd_value}) enviado com sucesso!")
            messagebox.showinfo("Sucesso", f"Sinal de IPD ({ipd_value}) enviado com sucesso!")
        except Exception as e:
            print(f"Erro na conexão: {str(e)}")
            messagebox.showerror("Erro", f"Erro na conexão: {str(e)}")

    def on_reset_click(self):
        ip = self.ip_entry.get()  # Obtém o IP do campo de entrada
        if not ip:
            messagebox.showwarning("Aviso", "Por favor, insira um IP válido.")
            return

        # Usa uma thread para enviar o comando sem travar a interface
        Thread(target=self.send_reset, args=(ip,)).start()

    def on_ipd_click(self):
        ip = self.ip_entry.get()  # Obtém o IP do campo de entrada
        ipd_value = self.ipd_entry.get()

        # Valida o valor de IPD
        try:
            ipd_value = float(ipd_value)
        except ValueError:
            messagebox.showwarning("Aviso", "Por favor, insira um valor válido para a distância IPD.")
            return

        # Usa uma thread para enviar o valor de IPD sem travar a interface
        Thread(target=self.send_ipd, args=(ip, ipd_value)).start()

if __name__ == "__main__":
    root = tk.Tk()

    # Melhorando a aparência da interface
    root.option_add("*TButton.padding", [10, 5])  # Ajusta o padding dos botões
    root.option_add("*Font", "Helvetica 10")

    app = CameraControllerApp(root)
    root.mainloop()
