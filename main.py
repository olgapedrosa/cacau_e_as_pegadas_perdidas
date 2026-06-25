"""
CACAU E AS PEGADAS PERDIDAS
Passeio Virtual 3D em OpenGL 4.0

Mapa: Quintal amplo (seguir pegadas até encontrar a Cacau)
Controles: WASD/Setas + Mouse | ESC para sair
"""

import os
import math
import sys
import ctypes
import textwrap

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *

import shaders
import camera
import objects
from textures import Texture
import cat

UI_VERTEX_SHADER = """
#version 410

layout (location = 0) in vec2 position;
layout (location = 1) in vec2 texCoord;

out vec2 vTexCoord;

void main()
{
    vTexCoord = texCoord;
    gl_Position = vec4(position, 0.0, 1.0);
}
"""

UI_FRAGMENT_SHADER = """
#version 410

in vec2 vTexCoord;

uniform sampler2D uiTexture;

out vec4 FragColor;

void main()
{
    FragColor = texture(uiTexture, vTexCoord);
}
"""

SKY_VERTEX_SHADER = """
#version 410

layout (location = 0) in vec3 position;
layout (location = 2) in vec2 texCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec2 TexCoord;

void main()
{
    TexCoord = texCoord;
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

SKY_FRAGMENT_SHADER = """
#version 410

in vec2 TexCoord;

uniform sampler2D skyTexture;

out vec4 FragColor;

void main()
{
    FragColor = texture(skyTexture, TexCoord);
}
"""

# Constantes da janela
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Cacau escondida no fundo do quintal, ao fim das pegadas
CACAU_POS = np.array([18.8, 0.0, 10.8], dtype=np.float32)
WIN_DISTANCE = 3.0

# Limites do quintal expandido
YARD_X_MIN, YARD_X_MAX = -20, 20
YARD_Z_MIN, YARD_Z_MAX = -22, 14

# Caminho sinuoso das pegadas pelo quintal (waypoints x, z)
FOOTPRINT_WAYPOINTS = [
    (-6.0, -7.8), (-8.4, -6.1), (-10.0, -3.8), (-11.0, -0.8), (-10.2, 2.2),
    (-8.4, 4.0), (-6.6, 6.2), (-7.8, 8.9), (-10.5, 9.8), (-12.0, 7.2),
    (-11.2, 4.2), (-8.8, 3.1), (-6.1, 3.2), (-4.2, 1.4), (-1.5, -0.2),
    (1.2, -1.2), (4.0, -2.4), (6.8, -2.7), (8.8, -0.8), (10.8, 1.4),
    (12.0, 4.0), (13.0, 6.8), (14.6, 9.2), (16.8, 10.9), (18.8, 10.8),
]

# Vegetação espalhada (x, z)
TREE_SPOTS = [
    (-14, -8), (12, -12), (16, 0), (-15, 4), (8, 12), (0, -14), (-12, -16), (-8, 8), (6, 4),
]
BUSH_SPOTS = [
    (4, -7, 0.42), (-2, 5, 0.58), (9, 5, 0.72), (-9, -3, 0.46), (1, 8, 0.64),
    (11, -5, 0.80), (-13, 0, 0.48), (5, -2, 0.36),
    (17.1, 10.0, 0.78),
]

# Cerca de madeira (postes + barras)
FENCE_COLOR = (160, 100, 50)
FENCE_POST_SCALE = (0.15, 1.5, 0.15)
FENCE_BAR_THICK = 0.1
FENCE_POST_STEP = 2.0


def build_yard_footprints(waypoints, step_dist=2.1, lateral=0.18):
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

        # Jogador começa em frente à porta, já voltado para as pegadas no chão
        self.camera = camera.Camera(position=(-6.0, 1.6, -6.4))
        self.camera.yaw = 90.0
        self.camera.pitch = -10.0
        self.camera.update_vectors()

        self.clock = pygame.time.Clock()
        self.running = True

        self.time_sec = 0.0
        self.light_angle = 0.0
        self.light_orbit_radius = 22.0
        self.light_orbit_height = 13.5
        self.light_pos = np.array([self.light_orbit_radius, self.light_orbit_height, 0.0], dtype=np.float32)

        self.ball_base_pos = np.array([YARD_X_MAX - 12.5, 0.18, YARD_Z_MIN + 5.5], dtype=np.float32)
        self.ball_phase = 0.0

        self.story_overlay_lines = None
        self.story_overlay_until = None
        self.story_seen = set()
        self.conclusion_story_lines = None

        self.game_state = "menu"  # menu | playing | found
        self.intro_visible_until = None
        self.intro_duration_ms = 3200
        self.font = pygame.font.SysFont("dejavusans", 28)
        self.font_large = pygame.font.SysFont("dejavusans", 34, bold=True)
        self.font_title = pygame.font.SysFont("dejavusans", 50, bold=True)
        self.font_story = pygame.font.SysFont("dejavusans", 18)
        self.font_story_title = pygame.font.SysFont("dejavusans", 20, bold=True)
        self.font_menu_title = pygame.font.SysFont("dejavusans", 44, bold=True)
        self.font_menu_text = pygame.font.SysFont("dejavusans", 24)
        self.font_conclusion_title = pygame.font.SysFont("dejavusans", 42, bold=True)
        self.font_conclusion_text = pygame.font.SysFont("dejavusans", 24)

        self.start_button = pygame.Rect(0, 0, 280, 62)
        self.exit_button = pygame.Rect(0, 0, 220, 56)
        self.conclusion_exit_button = pygame.Rect(0, 0, 220, 56)
        self._layout_ui()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        images = os.path.join(base_dir, "images")

        self.grass_texture = Texture(image_path=os.path.join(images, "grama.png"))
        self.sky_texture = Texture(image_path=os.path.join(images, "ceu.png"))
        self.food_texture = Texture(image_path=os.path.join(images, "racao.png"))
        self.footprint_texture = Texture(
            image_path=os.path.join(images, "pegada.png"),
            transparent_black=True,
        )
        self.wall_texture = Texture(image_path=os.path.join(images, "parede.png"))
        self.cat_texture = Texture(image_path=os.path.join(images, "gato.png"))

        # Permitir repetição para a textura do muro
        try:
            glBindTexture(GL_TEXTURE_2D, self.wall_texture.texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glBindTexture(GL_TEXTURE_2D, 0)
        except Exception:
            pass

        self.cube_mesh = objects.get_cube()
        self.sphere_mesh = objects.get_sphere()
        self.plane_mesh = objects.get_plane()
        self.footprint_mesh = objects.get_footprint_quad()
        self.food_top_mesh = objects.create_footprint_quad(width=0.55, depth=0.55)

        self.sky_program = self._create_sky_program()

        self.ui_program = self._create_ui_program()
        self.ui_texture = glGenTextures(1)
        self.ui_vao = glGenVertexArrays(1)
        self.ui_vbo = glGenBuffers(1)
        self._setup_ui_quad()

        self._sync_input_mode()
        self._print_intro()

    def _print_intro(self):
        print("=" * 60)
        print("CACAU E AS PEGADAS PERDIDAS")
        print("=" * 60)
        print("\nMenu inicial com botão de começar e sair.")
        print("Ao iniciar, a tela mostra a narrativa sobreposta e translúcida.")
        print("Ao encontrar a Cacau, aparece a tela de conclusão com botão de sair.\n")
        print("Controles: WASD/Setas — mover | Mouse — olhar | ESC — sair")
        print("=" * 60)

    def _layout_ui(self):
        self.start_button.center = (WINDOW_WIDTH // 2, 470)
        self.exit_button.center = (WINDOW_WIDTH // 2, 550)
        self.conclusion_exit_button.center = (WINDOW_WIDTH // 2, 560)

    def _sync_input_mode(self):
        interactive = self.game_state == "playing"
        pygame.mouse.set_visible(not interactive)
        pygame.event.set_grab(interactive)

    def _set_state(self, state):
        self.game_state = state
        self._sync_input_mode()

    def _start_game(self):
        self.intro_visible_until = pygame.time.get_ticks() + self.intro_duration_ms
        self._show_story(
            "Cacau desapareceu esta manhã. Ela costuma explorar o quintal, mas nunca fica longe por muito tempo. Talvez eu consiga encontrá-la seguindo seus rastros.",
            duration_ms=6500,
        )
        self._set_state("playing")

    def _show_story(self, text, duration_ms=6000):
        self.story_overlay_lines = textwrap.wrap(text, width=72)
        self.story_overlay_until = pygame.time.get_ticks() + duration_ms

    def _draw_story_overlay(self, screen):
        panel = pygame.Rect(0, 0, 900, 110)
        panel.midtop = (WINDOW_WIDTH // 2, 18)
        self._draw_panel(screen, panel, fill=(12, 16, 24), alpha=165, border=(120, 160, 210))

        y = panel.top + 22
        for i, line in enumerate(self.story_overlay_lines or []):
            font = self.font_story_title if i == 0 else self.font_story
            color = (255, 248, 230) if i == 0 else (232, 238, 245)
            rendered = font.render(line, True, color)
            rect = rendered.get_rect(center=(WINDOW_WIDTH // 2, y))
            screen.blit(rendered, rect)
            y += 28 if i == 0 else 24

    def _check_story_triggers(self):
        if self.game_state != "playing":
            return

        if "tree_favorite" not in self.story_seen:
            tree_pos = np.array([-8.0, 0.0, 8.0], dtype=np.float32)
            if np.linalg.norm(self.camera.position - tree_pos) < 4.5:
                self.story_seen.add("tree_favorite")
                self._show_story(
                    "Essa é a árvore favorita da Cacau. Ela adorava subir nos galhos e ficar observando tudo lá de cima. Talvez tenha passado por aqui.",
                    duration_ms=6000,
                )
                return

        if "food_bowl" not in self.story_seen:
            bowl_pos = np.array([2.5, 0.15, -5.5], dtype=np.float32)
            if np.linalg.norm(self.camera.position - bowl_pos) < 3.0:
                self.story_seen.add("food_bowl")
                self._show_story(
                    "O pote vermelho ainda está cheio. Isso é estranho... Cacau nunca deixava a hora da comida passar sem aparecer.",
                    duration_ms=6000,
                )
                return

        if "ball" not in self.story_seen:
            ball_x = self.ball_base_pos[0] + math.sin(self.ball_phase) * 0.7
            ball_pos = np.array([ball_x, self.ball_base_pos[1], self.ball_base_pos[2]], dtype=np.float32)
            if np.linalg.norm(self.camera.position - ball_pos) < 2.5:
                self.story_seen.add("ball")
                self._show_story(
                    "A bolinha dela está aqui. Quantas vezes eu a vi correr pelo quintal atrás desse brinquedo.",
                    duration_ms=6000,
                )
                return

        if "cat" not in self.story_seen:
            if np.linalg.norm(self.camera.position - CACAU_POS) < WIN_DISTANCE:
                self.story_seen.add("cat")
                self.conclusion_story_lines = textwrap.wrap("Cacau! Finalmente te encontrei. Vamos para casa.", width=72)
                self._set_state("found")
                print("\n>>> Você encontrou a Cacau! <<<\n")

    def _draw_text_center(self, surface, text, center_x, center_y, font, color):
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(center_x, center_y))
        surface.blit(rendered, rect)

    def _draw_button(self, surface, rect, label, hovered=False, base_color=(34, 45, 62)):
        fill_color = (58, 84, 126) if hovered else base_color
        shadow = rect.move(0, 4)
        pygame.draw.rect(surface, (0, 0, 0, 110), shadow, border_radius=16)
        pygame.draw.rect(surface, fill_color, rect, border_radius=16)
        pygame.draw.rect(surface, (162, 200, 255), rect, width=2, border_radius=16)
        self._draw_text_center(surface, label, rect.centerx, rect.centery, self.font_large, (255, 255, 255))

    def _draw_panel(self, surface, rect, fill=(18, 24, 34), alpha=220, border=(126, 182, 255)):
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((*fill, alpha))
        surface.blit(panel, rect.topleft)
        pygame.draw.rect(surface, border, rect, width=2, border_radius=24)

    def _create_ui_program(self):
        vertex = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex, UI_VERTEX_SHADER)
        glCompileShader(vertex)

        fragment = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment, UI_FRAGMENT_SHADER)
        glCompileShader(fragment)

        program = glCreateProgram()
        glAttachShader(program, vertex)
        glAttachShader(program, fragment)
        glLinkProgram(program)
        return program

    def _create_sky_program(self):
        vertex = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex, SKY_VERTEX_SHADER)
        glCompileShader(vertex)

        fragment = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment, SKY_FRAGMENT_SHADER)
        glCompileShader(fragment)

        program = glCreateProgram()
        glAttachShader(program, vertex)
        glAttachShader(program, fragment)
        glLinkProgram(program)
        return program

    def _setup_ui_quad(self):
        quad_vertices = np.array([
            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 1.0,
        ], dtype=np.float32)

        glBindVertexArray(self.ui_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.ui_vbo)
        glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        glBindTexture(GL_TEXTURE_2D, self.ui_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_2D, 0)

    def _handle_button_click(self, pos):
        if self.game_state == "menu":
            if self.start_button.collidepoint(pos):
                self._start_game()
            elif self.exit_button.collidepoint(pos):
                self.running = False
        elif self.game_state == "found" and self.conclusion_exit_button.collidepoint(pos):
            self.running = False

    def _present_ui_surface(self, surface):
        ui_pixels = pygame.image.tostring(surface, "RGBA", True)
        glDisable(GL_DEPTH_TEST)
        glUseProgram(self.ui_program)
        glBindVertexArray(self.ui_vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.ui_texture)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            surface.get_width(),
            surface.get_height(),
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            ui_pixels,
        )
        glUniform1i(glGetUniformLocation(self.ui_program, "uiTexture"), 0)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glEnable(GL_DEPTH_TEST)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.game_state == "playing":
                        self.running = False
                    else:
                        self.running = False
                elif self.game_state == "menu" and event.key in (K_RETURN, K_SPACE):
                    self._start_game()
                else:
                    if self.game_state == "playing":
                        self.camera.add_key_pressed(event.key)
            elif event.type == KEYUP:
                if self.game_state == "playing":
                    self.camera.remove_key_pressed(event.key)
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                self._handle_button_click(event.pos)
            elif event.type == MOUSEMOTION:
                dx, dy = event.rel
                if (dx or dy) and self.game_state == "playing":
                    self.camera.mouse_look(dx, dy)

    def update(self):
        dt = self.clock.get_time() / 1000.0
        self.time_sec += dt

        # Movimento lento do sol em órbita
        self.light_angle += dt * 0.28
        self.light_pos[0] = self.light_orbit_radius * math.cos(self.light_angle)
        self.light_pos[2] = self.light_orbit_radius * math.sin(self.light_angle)
        self.light_pos[1] = self.light_orbit_height

        # Pequena oscilação lateral da bolinha no quintal
        self.ball_phase += dt * 0.8

        if self.game_state == "playing":
            self.camera.update()
            self._check_story_triggers()

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
        texture_scale=(1.0, 1.0),
        rotation=(0, 0, 0),
        brightness_boost=1.0,
        double_sided=False,
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
        glUniform1f(glGetUniformLocation(self.program, "brightnessBoost"), float(brightness_boost))

        # Texture scale / tiling (default 1,1)
        tex_scale_loc = glGetUniformLocation(self.program, "texScale")
        if texture and use_texture:
            texture.bind()
            glUniform1i(glGetUniformLocation(self.program, "texture1"), 0)
            if tex_scale_loc != -1:
                glUniform2f(tex_scale_loc, float(texture_scale[0]), float(texture_scale[1]))
        else:
            if tex_scale_loc != -1:
                glUniform2f(tex_scale_loc, 1.0, 1.0)

        culling_was_enabled = False
        if double_sided:
            culling_was_enabled = glIsEnabled(GL_CULL_FACE)
            if culling_was_enabled:
                glDisable(GL_CULL_FACE)

        mesh.render()

        if double_sided and culling_was_enabled:
            glEnable(GL_CULL_FACE)

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

    def _render_wall_along_x(self, z, x_start, x_end):
        """Renderiza um trecho contínuo de muro paralelo ao eixo X usando textura."""
        # Garante que o comprimento seja sempre positivo para não quebrar a escala nem o UV
        span = abs(x_end - x_start)
        mid_x = (x_start + x_end) / 2
        
        wall_height = FENCE_POST_SCALE[1]
        wall_thickness = 0.18
        
        # O cálculo do tiling (repetição) também precisa ser estritamente positivo
        tex_u = max(1.0, span)
        tex_v = max(1.0, wall_height)
        
        self.render_object(
            self.cube_mesh,
            position=(mid_x, 1.0, z),
            scale=(span, wall_height, wall_thickness), # Agora garante valor positivo
            color=(255, 255, 255),                     # <--- Mudei para 255 para tirar o tom cinza e clarear o tijolo!
            texture=self.wall_texture,
            use_texture=True,
            texture_scale=(tex_u, tex_v),
        )

    def _render_wall_along_z(self, x, z_start, z_end):
        """Renderiza o muro do eixo Z rotacionando um muro do eixo X em 90 graus."""
        span = abs(z_end - z_start)
        mid_z = (z_start + z_end) / 2
        
        wall_height = FENCE_POST_SCALE[1]
        wall_thickness = 0.18
        
        # Usamos os mesmos cálculos de repetição do eixo X
        tex_u = max(1.0, span)
        tex_v = max(1.0, wall_height)
        
        self.render_object(
            self.cube_mesh,
            position=(x, 1.0, mid_z),
            # Invertemos os parâmetros de escala: passamos o 'span' no X do cubo,
            # porque a rotação vai se encargar de girar esse X para a direção Z!
            scale=(span, wall_height, wall_thickness), 
            color=(255, 255, 255),
            texture=self.wall_texture,
            use_texture=True,
            texture_scale=(tex_u, tex_v),
            rotation=(0, 90, 0) # <--- GIRA 90 GRAUS NO EIXO Y
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
        # Substitui a cerca por muros texturizados usando a imagem parede.png
        self._render_wall_along_x(YARD_Z_MIN, YARD_X_MIN, YARD_X_MAX)
        self._render_wall_along_x(YARD_Z_MAX, YARD_X_MIN, YARD_X_MAX)
        self._render_wall_along_z(YARD_X_MIN, YARD_Z_MIN, YARD_Z_MAX)
        self._render_wall_along_z(YARD_X_MAX, YARD_Z_MIN, YARD_Z_MAX)

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
            scale=(0.25, 0.1, 0.25),
            color=(220, 80, 60),
            double_sided=True,
        )
        self.render_object(
            self.food_top_mesh,
            position=(2.5, 0.255, -5.5),
            scale=(0.70, 0.70, 0.70),
            color=(255, 255, 255),
            texture=self.food_texture,
            use_texture=True,
            brightness_boost=1.15,
            double_sided=True,
        )

        for tx, tz in TREE_SPOTS:
            self._render_tree(tx, tz)

        for bush in BUSH_SPOTS:
            if len(bush) == 3:
                bx, bz, size = bush
            else:
                bx, bz = bush
                size = 0.55
            self._render_bush(bx, bz, size=size)

        ball_x = self.ball_base_pos[0] + math.sin(self.ball_phase) * 0.7
        self.render_object(
            self.sphere_mesh,
            position=(ball_x, self.ball_base_pos[1], self.ball_base_pos[2]),
            scale=(0.18, 0.18, 0.18),
            color=(111, 80, 222),
        )

        self.render_fence()

    def render_sky(self):
        """Fundo estático em tela cheia, sem depender da câmera."""
        glDisable(GL_DEPTH_TEST)
        glUseProgram(self.ui_program)
        glBindVertexArray(self.ui_vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.sky_texture.texture_id)
        glUniform1i(glGetUniformLocation(self.ui_program, "uiTexture"), 0)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glEnable(GL_DEPTH_TEST)
        glUseProgram(self.program)

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

        self.render_sky()
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
        """Desenha menus e textos sobre a cena 3D."""
        screen = pygame.Surface(self.display, pygame.SRCALPHA)
        if self.game_state == "menu":
            self._draw_menu(screen)
        elif self.game_state == "found":
            self._draw_conclusion(screen)
        else:
            self._draw_game_hud(screen)
            now = pygame.time.get_ticks()
            story_visible = self.story_overlay_lines is not None and self.story_overlay_until is not None and now < self.story_overlay_until
            intro_visible = self.intro_visible_until is not None and now < self.intro_visible_until

            if story_visible:
                self._draw_story_overlay(screen)
            elif intro_visible:
                self._draw_intro(screen)
            elif self.intro_visible_until is not None and now >= self.intro_visible_until:
                self.intro_visible_until = None

            if self.story_overlay_until is not None and now >= self.story_overlay_until:
                self.story_overlay_lines = None
                self.story_overlay_until = None

        self._present_ui_surface(screen)

    def _draw_game_hud(self, screen):
        hint = self.font.render("WASD: mover | Mouse: olhar | ESC: sair", True, (230, 230, 230))
        screen.blit(hint, (20, WINDOW_HEIGHT - 36))

    def _draw_menu(self, screen):
        overlay = pygame.Surface(self.display, pygame.SRCALPHA)
        overlay.fill((7, 12, 18, 240))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 820, 360)
        panel.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self._draw_panel(screen, panel, fill=(15, 22, 32), alpha=230)

        title = self.font_menu_title.render("Cacau e as Pegadas Perdidas", True, (255, 243, 210))
        title_shadow = self.font_menu_title.render("Cacau e as Pegadas Perdidas", True, (0, 0, 0))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, panel.top + 80))
        screen.blit(title_shadow, title_rect.move(3, 3))
        screen.blit(title, title_rect)

        instruction = self.font_menu_text.render("Siga as pegadas para encontrar a Cacau.", True, (235, 240, 248))
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, panel.top + 165))
        screen.blit(instruction, instruction_rect)

        controls = self.font_menu_text.render("Controles: WASD/Setas — mover | Mouse — olhar | ESC — sair", True, (225, 235, 245))
        controls_rect = controls.get_rect(center=(WINDOW_WIDTH // 2, panel.top + 215))
        screen.blit(controls, controls_rect)

        self.start_button.center = (WINDOW_WIDTH // 2, panel.bottom - 52)
        self._draw_button(screen, self.start_button, "Começar", self.start_button.collidepoint(pygame.mouse.get_pos()), base_color=(42, 142, 80))

    def _draw_intro(self, screen):
        overlay = pygame.Surface(self.display, pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 160))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 820, 280)
        panel.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self._draw_panel(screen, panel, fill=(20, 26, 38), alpha=190)

        lines = self.story_overlay_lines or ["Cacau desapareceu.", "Vou seguir suas pegadas."]
        y = panel.top + 74
        for i, line in enumerate(lines):
            font = self.font_large if i == 0 else self.font_story
            color = (255, 248, 230) if i == 0 else (225, 232, 240)
            rendered = font.render(line, True, color)
            rect = rendered.get_rect(center=(WINDOW_WIDTH // 2, y))
            screen.blit(rendered, rect)
            y += 42 if i == 0 else 28

        self._draw_text_center(screen, "Controles: WASD/Setas — mover | Mouse — olhar | ESC — sair", WINDOW_WIDTH // 2, panel.bottom - 34, self.font, (225, 232, 240))

    def _draw_conclusion(self, screen):
        overlay = pygame.Surface(self.display, pygame.SRCALPHA)
        overlay.fill((5, 8, 12, 220))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 720, 280)
        panel.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self._draw_panel(screen, panel, fill=(16, 22, 30), alpha=235, border=(112, 210, 160))

        self._draw_text_center(screen, "Você encontrou a Cacau!", WINDOW_WIDTH // 2, panel.top + 82, self.font_conclusion_title, (245, 250, 247))
        if self.conclusion_story_lines:
            y = panel.top + 140
            for line in self.conclusion_story_lines:
                text = self.font_conclusion_text.render(line, True, (220, 232, 226))
                rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
                screen.blit(text, rect)
                y += 28
        else:
            self._draw_text_center(screen, "Fim da busca. Obrigado por jogar.", WINDOW_WIDTH // 2, panel.top + 142, self.font_conclusion_text, (220, 232, 226))

        self.conclusion_exit_button.center = (WINDOW_WIDTH // 2, panel.bottom - 64)
        self._draw_button(screen, self.conclusion_exit_button, "Sair", self.conclusion_exit_button.collidepoint(pygame.mouse.get_pos()), base_color=(150, 60, 60))

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
