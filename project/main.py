import pygame
import numpy as np
from engine.core import Engine
from engine.rasterizer import Rasterizer

def main():
    pygame.init()
    
    # Configurações da tela
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cacau e as Pegadas Perdidas - Engine Test")
    
    # Inicializa nosso motor "na mão"
    engine = Engine(WIDTH, HEIGHT)
    raster = Rasterizer()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 1. Limpa a tela
        engine.clear((30, 30, 30)) # Fundo cinza escuro

        # --- TESTES DA PESSOA A ---
        # Desenhar uma casa simples usando retas (Bresenham)
        raster.draw_line(engine, 200, 400, 600, 400, (255, 255, 255)) # Base
        raster.draw_line(engine, 200, 400, 400, 200, (255, 0, 0))   # Telhado Esq
        raster.draw_line(engine, 400, 200, 600, 400, (255, 0, 0))   # Telhado Dir

        # Desenhar o Sol (Círculo de Ponto Médio)
        raster.draw_circle(engine, 700, 100, 50, (255, 255, 0))
        
        # Desenhar uma nuvem (Elipse)
        raster.draw_ellipse(engine, 150, 100, 60, 30, (200, 200, 200))
        # --------------------------

        # 2. Renderiza a matriz na tela do Pygame
        engine.update_surface(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()