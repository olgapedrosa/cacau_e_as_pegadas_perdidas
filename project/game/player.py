from engine.transform import Transform

class Cacau:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.angle = 0
        self.scale = 1.0

        self.base_shape = [
            (-10, -5), (0, -15), (10, -5),
            (10, 10), (0, 15), (-10, 10)   
        ]

    def get_transformed_points(self):
        T = Transform.translation_matrix(self.pos[0], self.pos[1])
        R = Transform.rotation_matrix(self.angle)
        S = Transform.scale_matrix(self.scale, self.scale)
        
        M = T @ R @ S
        
        return Transform.apply(self.base_shape, M)

    def move(self, dx, dy, target_angle):
        self.pos[0] += dx
        self.pos[1] += dy
        self.angle = target_angle 