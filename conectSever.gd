extends CharacterBody3D

@export var gyroCam: Camera3D  # Referência para a câmera que será controlada

var udp = PacketPeerUDP.new()
var listening_port = 5005

func _ready():
	udp.bind(listening_port)
	print("Aguardando Sinais")
	# Configuração inicial da câmera

func _process(_delta):
	if udp.get_available_packet_count() > 0:
		var packet = udp.get_packet()
		var message = packet.get_string_from_utf8()
		var sinal = JSON.parse_string(message)
		
		if sinal:
			print(sinal);

func reset_gyro_camera():
	if gyroCam and gyroCam.has_method("reset_rotation"):
		gyroCam.reset_rotation()  # Chamar o método reset_rotation da câmera
		print("Rotação da câmera resetada")
	else:
		print("Erro: gyroCam não tem um método reset_rotation ou não foi atribuído")
		
func change_divide_value(value: float):
	$SubViewport/GyroCam.divide_value = value
	$SubViewport/GyroCam._ready()
	print($SubViewport/GyroCam.divide_value)
