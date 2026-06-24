"""
Modelo da gata Cacau — primitivas geométricas simples + cauda animada.
"""

import math


def render_cacau(renderer, position, time_sec):
    """
    Desenha a Cacau com cubos/esferas e cauda balançando.

    tailAngle = sin(time) * 20 graus
    """
    x, y, z = position
    tail_angle = math.sin(time_sec) * 20

    # Corpo
    renderer.render_object(
        renderer.cube_mesh,
        position=(x, y + 0.35, z),
        scale=(0.7, 0.45, 1.0),
        color=(180, 120, 60),
    )

    # Cabeça
    renderer.render_object(
        renderer.sphere_mesh,
        position=(x, y + 0.75, z + 0.55),
        scale=(0.38, 0.38, 0.38),
        color=(200, 140, 80),
    )

    # Orelhas (cubos inclinados)
    for ear_x in (-0.18, 0.18):
        renderer.render_object(
            renderer.cube_mesh,
            position=(x + ear_x, y + 1.05, z + 0.5),
            scale=(0.12, 0.18, 0.12),
            color=(160, 100, 50),
            rotation=(15, 0, ear_x * 80),
        )

    # Patas
    for paw_x, paw_z in [(-0.22, 0.3), (0.22, 0.3), (-0.22, -0.3), (0.22, -0.3)]:
        renderer.render_object(
            renderer.cube_mesh,
            position=(x + paw_x, y + 0.08, z + paw_z),
            scale=(0.12, 0.16, 0.12),
            color=(140, 90, 45),
        )

    # Cauda animada
    renderer.render_object(
        renderer.cube_mesh,
        position=(x, y + 0.45, z - 0.65),
        scale=(0.08, 0.08, 0.55),
        color=(160, 100, 50),
        rotation=(0, tail_angle, 0),
    )
