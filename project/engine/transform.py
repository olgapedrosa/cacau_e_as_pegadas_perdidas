import numpy as np
import math

class Transform:
    @staticmethod
    def translation_matrix(dx, dy):
        return np.array([
            [1, 0, dx],
            [0, 1, dy],
            [0, 0, 1]
        ])

    @staticmethod
    def scale_matrix(sx, sy):
        return np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ])

    @staticmethod
    def rotation_matrix(angle_degrees):
        rad = math.radians(angle_degrees)
        return np.array([
            [math.cos(rad), -math.sin(rad), 0],
            [math.sin(rad),  math.cos(rad), 0],
            [0,             0,              1]
        ])

    @staticmethod
    def apply(points, matrix):
        """
        points: lista de tuplas [(x1, y1), (x2, y2), ...]
        Retorna os pontos transformados.
        """
        transformed_points = []
        for x, y in points:
            v = np.array([x, y, 1])
            res = matrix @ v
            transformed_points.append((res[0], res[1]))
        return transformed_points