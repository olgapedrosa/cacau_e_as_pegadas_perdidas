import math

class Rasterizer:
    @staticmethod
    def draw_line(engine, x0, y0, x1, y1, color):
        """Algoritmo de Bresenham para Retas"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            engine.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    @staticmethod
    def draw_circle(engine, xc, yc, r, color):
        """Algoritmo de Ponto Médio para Círculos"""
        x = 0
        y = r
        d = 1 - r
        
        # Desenha os 8 simétricos iniciais
        Rasterizer._circle_points(engine, xc, yc, x, y, color)
        
        while x < y:
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
            Rasterizer._circle_points(engine, xc, yc, x, y, color)

    @staticmethod
    def _circle_points(engine, xc, yc, x, y, color):
        """Auxiliar para desenhar os 8 octantes do círculo"""
        points = [
            (xc+x, yc+y), (xc-x, yc+y), (xc+x, yc-y), (xc-x, yc-y),
            (xc+y, yc+x), (xc-y, yc+x), (xc+y, yc-x), (xc-y, yc-x)
        ]
        for px, py in points:
            engine.set_pixel(px, py, color)

    @staticmethod
    def draw_ellipse(engine, xc, yc, rx, ry, color):
        """Algoritmo de Ponto Médio para Elipses"""
        x = 0
        y = ry
        
        # Região 1
        d1 = (ry**2) - (rx**2 * ry) + (0.25 * rx**2)
        dx = 2 * ry**2 * x
        dy = 2 * rx**2 * y
        
        while dx < dy:
            Rasterizer._ellipse_points(engine, xc, yc, x, y, color)
            if d1 < 0:
                x += 1
                dx += 2 * ry**2
                d1 += dx + ry**2
            else:
                x += 1
                y -= 1
                dx += 2 * ry**2
                dy -= 2 * rx**2
                d1 += dx - dy + ry**2
        
        # Região 2
        d2 = ((ry**2) * ((x + 0.5)**2)) + ((rx**2) * ((y - 1)**2)) - (rx**2 * ry**2)
        while y >= 0:
            Rasterizer._ellipse_points(engine, xc, yc, x, y, color)
            if d2 > 0:
                y -= 1
                dy -= 2 * rx**2
                d2 += rx**2 - dy
            else:
                y -= 1
                x += 1
                dx += 2 * ry**2
                dy -= 2 * rx**2
                d2 += dx - dy + rx**2

    @staticmethod
    def _ellipse_points(engine, xc, yc, x, y, color):
        """Auxiliar para os 4 quadrantes da elipse"""
        points = [
            (xc+x, yc+y), (xc-x, yc+y), (xc+x, yc-y), (xc-x, yc-y)
        ]
        for px, py in points:
            engine.set_pixel(px, py, color)