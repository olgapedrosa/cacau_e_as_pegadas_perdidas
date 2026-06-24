"""
CACAU E AS PEGADAS PERDIDAS
Passeio Virtual 3D em OpenGL 4.0

Requisitos implementados:
- Câmera em primeira pessoa com controles WASD/Mouse
- Iluminação Phong com fonte de luz móvel
- Objetos com transformações geométricas e animações
- Texturas (grama, céu, árvores, brinquedo)
- Objetos com cores sólidas
- Interação via teclado e mouse

Controles:
- W/A/S/D: Mover câmera
- Setas: Mover câmera
- Mouse: Olhar ao redor
- ESC: Sair
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import sys

# Imports dos módulos
import shaders
import camera
import objects
from textures import Texture, create_grass_texture, create_wood_texture, create_sky_texture

# Constantes
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

class SceneRenderer:
    def __init__(self):
        """Inicializa o renderizador da cena"""
        pygame.init()
        self.display = (WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Cacau e as Pegadas Perdidas - Passeio Virtual 3D")
        
        # Configurar OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glClearColor(0.5, 0.7, 1.0, 1.0)  # Céu azul
        
        # Criar programa de shader
        self.program = shaders.create_program()
        glUseProgram(self.program)
        
        # Câmera
        self.camera = camera.Camera(position=(5, 2, 10))
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Estado do mouse
        self.mouse_locked = False
        self.last_mouse_pos = pygame.mouse.get_pos()
        
        # Texturas
        self.create_textures()
        
        # Objetos
        self.cube_mesh = objects.get_cube()
        self.sphere_mesh = objects.get_sphere()
        self.cylinder_mesh = objects.get_cylinder()
        self.plane_mesh = objects.get_plane()
        
        # Ângulo de animação para luz e objetos
        self.animation_angle = 0.0
        
        # Posição da fonte de luz
        self.light_pos = np.array([5, 4, 0], dtype=np.float32)
        
        print("=" * 60)
        print("CACAU E AS PEGADAS PERDIDAS - PASSEIO VIRTUAL 3D")
        print("=" * 60)
        print("\nControles:")
        print("  W/A/S/D      - Mover câmera")
        print("  Setas        - Mover câmera (alternativo)")
        print("  Mouse        - Olhar ao redor")
        print("  ESC          - Sair")
        print("\nHistória:")
        print("  Minha gata Cacau desapareceu esta manhã...")
        print("  Vou seguir suas pegadas pelo quintal.")
        print("=" * 60 + "\n")
    
    def create_textures(self):
        """Cria as texturas procedurais"""
        # Grama
        grass_data = create_grass_texture()
        self.grass_texture = Texture(color=(100, 150, 80))
        
        # Céu
        sky_data = create_sky_texture()
        self.sky_texture = Texture(color=(135, 206, 235))
        
        # Madeira
        wood_data = create_wood_texture()
        self.wood_texture = Texture(color=(139, 90, 43))
        
        # Cor de teste
        self.red_texture = Texture(color=(200, 50, 50))
        self.beige_texture = Texture(color=(200, 180, 140))
        self.dark_gray_texture = Texture(color=(60, 60, 60))
    
    def handle_events(self):
        """Processa eventos do pygame"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                else:
                    # Adicionar tecla pressionada
                    self.camera.add_key_pressed(event.key)
            
            elif event.type == KEYUP:
                # Remover tecla solta
                self.camera.remove_key_pressed(event.key)
            
            elif event.type == MOUSEMOTION:
                # Controle de mouse para câmera
                x, y = event.pos
                dx = x - self.last_mouse_pos[0]
                dy = y - self.last_mouse_pos[1]
                
                self.camera.mouse_look(dx, dy)
                self.last_mouse_pos = (x, y)
    
    def update(self):
        """Atualiza a lógica do jogo"""
        self.camera.update()
        
        # Animar luz
        self.animation_angle += 0.005
        self.light_pos[0] = 5 + 3 * math.cos(self.animation_angle)
        self.light_pos[2] = 3 * math.sin(self.animation_angle)
        self.light_pos[1] = 4 + math.sin(self.animation_angle * 2) * 0.5
    
    def render_matrix(self, matrix, model, view, projection):
        """Define as matrizes no shader"""
        model_loc = glGetUniformLocation(self.program, "model")
        view_loc = glGetUniformLocation(self.program, "view")
        proj_loc = glGetUniformLocation(self.program, "projection")
        
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, model)
        glUniformMatrix4fv(view_loc, 1, GL_TRUE, view)
        glUniformMatrix4fv(proj_loc, 1, GL_TRUE, projection)
    
    def render_object(self, mesh, position, scale, color, texture=None, use_texture=False):
        """Renderiza um objeto"""
        # Matriz model
        model = np.identity(4, dtype=np.float32)
        model[0, 3] = position[0]
        model[1, 3] = position[1]
        model[2, 3] = position[2]
        
        # Escala
        model[0, 0] = scale[0]
        model[1, 1] = scale[1]
        model[2, 2] = scale[2]
        
        # Matriz view
        view = self.camera.get_view_matrix()
        
        # Matriz projection
        projection = np.identity(4, dtype=np.float32)
        aspect = WINDOW_WIDTH / WINDOW_HEIGHT
        f = 1.0 / math.tan(math.radians(45) / 2)
        near, far = 0.1, 100.0
        projection[0, 0] = f / aspect
        projection[1, 1] = f
        projection[2, 2] = -(far + near) / (far - near)
        projection[2, 3] = -(2 * far * near) / (far - near)
        projection[3, 2] = -1
        projection[3, 3] = 0
        
        # Enviar matrizes
        self.render_matrix(None, model, view, projection)
        
        # Configurar iluminação
        light_color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        light_pos_loc = glGetUniformLocation(self.program, "lightPos")
        view_pos_loc = glGetUniformLocation(self.program, "viewPos")
        light_color_loc = glGetUniformLocation(self.program, "lightColor")
        
        glUniform3f(light_pos_loc, self.light_pos[0], self.light_pos[1], self.light_pos[2])
        glUniform3f(view_pos_loc, self.camera.position[0], self.camera.position[1], self.camera.position[2])
        glUniform3f(light_color_loc, light_color[0], light_color[1], light_color[2])
        
        # Cor
        color_loc = glGetUniformLocation(self.program, "objectColor")
        glUniform3f(color_loc, color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
        
        # Textura
        use_texture_loc = glGetUniformLocation(self.program, "useTexture")
        glUniform1i(use_texture_loc, 1 if use_texture else 0)
        
        if texture:
            texture.bind()
            glUniform1i(glGetUniformLocation(self.program, "texture1"), 0)
        
        # Renderizar
        mesh.render()
    
    def render_scene(self):
        """Renderiza a cena completa"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # CHÃO (Grama texturizada)
        self.render_object(
            self.plane_mesh,
            position=(0, 0, 0),
            scale=(1, 1, 1),
            color=(100, 150, 80),
            texture=self.grass_texture,
            use_texture=True
        )
        
        # CASA (cubo grande com telhado)
        # Paredes
        self.render_object(
            self.cube_mesh,
            position=(0, 1.5, -5),
            scale=(2, 1.5, 2),
            color=(200, 180, 140),  # Bege
            texture=self.beige_texture,
            use_texture=True
        )
        
        # Telhado (prisma triangular = dois cubos inclinados)
        self.render_object(
            self.cube_mesh,
            position=(0, 3, -5),
            scale=(2, 0.5, 2),
            color=(139, 90, 43),  # Marrom
            texture=self.wood_texture,
            use_texture=True
        )
        
        # Porta
        self.render_object(
            self.cube_mesh,
            position=(0, 0.75, -6),
            scale=(0.4, 1, 0.1),
            color=(101, 67, 33),  # Marrom escuro
            texture=self.wood_texture,
            use_texture=True
        )
        
        # Janelas
        for x_offset in [-0.7, 0.7]:
            self.render_object(
                self.cube_mesh,
                position=(x_offset, 2, -6),
                scale=(0.3, 0.3, 0.1),
                color=(100, 150, 200),  # Azul
            )
        
        # ÁRVORES (cilindro + esfera)
        tree_positions = [(-5, 0, -8), (6, 0, -6), (-8, 0, 3)]
        
        for tree_x, tree_y, tree_z in tree_positions:
            # Tronco
            self.render_object(
                self.cylinder_mesh,
                position=(tree_x, tree_y + 2, tree_z),
                scale=(0.5, 2, 0.5),
                color=(139, 90, 43),  # Marrom
                texture=self.wood_texture,
                use_texture=True
            )
            
            # Copa
            self.render_object(
                self.sphere_mesh,
                position=(tree_x, tree_y + 4, tree_z),
                scale=(2, 2, 2),
                color=(34, 139, 34),  # Verde floresta
            )
        
        # CERCA (postes + barras)
        fence_z = 8
        for fence_x in np.arange(-8, 9, 2):
            # Poste vertical
            self.render_object(
                self.cube_mesh,
                position=(fence_x, 1, fence_z),
                scale=(0.15, 1.5, 0.15),
                color=(160, 100, 50),  # Madeira clara
                texture=self.wood_texture,
                use_texture=True
            )
            
            # Barra horizontal superior
            if fence_x < 8:
                self.render_object(
                    self.cube_mesh,
                    position=(fence_x + 0.5, 1.8, fence_z),
                    scale=(1, 0.1, 0.15),
                    color=(160, 100, 50),
                    texture=self.wood_texture,
                    use_texture=True
                )
                
                # Barra horizontal inferior
                self.render_object(
                    self.cube_mesh,
                    position=(fence_x + 0.5, 0.5, fence_z),
                    scale=(1, 0.1, 0.15),
                    color=(160, 100, 50),
                    texture=self.wood_texture,
                    use_texture=True
                )
        
        # PORTÃO ABERTO
        self.render_object(
            self.cube_mesh,
            position=(9, 1, fence_z),
            scale=(0.15, 1.5, 1.2),
            color=(160, 100, 50),
            texture=self.wood_texture,
            use_texture=True
        )
        
        # PEGADAS (pequenas manchas no chão)
        footprint_positions = [
            (0, 0.05, 0), (0.3, 0.05, 0.3), (0.6, 0.05, 0.5),
            (1, 0.05, 0.8), (1.5, 0.05, 1.2), (2, 0.05, 1.5),
            (2.5, 0.05, 2), (3.5, 0.05, 2.8), (4.5, 0.05, 3.5),
            (5.5, 0.05, 4.2), (6.5, 0.05, 4.8), (7.5, 0.05, 5.5),
            (8.5, 0.05, 6.5), (9, 0.05, 7.5)
        ]
        
        for fp_x, fp_y, fp_z in footprint_positions:
            # Cada pegada é feita de dois pequenos círculos
            for offset in [-0.15, 0.15]:
                self.render_object(
                    self.sphere_mesh,
                    position=(fp_x + offset, fp_y, fp_z),
                    scale=(0.1, 0.02, 0.1),
                    color=(60, 60, 60),  # Cinza escuro
                )
        
        # BRINQUEDO DA GATA (bola vermelha)
        self.render_object(
            self.sphere_mesh,
            position=(2, 0.5, -3),
            scale=(0.4, 0.4, 0.4),
            color=(220, 50, 50),  # Vermelho
        )
        
        # Fonte de luz (visualização)
        self.render_object(
            self.sphere_mesh,
            position=(self.light_pos[0], self.light_pos[1], self.light_pos[2]),
            scale=(0.3, 0.3, 0.3),
            color=(255, 255, 100),  # Amarelo (luz)
        )
    
    def run(self):
        """Loop principal"""
        while self.running:
            self.handle_events()
            self.update()
            self.render_scene()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


def main():
    """Função principal"""
    try:
        renderer = SceneRenderer()
        renderer.run()
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
