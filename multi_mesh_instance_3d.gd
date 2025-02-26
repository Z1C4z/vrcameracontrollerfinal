extends MultiMeshInstance3D

@onready var camera = $"/root/Node3D/player/SubViewPort/GyroCam"  # Caminho até a câmera
@onready var area3d = $"StaticBody3D/Area3D"  # Caminho até o Area3D
# @onready var hand = $

func update_hand_positions(hand_points: Array):
	var mesh = multimesh
	mesh.instance_count = hand_points.size()

	for i in range(hand_points.size()):
		var point_2d = hand_points[i]
		
		# Converte para coordenadas 3D
		var from = camera.project_ray_origin(point_2d)
		var to = from + camera.project_ray_normal(point_2d) * 10  # Ajuste a profundidade
		var point_3d = to  

		# Define a posição do ponto no MultiMesh
		var transform = Transform3D()
		transform.origin = point_3d
		mesh.set_instance_transform(i, transform)

	check_collision()

# Verifica se os pontos da mão estão dentro da área
func check_collision():
	var overlapping = area3d.get_overlapping_areas()
	if overlapping.size() > 0:
		print("Mão dentro da área:", overlapping)


func _on_area_3d_area_entered(area: Area3D) -> void:
	print('colidido') # Replace with function body.
