extends Node2D
 
var udp = PacketPeerUDP.new()
var listening_port = 5005
var hands = {}
 
# Estrutura das conexões entre os pontos da mão (seguindo o MediaPipe)
var connections = [
	[0, 1], [1, 2], [2, 3], [3, 4],  # Polegar
	[0, 5], [5, 6], [6, 7], [7, 8],  # Indicador
	[0, 9], [9, 10], [10, 11], [11, 12],  # Médio
	[0, 13], [13, 14], [14, 15], [15, 16],  # Anelar
	[0, 17], [17, 18], [18, 19], [19, 20],  # Mindinho
	[5, 9], [9, 13], [13, 17]  # Ligações da palma
]
 
func _ready():
	udp.bind(listening_port)
	print("Aguardando dados da mão...")
 
func _process(_delta):
	if udp.get_available_packet_count() > 0:
		var packet = udp.get_packet()
		var message = packet.get_string_from_utf8()
		var hand_data = JSON.parse_string(message)
 
		if hand_data:
			hands = {}
			for hand in hand_data.keys():
				var raw_landmarks = hand_data[hand]["landmarks"]
				var screen_landmarks = []
 
				for lm in raw_landmarks:
					var x = int(lm["x"] * get_viewport().size.x)
					var y = int(lm["y"] * get_viewport().size.y)
					screen_landmarks.append(Vector2(x, y))
 
				hands[hand] = screen_landmarks
 
		queue_redraw()  # Agora está correto
 
func _draw():
	for hand in hands.values():
		for conn in connections:
			var p1 = hand[conn[0]]
			var p2 = hand[conn[1]]
			draw_line(p1, p2, Color(1, 1, 1), 3)  # Desenha as linhas brancas
 
		for point in hand:
			draw_circle(point, 5, Color(0, 1, 0))  # Desenha os pontos verdes
