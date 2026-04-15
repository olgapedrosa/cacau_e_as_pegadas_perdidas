import pygame
import numpy as np
import math

from engine.core import Engine
from engine.rasterizer import Rasterizer
from game.player import Cacau

def main():
    pygame.init()
    
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cacau e as Pegadas Perdidas")

    clock = pygame.time.Clock()

    engine = Engine(WIDTH, HEIGHT)
    raster = Rasterizer()
    cacau = Cacau(WIDTH // 2, HEIGHT // 2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        target_angle = cacau.angle

        if keys[pygame.K_LEFT]:
            dx, target_angle = -3, 180
        elif keys[pygame.K_RIGHT]:
            dx, target_angle = 3, 0
        elif keys[pygame.K_UP]:
            dy, target_angle = -3, 270
        elif keys[pygame.K_DOWN]:
            dy, target_angle = 3, 90
            
        cacau.move(dx, dy, target_angle)
        cacau.scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.005)

        engine.clear((30, 30, 30))

        raster.draw_line(engine, 200, 400, 600, 400, (255, 255, 255))
        raster.draw_line(engine, 200, 400, 400, 200, (255, 0, 0))
        raster.draw_line(engine, 400, 200, 600, 400, (255, 0, 0))
        raster.draw_circle(engine, 700, 100, 50, (255, 255, 0))
        raster.draw_ellipse(engine, 150, 100, 60, 30, (200, 200, 200))

        pontos = cacau.get_transformed_points()

        # to do pontos da cacau

        engine.update_surface(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()