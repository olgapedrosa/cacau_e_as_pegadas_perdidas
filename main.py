"""
CACAU E AS PEGADAS PERDIDAS
Passeio Virtual 3D em OpenGL 4.0

Mapa: Quintal → Rua → Cacau
Controles: WASD/Setas + Mouse | ESC para sair
"""

import os
import math
import sys

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *

import shaders
import camera
import objects
from textures import Texture
import cat

# Constantes da janela
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Posição da Cacau no final da rua
CACAU_POS = np.array([0.0, 0.0, 44.0], dtype=np.float32)
WIN_DISTANCE = 3.0

# Caminho das pegadas: quintal (z negativo) → rua (z positivo)
FOOTPRINTS = []
for i in range(8):
    z = -12 + i * 1.5
    offset = 0.2 if i % 2 == 0 else -0.2
    FOOTPRINTS.append((offset, 0.04, z))
    FOOTPRINTS.append((-offset, 0.04, z + 0.35))

for i in range(22):
    z = 1.5 + i * 1.9
    offset = 0.18 if i % 2 == 0 else -0.18
    FOOTPRINTS.append((offset, 0.04, z))
    FOOTPRINTS.append((-offset, 0.04, z + 0.35))


def rotation_y(degrees):
    """Matriz 4x4 de rotação em torno do eixo Y."""
    rad = math.radians(degrees)
    c, s = math.cos(rad), math.sin(rad)
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = c
    m[0, 2] = s
    m[2, 0] = -s
    m[2, 2] = c
    return m


def rotation_x(degrees):
    """Matriz 4x4 de rotação em torno do eixo X."""
    rad = math.radians(degrees)
    c, s = math.cos(rad), math.sin(rad)
    m = np.identity(4, dtype=np.float32)
    m[1, 1] = c
    m[1, 2] = -s
    m[2, 1] = s
    m[2, 2] = c
    return m


def rotation_z(degrees):
    """Matriz 4x4 de rotação em torno do eixo Z."""
    rad = math.radians(degrees)
    c, s = math.cos(rad), math.sin(rad)
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = c
    m[0, 1] = -s
    m[1, 0] = s
    m[1, 1] = c
    return m


def make_model_matrix(position, scale=(1, 1, 1), rotation=(0, 0, 0)):
    """Constrói matriz model = T * Rz * Rx * Ry * S."""
    sx, sy, sz = scale
    S = np.diag([sx, sy, sz, 1.0]).astype(np.float32)

    rx, ry, rz = rotation
    R = rotation_y(ry) @ rotation_x(rx) @ rotation_z(rz)

    T = np.identity(4, dtype=np.float32)
    T[0, 3], T[1, 3], T[2, 3] = position

    return T @ R @ S


class SceneRenderer:
    def __init__(self):
        pygame.init()
        self.display = (WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Cacau e as Pegadas Perdidas")

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glClearColor(0.55, 0.75, 0.95, 1.0)

        self.program = shaders.create_program()
        glUseProgram(self.program)

        # Jogador começa no quintal, olhando para as pegadas (+Z)
        self.camera = camera.Camera(position=(0, 1.6, -9))
        self.camera.yaw = 90.0
        self.camera.pitch = -5.0
        self.camera.update_vectors()

        self.clock = pygame.time.Clock()
        self.running = True

        # Esconde o cursor e captura o mouse para olhar livremente
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.time_sec = 0.0
        self.light_pos = np.array([20.0, 10.0, 0.0], dtype=np.float32)

        self.game_state = "intro"  # intro | playing | found
        self.font = pygame.font.SysFont("dejavusans", 28)
        self.font_large = pygame.font.SysFont("dejavusans", 34, bold=True)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        images = os.path.join(base_dir, "images")

        self.grass_texture = Texture(image_path=os.path.join(images, "grama.png"))
        self.asphalt_texture = Texture(image_path=os.path.join(images, "asfalto.png"))
        self.tree_texture = Texture(image_path=os.path.join(images, "arvore.png"))

        self.cube_mesh = objects.get_cube()
        self.sphere_mesh = objects.get_sphere()
        self.plane_mesh = objects.get_plane()

        self._print_intro()

    def _print_intro(self):
        print("=" * 60)
        print("CACAU E AS PEGADAS PERDIDAS")
        print("=" * 60)
        print("\nCacau desapareceu.")
        print("Vou seguir suas pegadas.\n")
        print("Controles: WASD/Setas — mover | Mouse — olhar | ESC — sair")
        print("=" * 60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                else:
                    self.camera.add_key_pressed(event.key)
                    if self.game_state == "intro":
                        self.game_state = "playing"
            elif event.type == KEYUP:
                self.camera.remove_key_pressed(event.key)
            elif event.type == MOUSEMOTION:
                dx, dy = event.rel
                if dx or dy:
                    self.camera.mouse_look(dx, dy)
                    if self.game_state == "intro":
                        self.game_state = "playing"

    def update(self):
        dt = self.clock.get_time() / 1000.0
        self.time_sec += dt

        if self.game_state != "found":
            self.camera.update()

        # Luz móvel: lightX = 20*cos(t), lightZ = 20*sin(t)
        self.light_pos[0] = 20.0 * math.cos(self.time_sec)
        self.light_pos[2] = 20.0 * math.sin(self.time_sec)
        self.light_pos[1] = 10.0

        if self.game_state == "playing":
            dist = np.linalg.norm(self.camera.position - CACAU_POS)
            if dist < WIN_DISTANCE:
                self.game_state = "found"
                print("\n>>> Você encontrou a Cacau! <<<\n")

    def _get_projection(self):
        aspect = WINDOW_WIDTH / WINDOW_HEIGHT
        f = 1.0 / math.tan(math.radians(45) / 2)
        near, far = 0.1, 200.0
        projection = np.zeros((4, 4), dtype=np.float32)
        projection[0, 0] = f / aspect
        projection[1, 1] = f
        projection[2, 2] = -(far + near) / (far - near)
        projection[2, 3] = -(2 * far * near) / (far - near)
        projection[3, 2] = -1
        return projection

    def render_object(
        self,
        mesh,
        position,
        scale=(1, 1, 1),
        color=(200, 200, 200),
        texture=None,
        use_texture=False,
        rotation=(0, 0, 0),
    ):
        model = make_model_matrix(position, scale, rotation)
        view = self.camera.get_view_matrix()
        projection = self._get_projection()

        glUniformMatrix4fv(glGetUniformLocation(self.program, "model"), 1, GL_TRUE, model)
        glUniformMatrix4fv(glGetUniformLocation(self.program, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(self.program, "projection"), 1, GL_TRUE, projection)

        glUniform3f(
            glGetUniformLocation(self.program, "lightPos"),
            self.light_pos[0], self.light_pos[1], self.light_pos[2],
        )
        glUniform3f(
            glGetUniformLocation(self.program, "viewPos"),
            self.camera.position[0], self.camera.position[1], self.camera.position[2],
        )
        glUniform3f(glGetUniformLocation(self.program, "lightColor"), 1.0, 1.0, 1.0)
        glUniform3f(
            glGetUniformLocation(self.program, "objectColor"),
            color[0] / 255.0, color[1] / 255.0, color[2] / 255.0,
        )
        glUniform1i(glGetUniformLocation(self.program, "useTexture"), 1 if use_texture else 0)

        if texture and use_texture:
            texture.bind()
            glUniform1i(glGetUniformLocation(self.program, "texture1"), 0)

        mesh.render()

    def render_quintal(self):
        """Área 1 — Quintal com grama, casa, pote e pegadas iniciais."""
        # Chão de grama (textura obrigatória)
        self.render_object(
            self.plane_mesh,
            position=(0, 0, -7),
            scale=(0.4, 1, 0.32),
            color=(100, 150, 80),
            texture=self.grass_texture,
            use_texture=True,
        )

        # Casa — cubo grande azul (cor sólida)
        self.render_object(
            self.cube_mesh,
            position=(-6, 1.5, -11),
            scale=(3, 3, 3),
            color=(70, 130, 210),
        )

        # Pote de ração — cubo colorido pequeno
        self.render_object(
            self.cube_mesh,
            position=(-4, 0.15, -8),
            scale=(0.35, 0.3, 0.35),
            color=(220, 80, 60),
        )

        # Portão (marco visual de saída do quintal)
        self.render_object(
            self.cube_mesh,
            position=(3.5, 1.0, -0.5),
            scale=(0.15, 2.0, 2.0),
            color=(120, 80, 40),
        )
        self.render_object(
            self.cube_mesh,
            position=(-3.5, 1.0, -0.5),
            scale=(0.15, 2.0, 2.0),
            color=(120, 80, 40),
        )

    def render_rua(self):
        """Área 2 — Rua reta com asfalto, calçadas, postes e árvores."""
        # Asfalto
        self.render_object(
            self.plane_mesh,
            position=(0, 0.01, 25),
            scale=(0.16, 1, 1.0),
            color=(80, 80, 85),
            texture=self.asphalt_texture,
            use_texture=True,
        )

        # Calçadas laterais
        for side in (-1, 1):
            self.render_object(
                self.plane_mesh,
                position=(side * 4.5, 0.02, 25),
                scale=(0.06, 1, 1.0),
                color=(190, 190, 185),
            )

        # Postes — cubos finos cinza (cor sólida)
        for z in (8, 18, 28, 38):
            self.render_object(
                self.cube_mesh,
                position=(5.5, 2.5, z),
                scale=(0.15, 5.0, 0.15),
                color=(140, 140, 145),
            )
            # Braço do poste
            self.render_object(
                self.cube_mesh,
                position=(5.2, 4.8, z),
                scale=(0.8, 0.12, 0.12),
                color=(130, 130, 135),
            )

        # Árvores simples ao longo da rua
        tree_spots = [(-6, 10), (6, 16), (-6, 24), (6, 32), (-6, 40)]
        for tx, tz in tree_spots:
            self.render_object(
                self.cube_mesh,
                position=(tx, 1.2, tz),
                scale=(0.35, 2.4, 0.35),
                color=(101, 67, 33),
            )
            self.render_object(
                self.cube_mesh,
                position=(tx, 3.2, tz),
                scale=(1.6, 1.6, 1.6),
                color=(34, 120, 45),
            )

    def render_footprints(self):
        """Pegadas como quadrados achatados no chão."""
        for fp_x, fp_y, fp_z in FOOTPRINTS:
            if fp_z < 0:
                continue  # quintal já tem pegadas próximas
            self.render_object(
                self.cube_mesh,
                position=(fp_x, fp_y, fp_z),
                scale=(0.18, 0.02, 0.22),
                color=(50, 45, 40),
            )

    def render_quintal_footprints(self):
        for fp_x, fp_y, fp_z in FOOTPRINTS:
            if fp_z >= 0:
                continue
            self.render_object(
                self.cube_mesh,
                position=(fp_x, fp_y, fp_z),
                scale=(0.18, 0.02, 0.22),
                color=(50, 45, 40),
            )

    def render_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program)

        self.render_quintal()
        self.render_quintal_footprints()
        self.render_rua()
        self.render_footprints()

        # Cacau no final da rua (animação da cauda)
        cat.render_cacau(self, (CACAU_POS[0], CACAU_POS[1], CACAU_POS[2]), self.time_sec)

        # Sol (representação visual da luz)
        self.render_object(
            self.sphere_mesh,
            position=tuple(self.light_pos),
            scale=(0.5, 0.5, 0.5),
            color=(255, 240, 120),
        )

    def render_hud(self):
        """Texto narrativo sobre a cena."""
        screen = pygame.display.get_surface()
        messages = []

        if self.game_state == "intro":
            messages = [
                "Cacau desapareceu.",
                "Vou seguir suas pegadas.",
            ]
        elif self.game_state == "found":
            messages = ["Você encontrou a Cacau!"]
        elif self.game_state == "playing":
            dist = np.linalg.norm(self.camera.position - CACAU_POS)
            if dist < 15:
                messages = ["Estou chegando perto..."]

        y = 16
        for i, msg in enumerate(messages):
            font = self.font_large if (self.game_state == "found" or i == 0 and self.game_state == "intro") else self.font
            shadow = font.render(msg, True, (0, 0, 0))
            text = font.render(msg, True, (255, 255, 255))
            screen.blit(shadow, (22, y + 2))
            screen.blit(text, (20, y))
            y += 42 if font == self.font_large else 34

        hint = self.font.render("WASD: mover | Mouse: olhar | ESC: sair", True, (230, 230, 230))
        screen.blit(hint, (20, WINDOW_HEIGHT - 36))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render_scene()
            self.render_hud()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        pygame.quit()
        sys.exit()


def main():
    try:
        SceneRenderer().run()
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
