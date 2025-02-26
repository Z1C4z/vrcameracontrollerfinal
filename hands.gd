extends Node2D

var udp = PacketPeerUDP.new()
var listening_port = 5005
var hands = {}
var left_handpose = 'none'
var right_handpose = 'none'

# Conexões entre landmarks da mão (índices baseados no MediaPipe Hands)
var connections = [
	[0,1], [1,2], [2,3], [3,4],         # Polegar
	[0,5], [5,6], [6,7], [7,8],         # Indicador
	[0,9], [9,10], [10,11], [11,12],     # Médio
	[0,13], [13,14], [14,15], [15,16],   # Anelar
	[0,17], [17,18], [18,19], [19,20]    # Mínimo
]

@onready var camera_3d = get_node_or_null("/root/Node3D/player/SubViewport/GyroCam")
@onready var objeto_3d = get_node_or_null("/root/Node3D/box")

func _ready():
	if udp.bind(listening_port) != OK:
		push_error("Falha ao vincular à porta UDP")
		return
	print("Aguardando dados da mão...")

func _process(_delta):
	if udp.get_available_packet_count() > 0:
		var packet = udp.get_packet()
		var message = packet.get_string_from_utf8()
		var json = JSON.new()
		var error = json.parse(message)
		
		if error == OK:
			process_hand_data(json.data)
		else:
			push_error("Erro ao analisar JSON: ", json.get_error_message())

	if camera_3d and objeto_3d:
		if is_hand_over_object(objeto_3d, camera_3d):
			print("A mão está sobre o objeto 3D!")

func process_hand_data(hand_data):
	hands.clear()
	left_handpose = hand_data['left']['pose']
	print(left_handpose)
	right_handpose = hand_data['right']['pose']
	print(right_handpose)
	for hand in hand_data.keys():
		var raw_landmarks = hand_data[hand]["landmarks"]
		var screen_landmarks = []
		
		for lm in raw_landmarks:
			var x = int(lm["x"] * get_viewport().size.x)
			var y = int(lm["y"] * get_viewport().size.y)
			screen_landmarks.append(Vector2(x, y))
		
		hands[hand] = screen_landmarks
	queue_redraw()

func _draw():
	for hand in hands.values():
		# Desenhar conexões
		for conn in connections:
			if conn[0] < hand.size() and conn[1] < hand.size():
				draw_line(hand[conn[0]], hand[conn[1]], Color(1, 1, 1), 3)
		
		# Desenhar pontos
		for point in hand:
			draw_circle(point, 5, Color(0, 1, 0))

func world_to_screen(object_3d: Node3D, camera: Camera3D) -> Vector2:
	if camera:
		return camera.unproject_position(object_3d.global_transform.origin)
	return Vector2.ZERO

func is_hand_over_object(object_3d: Node3D, camera: Camera3D) -> bool:
	var screen_pos = world_to_screen(object_3d, camera)
	
	for hand in hands.values():
		if hand.size() >= 3:
			var hull = Geometry2D.convex_hull(hand)
			if Geometry2D.is_point_in_polygon(screen_pos, hull):
				return true
	return false
