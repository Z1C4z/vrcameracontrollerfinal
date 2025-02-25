extends CharacterBody3D

# Configurações do servidor
var server_port = 57387
var server : TCPServer
var client : StreamPeerTCP

@export var gyroCam: Camera3D  # Referência para a câmera que será controlada

func _ready():
	start_server()
	# Configuração inicial da câmera

func start_server():
	server = TCPServer.new()
	if server.listen(server_port) == OK:
		print("Servidor iniciado na porta ", server_port)
	else:
		print("Erro ao iniciar servidor")

func _process(_delta):
	# Verificar novas conexões
	if server.is_connection_available():
		client = server.take_connection()
		print("Cliente conectado: ", client.get_connected_host())
	
	# Processar dados recebidos
	if client != null and client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		if client.get_available_bytes() > 0:
			print(client.to_string())
	
			reset_gyro_camera()

func reset_gyro_camera():
	if gyroCam and gyroCam.has_method("reset_rotation"):
		gyroCam.reset_rotation()  # Chamar o método reset_rotation da câmera
		print("Rotação da câmera resetada")
	else:
		print("Erro: gyroCam não tem um método reset_rotation ou não foi atribuído")

func _exit_tree():
	if server != null:
		server.stop()
