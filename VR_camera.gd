extends Camera3D

@export var left_eye_control: Control
@export var right_eye_control: Control
@export var subview_port: SubViewport
@export var divide_value: float = 2
@export var subviewport_scale: float = 1.5
@export var vr_filter_strength: float = 0  # Força do filtro VR (0 a 1)
@export var gyro_sensitivity: float = 50.0  # Sensibilidade do giroscópio

var half_screen_size: Vector2
var left_eye_position: Vector2
var right_eye_position: Vector2
var distance_value: float
var default_position = Vector3(0, 13, 0)  # Posição fixa da câmera
var defaultData = {}
var base_subviewport_size: Vector2  # Armazena o tamanho inicial do SubViewport

func _ready():
	base_subviewport_size = subview_port.size  # Salva o tamanho original
	defaultData["subviewport_scale"] = subviewport_scale
	defaultData["ipd"] = divide_value
	defaultData["vr_filter_strength"] = vr_filter_strength
	defaultData["gyro_sensitivity"] = gyro_sensitivity
	setValues(defaultData)

func setValues(values: Dictionary):
	Input.set_use_accumulated_input(true)
	
	# Sempre redefinir o tamanho com base no valor inicial
	subview_port.size = base_subviewport_size * values["subviewport_scale"]
	
	half_screen_size = DisplayServer.screen_get_size() / 2    
	
	# Calcular a distância entre os olhos
	distance_value = half_screen_size.x / values["ipd"]
	
	# Definir as posições iniciais para os controles dos olhos
	left_eye_position = Vector2(half_screen_size.x - distance_value, half_screen_size.y)
	right_eye_position = Vector2(half_screen_size.x + distance_value, half_screen_size.y)
	
	left_eye_control.position = left_eye_position
	right_eye_control.position = right_eye_position
	
	# Atualizar configurações de sensibilidade e filtro
	gyro_sensitivity = values["gyro_sensitivity"]
	vr_filter_strength = values["vr_filter_strength"]
	
	# Garantir que a câmera comece na posição correta
	global_position = default_position

func _process(delta):
	# Manter a câmera sempre na mesma posição
	global_position = default_position
	
	# Obter dados do giroscópio
	var gyro = Input.get_gyroscope()
	
	# Aplicar rotação baseada no giroscópio
	if gyro != Vector3.ZERO:
		rotation_degrees.x += gyro.x * delta * gyro_sensitivity  # Inclinação (para cima/baixo)
		rotation_degrees.y += gyro.y * delta * gyro_sensitivity  # Rotação lateral (olhar pros lados)
	
	# Atualizar as posições dos controles dos olhos (opcional, se necessário)
	left_eye_control.position = left_eye_position
	right_eye_control.position = right_eye_position

func reset_rotation():
	# Zera a rotação da câmera (olhando para frente no eixo Z)
	rotation_degrees = Vector3.ZERO
