"""
Sistema de câmera em primeira pessoa
"""

import math
import numpy as np
from pygame.locals import K_w, K_a, K_s, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT


class Camera:
    def __init__(self, position=(0, 1.6, -9)):
        self.position = np.array(position, dtype=np.float32)
        self.front = np.array([0, 0, 1], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.array([1, 0, 0], dtype=np.float32)

        self.yaw = 90.0
        self.pitch = 0.0

        self.speed = 0.12
        self.mouse_sensitivity = 0.12
        self.eye_height = 1.6
        self.ground_y = 0.0

        self.keys_pressed = set()

    def update(self):
        """Atualiza posição com WASD/setas, mantendo os pés no chão."""
        forward_xz = np.array([self.front[0], 0.0, self.front[2]], dtype=np.float32)
        norm = np.linalg.norm(forward_xz)
        if norm > 1e-6:
            forward_xz /= norm
        else:
            forward_xz = np.array([0.0, 0.0, 1.0], dtype=np.float32)

        right_xz = np.cross(forward_xz, np.array([0.0, 1.0, 0.0], dtype=np.float32))
        right_xz /= np.linalg.norm(right_xz)

        move = np.zeros(3, dtype=np.float32)

        if K_w in self.keys_pressed or K_UP in self.keys_pressed:
            move += forward_xz * self.speed
        if K_s in self.keys_pressed or K_DOWN in self.keys_pressed:
            move -= forward_xz * self.speed
        if K_a in self.keys_pressed or K_LEFT in self.keys_pressed:
            move -= right_xz * self.speed
        if K_d in self.keys_pressed or K_RIGHT in self.keys_pressed:
            move += right_xz * self.speed

        self.position += move
        self._apply_ground_collision()

    def _apply_ground_collision(self):
        """Impede voar ou afundar — altura fixa acima do chão y=0."""
        self.position[1] = self.ground_y + self.eye_height

    def mouse_look(self, dx, dy):
        """Atualiza rotação da câmera baseada no movimento do mouse."""
        self.yaw += dx * self.mouse_sensitivity
        self.pitch -= dy * self.mouse_sensitivity

        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        self.update_vectors()

    def update_vectors(self):
        """Atualiza vetores front, right e up baseado em yaw e pitch."""
        front = np.array([
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
        ], dtype=np.float32)

        self.front = front / np.linalg.norm(front)
        self.right = np.cross(self.front, np.array([0, 1, 0], dtype=np.float32))
        self.right = self.right / np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)

    def get_view_matrix(self):
        """Retorna a matriz de visualização (view matrix)."""
        forward = self.front
        right = self.right
        up = self.up

        view = np.identity(4, dtype=np.float32)
        view[0, 0:3] = right
        view[1, 0:3] = up
        view[2, 0:3] = -forward

        view[0, 3] = -np.dot(right, self.position)
        view[1, 3] = -np.dot(up, self.position)
        view[2, 3] = np.dot(forward, self.position)

        return view

    def add_key_pressed(self, key):
        self.keys_pressed.add(key)

    def remove_key_pressed(self, key):
        self.keys_pressed.discard(key)
