import pygame
import numpy as np

class Engine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Matriz de pixels (Buffer de cor) - Requisito: Exibição de matrizes [cite: 15]
        self.pixel_matrix = np.zeros((height, width, 3), dtype=np.uint8)

    def set_pixel(self, x, y, color):
        """Implementação base do Set Pixel [cite: 21]"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixel_matrix[int(y), int(x)] = color

    def update_surface(self, surface):
        """Transforma a matriz em uma imagem para o Pygame exibir [cite: 15]"""
        pygame.surfarray.blit_array(surface, self.pixel_matrix.swapaxes(0, 1))

    def clear(self, color=(0, 0, 0)):
        self.pixel_matrix[:] = color