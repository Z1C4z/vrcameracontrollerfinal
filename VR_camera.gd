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

func _ready():
	# Ativar o giroscópio
	Input.set_use_accumulated_input(true)
	
	# Definir o tamanho do SubViewport
	subview_port.size = subview_port.size * subviewport_scale
	half_screen_size = DisplayServer.screen_get_size() / 2	
	
	# Calcular a distância entre os olhos
	distance_value = half_screen_size.x / divide_value
	
	# Definir as posições iniciais para os controles dos olhos
	left_eye_position = Vector2(half_screen_size.x - distance_value, half_screen_size.y)
	right_eye_position = Vector2(half_screen_size.x + distance_value, half_screen_size.y)
	
	left_eye_control.position = left_eye_position
	right_eye_control.position = right_eye_position
	
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

# Converte uma posição 3D para coordenadas 2D da tela
func world_to_screen(object_3d: Node3D, camera: Camera3D) -> Vector2:
	var screen_pos = camera.unproject_position(object_3d.global_transform.origin)
	return screen_pos
