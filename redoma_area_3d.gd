extends Area3D

@export var obstaculo_scenes: Array[PackedScene]  # Outros planetas
@export var redoma: CollisionShape3D
@export var num_obstaculos: int = 10  # Quantidade total de planetas (sem contar Terra e Nave)
@export var min_distancia: float = 1.5  # Distância mínima entre planetas

@export var terra_scene: PackedScene  # Terra
@export var nave_scene: PackedScene  # Nave

var posicoes_geradas: Array[Vector3]  # Lista de posições já usadas

func _ready():
	if redoma == null:
		redoma = $CollisionShape3D
	gerar_obstaculos()

func gerar_obstaculos():
	if redoma == null:
		print("Erro: Redoma não está definida!")
		return

	if obstaculo_scenes.is_empty():
		print("Erro: Nenhum planeta foi adicionado à lista!")
		return

	var shape = redoma.shape
	if shape is CylinderShape3D:
		var raio = shape.radius
		var altura = shape.height * 0.5

		# Gera a Terra
		if terra_scene:
			criar_obstaculo_unico(terra_scene, raio, altura)

		# Gera a Nave
		if nave_scene:
			criar_obstaculo_unico(nave_scene, raio, altura)

		# Gera os outros planetas
		for i in range(num_obstaculos):  
			criar_obstaculo_aleatorio(raio, altura)

func criar_obstaculo_unico(scene: PackedScene, raio: float, altura: float):
	var nova_posicao: Vector3
	var tentativa = 0
	var max_tentativas = 10

	while tentativa < max_tentativas:
		var angulo = randf() * TAU
		var x = cos(angulo) * raio
		var z = sin(angulo) * raio
		var y = randf_range(-altura * 0.7, altura * 0.7)

		nova_posicao = Vector3(x, y, z)

		# Verifica se está muito perto de outro objeto
		var muito_perto = false
		for pos in posicoes_geradas:
			if pos.distance_to(nova_posicao) < min_distancia:
				muito_perto = true
				break

		if not muito_perto:
			posicoes_geradas.append(nova_posicao)
			break  

		tentativa += 1

	# Instancia e posiciona o objeto
	var obstaculo = scene.instantiate()
	obstaculo.position = nova_posicao
	add_child(obstaculo)

func criar_obstaculo_aleatorio(raio: float, altura: float):
	if obstaculo_scenes.is_empty():
		return

	var nova_posicao: Vector3
	var tentativa = 0
	var max_tentativas = 10

	while tentativa < max_tentativas:
		var angulo = randf() * TAU
		var x = cos(angulo) * raio
		var z = sin(angulo) * raio
		var y = randf_range(-altura * 0.7, altura * 0.7)

		nova_posicao = Vector3(x, y, z)

		var muito_perto = false
		for pos in posicoes_geradas:
			if pos.distance_to(nova_posicao) < min_distancia:
				muito_perto = true
				break

		if not muito_perto:
			posicoes_geradas.append(nova_posicao)
			break  

		tentativa += 1

	var random_scene = obstaculo_scenes.pick_random()
	var obstaculo = random_scene.instantiate()
	obstaculo.position = nova_posicao
	add_child(obstaculo)
