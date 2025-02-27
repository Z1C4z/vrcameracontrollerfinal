extends Node2D

var udp = PacketPeerUDP.new()
var listening_port = 5005
var hands = {}
var left_handpose = 'unkonow'
var right_handpose = 'unkonow'
var arrastando = false  # Variável para controlar o arrasto

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
			if not arrastando:
				print("Mãos detectadas:", hands.keys())
				arrastando = true
				
				arrastar_objeto(objeto_3d)
			else:
				arrastando = false
		 

func process_hand_data(hand_data):
	hands.clear()
	for hand in hand_data.keys():
		var raw_landmarks = hand_data[hand]["landmarks"]
		print(hand_data[hand]['pose'])
		var screen_landmarks = []
		
		for lm in raw_landmarks:
			var x = int(lm["x"] * get_viewport().size.x)
			var y = int(lm["y"] * get_viewport().size.y)
			screen_landmarks.append(Vector2(x, y))
		
		hands[hand] = screen_landmarks
	if hand_data.has("Left"):
		left_handpose = hand_data["Left"].get("pose", "none")
	else:
		left_handpose = "unknow"

	if hand_data.has("Right"):
		right_handpose = hand_data["Right"].get("pose", "none")
	else:
		right_handpose = "unknow"

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
	
func arrastar_objeto(obj: Node3D):
	if hands.has("Right") and hands["Right"].size() > 13 and right_handpose == 'close':
		var dedo_anelar = hands["Right"][13]
		var screen_pos = Vector2(dedo_anelar.x, dedo_anelar.y)

		# Projetar posição 2D da mão para coordenadas 3D
		var ray_origin = camera_3d.project_ray_origin(screen_pos)
		var ray_dir = camera_3d.project_ray_normal(screen_pos)
		var distancia = 5.0  # Reduzindo a distância para testar
		var new_position = ray_origin + (ray_dir * distancia)
		# Movendo o cubo SEM a verificação de `arrastando` para testar
		obj.global_transform.origin = obj.global_transform.origin.lerp(new_position, 0.2)
		
	elif hands.has("Left") and hands["Left"].size() > 13 and left_handpose == 'close':
		var dedo_anelar = hands["Left"][13]
		var screen_pos = Vector2(dedo_anelar.x, dedo_anelar.y)
		# Projetar posição 2D da mão para coordenadas 3D
		var ray_origin = camera_3d.project_ray_origin(screen_pos)
		var ray_dir = camera_3d.project_ray_normal(screen_pos)
		var distancia = 5.0  # Reduzindo a distância para testar
		var new_position = ray_origin + (ray_dir * distancia)
		# Movendo o cubo SEM a verificação de `arrastando` para testar
		obj.global_transform.origin = obj.global_transform.origin.lerp(new_position, 0.2)
