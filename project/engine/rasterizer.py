class Rasterizer:
    @staticmethod
    def draw_line(engine, x0, y0, x1, y1, color):
        """Algoritmo de Bresenham [cite: 6, 22]"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            engine.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    @staticmethod
    def draw_circle(engine, xc, yc, r, color):
        """Ponto médio para circunferências [cite: 6, 22]"""
        x = 0
        y = r
        d = 3 - 2 * r
        Rasterizer._draw_circle_points(engine, xc, yc, x, y, color)
        while y >= x:
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            Rasterizer._draw_circle_points(engine, xc, yc, x, y, color)

    @staticmethod
    def _draw_circle_points(engine, xc, yc, x, y, color):
        points = [(xc+x, yc+y), (xc-x, yc+y), (xc+x, yc-y), (xc-x, yc-y),
                  (xc+y, yc+x), (xc-y, yc+x), (xc+y, yc-x), (xc-y, yc-x)]
        for px, py in points:
            engine.set_pixel(px, py, color)