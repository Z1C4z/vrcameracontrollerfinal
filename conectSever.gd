extends CharacterBody3D

# Configurações do servidor
var udp = PacketPeerUDP.new()
var listening_port = 5005

@export var gyroCam: Camera3D  # Referência para a câmera que será controlada

func _ready():
	start_server()
	# Configuração inicial da câmera

func start_server():
	udp.bind(listening_port)

func _process(_delta):
	if udp.get_available_packet_count() > 0:
		var packet = udp.get_packet()
		var message = packet.get_string_from_utf8()
		print(message)

func reset_gyro_camera():
	if gyroCam and gyroCam.has_method("reset_rotation"):
		gyroCam.reset_rotation()  # Chamar o método reset_rotation da câmera
		print("Rotação da câmera resetada")
	else:
		print("Erro: gyroCam não tem um método reset_rotation ou não foi atribuído")
