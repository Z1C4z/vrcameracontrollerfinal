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
			if sinal.keys.contains("reset"):
				reset_gyro_camera()
			else: if sinal.keys.contais("ipd"):
				updateData(sinal)

func reset_gyro_camera():
	if gyroCam and gyroCam.has_method("reset_rotation"):
		gyroCam.reset_rotation()  # Chamar o método reset_rotation da câmera
		print("Rotação da câmera resetada")
	else:
		print("Erro: gyroCam não tem um método reset_rotation ou não foi atribuído")
		
func updateData(data: Dictionary):
	$SubViewport/GyroCam.divide_value = data["ipd"]
	$SubViewport/GyroCam.subviewport_scale = data["subviewport_scale"]
	$SubViewport/GyroCam.vr_filter_strength = data["vr_filter_strength"]
	$SubViewport/GyroCam.gyro_sensitivity = data["gyro_sensitive"]
	$SubViewport/GyroCam._ready()
