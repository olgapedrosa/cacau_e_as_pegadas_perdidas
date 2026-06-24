"""
CACAU E AS PEGADAS PERDIDAS
Passeio Virtual 3D em OpenGL 4.0

Mapa: Quintal amplo (seguir pegadas até encontrar a Cacau)
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

# Cacau escondida no fundo do quintal, ao fim das pegadas
CACAU_POS = np.array([13.0, 0.0, 9.0], dtype=np.float32)
WIN_DISTANCE = 3.0

# Limites do quintal expandido
YARD_X_MIN, YARD_X_MAX = -20, 20
YARD_Z_MIN, YARD_Z_MAX = -22, 14

# Caminho sinuoso das pegadas pelo quintal (waypoints x, z)
FOOTPRINT_WAYPOINTS = [
    (0, -6), (3, -4), (7, -2), (9, 2), (7, 7), (3, 10),
    (-2, 12), (-7, 10), (-11, 6), (-10, 0), (-6, -5),
    (-1, -9), (4, -11), (10, -8), (14, -3), (15, 3), (13, 9),
]

# Vegetação espalhada (x, z)
TREE_SPOTS = [
    (-14, -8), (12, -12), (16, 0), (-15, 4), (8, 12),
    (-10, 14), (0, -14), (-12, -16), (-8, 8), (6, 4),
]
BUSH_SPOTS = [
    (4, -7), (-2, 5), (9, 5), (-9, -3), (1, 8),
    (-5, -12), (11, -5), (-13, 0), (5, -2), (-3, -8),
]

# Cerca de madeira (postes + barras)
FENCE_COLOR = (160, 100, 50)
FENCE_POST_SCALE = (0.15, 1.5, 0.15)
FENCE_BAR_THICK = 0.1
FENCE_POST_STEP = 2.0


def build_yard_footprints(waypoints, step_dist=0.65, lateral=0.16):
    """Gera pares de pegadas ao longo de waypoints com curvas e mudanças de direção."""
    footprints = []
    for i in range(len(waypoints) - 1):
        x0, z0 = waypoints[i]
        x1, z1 = waypoints[i + 1]
        dx, dz = x1 - x0, z1 - z0
        length = math.hypot(dx, dz)
        if length < 1e-6:
            continue

        steps = max(1, int(length / step_dist))
        heading = math.degrees(math.atan2(dx, dz))
        perp_x, perp_z = -dz / length, dx / length

        for s in range(steps):
            t = (s + 0.5) / steps
            x = x0 + dx * t
            z = z0 + dz * t
            forward = 0.18
            footprints.append((x + perp_x * lateral, 0.04, z + perp_z * lateral, heading))
            footprints.append((
                x - perp_x * lateral,
                0.04,
                z - perp_z * lateral + forward,
                heading,
            ))
    return footprints


FOOTPRINTS = build_yard_footprints(FOOTPRINT_WAYPOINTS)


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
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.55, 0.75, 0.95, 1.0)

        self.program = shaders.create_program()
        glUseProgram(self.program)

        # Jogador começa no quintal, olhando para as pegadas
        self.camera = camera.Camera(position=(0, 1.6, -8))
        self.camera.yaw = 75.0
        self.camera.pitch = -8.0
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
        self.footprint_texture = Texture(
            image_path=os.path.join(images, "pegada.png"),
            transparent_black=True,
        )

        self.cube_mesh = objects.get_cube()
        self.sphere_mesh = objects.get_sphere()
        self.plane_mesh = objects.get_plane()
        self.footprint_mesh = objects.get_footprint_quad()

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

    def _render_fence_post(self, x, y, z):
        self.render_object(
            self.cube_mesh,
            position=(x, y, z),
            scale=FENCE_POST_SCALE,
            color=FENCE_COLOR,
        )

    def _render_fence_bars_along_x(self, z, x0, x1):
        """Barras horizontais entre dois postes alinhados em X."""
        span = x1 - x0
        mid_x = (x0 + x1) / 2
        self.render_object(
            self.cube_mesh,
            position=(mid_x, 1.8, z),
            scale=(span, FENCE_BAR_THICK, 0.15),
            color=FENCE_COLOR,
        )
        self.render_object(
            self.cube_mesh,
            position=(mid_x, 0.5, z),
            scale=(span, FENCE_BAR_THICK, 0.15),
            color=FENCE_COLOR,
        )

    def _render_fence_bars_along_z(self, x, z0, z1):
        """Barras horizontais entre dois postes alinhados em Z."""
        span = z1 - z0
        mid_z = (z0 + z1) / 2
        self.render_object(
            self.cube_mesh,
            position=(x, 1.8, mid_z),
            scale=(0.15, FENCE_BAR_THICK, span),
            color=FENCE_COLOR,
        )
        self.render_object(
            self.cube_mesh,
            position=(x, 0.5, mid_z),
            scale=(0.15, FENCE_BAR_THICK, span),
            color=FENCE_COLOR,
        )

    def _render_fence_along_x(self, z, x_start, x_end, step=FENCE_POST_STEP):
        """Trecho de cerca paralelo ao eixo X (postes + barras)."""
        posts = list(np.arange(x_start, x_end + 0.01, step))
        if not posts or posts[-1] < x_end - 0.25:
            posts.append(x_end)

        for fence_x in posts:
            self._render_fence_post(fence_x, 1.0, z)

        for i in range(len(posts) - 1):
            self._render_fence_bars_along_x(z, posts[i], posts[i + 1])

    def _render_fence_along_z(self, x, z_start, z_end, step=FENCE_POST_STEP):
        """Trecho de cerca paralelo ao eixo Z (postes + barras)."""
        posts = list(np.arange(z_start, z_end + 0.01, step))
        if not posts or posts[-1] < z_end - 0.25:
            posts.append(z_end)

        for fence_z in posts:
            self._render_fence_post(x, 1.0, fence_z)

        for i in range(len(posts) - 1):
            self._render_fence_bars_along_z(x, posts[i], posts[i + 1])

    def _render_tree(self, x, z, trunk_h=2.4, crown_size=1.6):
        """Árvore simples: tronco + copa."""
        self.render_object(
            self.cube_mesh,
            position=(x, trunk_h / 2, z),
            scale=(0.35, trunk_h, 0.35),
            color=(101, 67, 33),
        )
        self.render_object(
            self.cube_mesh,
            position=(x, trunk_h + crown_size / 2 - 0.2, z),
            scale=(crown_size, crown_size, crown_size),
            color=(34, 120, 45),
        )

    def _render_bush(self, x, z, size=0.55):
        """Arbusto baixo e arredondado."""
        self.render_object(
            self.sphere_mesh,
            position=(x, size * 0.45, z),
            scale=(size, size * 0.7, size),
            color=(45, 135, 55),
        )

    def render_fence(self):
        """Cerca em torno do quintal expandido e contorno parcial da casa."""
        self._render_fence_along_x(YARD_Z_MIN, YARD_X_MIN, YARD_X_MAX)
        self._render_fence_along_x(YARD_Z_MAX, YARD_X_MIN, YARD_X_MAX)
        self._render_fence_along_z(YARD_X_MIN, YARD_Z_MIN, YARD_Z_MAX)
        self._render_fence_along_z(YARD_X_MAX, YARD_Z_MIN, YARD_Z_MAX)

        # Cerca ao redor da casa (aberta para o quintal ao sul)
        self._render_fence_along_x(-14.2, -9.5, -2.8)
        self._render_fence_along_z(-9.5, -14.2, -8.5)

    def render_house(self):
        """Casa azul com porta na fachada (+Z) e janela na parede lateral (+X)."""
        house_pos = (-6, 1.5, -11)
        house_scale = (3, 3, 3)
        # Cubo unitário vai de -1 a 1: face +Z fica em center + scale (não scale/2)
        facade_z = house_pos[2] + house_scale[2]
        detail_z = facade_z + 0.1
        side_x = house_pos[0] + house_scale[0] + 0.1

        self.render_object(
            self.cube_mesh,
            position=house_pos,
            scale=house_scale,
            color=(70, 130, 210),
        )

        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(-1.0, -1.0)

        # Porta (marrom, centrada na fachada)
        self.render_object(
            self.cube_mesh,
            position=(house_pos[0], 0.75, detail_z),
            scale=(0.85, 1.5, 0.08),
            color=(95, 55, 25),
        )
        # Maçaneta
        self.render_object(
            self.cube_mesh,
            position=(house_pos[0] + 0.28, 0.75, detail_z + 0.06),
            scale=(0.08, 0.08, 0.06),
            color=(200, 180, 60),
        )

        # Janela na parede lateral direita (+X), centrada ao longo do eixo Z
        window_z = house_pos[2] + 0.8
        self.render_object(
            self.cube_mesh,
            position=(side_x, 2.1, window_z),
            scale=(0.08, 1.0, 1.0),
            color=(45, 45, 50),
        )
        self.render_object(
            self.cube_mesh,
            position=(side_x + 0.05, 2.1, window_z),
            scale=(0.04, 0.82, 0.82),
            color=(160, 210, 240),
        )

        glDisable(GL_POLYGON_OFFSET_FILL)

    def render_quintal(self):
        """Quintal amplo com grama, casa, vegetação e cerca."""
        # Chão de grama expandido
        self.render_object(
            self.plane_mesh,
            position=(0, 0, -2),
            scale=(0.9, 1, 1.5),
            color=(100, 150, 80),
            texture=self.grass_texture,
            use_texture=True,
        )

        self.render_house()

        # Pote de ração perto da casa
        self.render_object(
            self.cube_mesh,
            position=(2.5, 0.15, -5.5),
            scale=(0.35, 0.3, 0.35),
            color=(220, 80, 60),
        )

        for tx, tz in TREE_SPOTS:
            self._render_tree(tx, tz)

        for bx, bz in BUSH_SPOTS:
            self._render_bush(bx, bz)

        self.render_fence()

    def _draw_footprint(self, fp_x, fp_y, fp_z, heading=0.0, flip_x=False):
        """Pegada no chão com rotação conforme a direção do caminho."""
        scale_x = -1.0 if flip_x else 1.0
        glDisable(GL_CULL_FACE)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(-2.0, -2.0)

        self.render_object(
            self.footprint_mesh,
            position=(fp_x, fp_y, fp_z),
            scale=(scale_x, 1.0, 1.0),
            color=(255, 255, 255),
            texture=self.footprint_texture,
            use_texture=True,
            rotation=(0, heading, 0),
        )

        glDisable(GL_POLYGON_OFFSET_FILL)
        glEnable(GL_CULL_FACE)

    def render_footprints(self):
        """Pegadas sinuosas espalhadas pelo quintal."""
        for i, fp in enumerate(FOOTPRINTS):
            fp_x, fp_y, fp_z, heading = fp
            self._draw_footprint(fp_x, fp_y, fp_z, heading=heading, flip_x=(i % 2 == 1))

    def render_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program)

        self.render_quintal()
        self.render_footprints()

        # Cacau escondida no fim do caminho de pegadas
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
