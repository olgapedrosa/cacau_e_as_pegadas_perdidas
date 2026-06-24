"""
Sistema de câmera em primeira pessoa
"""

import math
import numpy as np

class Camera:
    def __init__(self, position=(5, 2, 10), target=(0, 1, 0)):
        self.position = np.array(position, dtype=np.float32)
        self.front = np.array([0, 0, -1], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.array([1, 0, 0], dtype=np.float32)
        
        # Rotação (yaw e pitch)
        self.yaw = -90.0
        self.pitch = 0.0
        
        # Velocidades
        self.speed = 0.1
        self.mouse_sensitivity = 0.1
        
        # Estado das teclas
        self.keys_pressed = set()
        
    def update(self):
        """Atualiza posição da câmera baseada em teclas pressionadas"""
        # Movimento WASD
        if ord('w') in self.keys_pressed or ord('W') in self.keys_pressed:
            self.position += self.front * self.speed
        if ord('s') in self.keys_pressed or ord('S') in self.keys_pressed:
            self.position -= self.front * self.speed
        if ord('a') in self.keys_pressed or ord('A') in self.keys_pressed:
            self.position -= self.right * self.speed
        if ord('d') in self.keys_pressed or ord('D') in self.keys_pressed:
            self.position += self.right * self.speed
            
        # Também suporte para setas
        if 273 in self.keys_pressed:  # UP
            self.position += self.front * self.speed
        if 274 in self.keys_pressed:  # DOWN
            self.position -= self.front * self.speed
        if 276 in self.keys_pressed:  # LEFT
            self.position -= self.right * self.speed
        if 275 in self.keys_pressed:  # RIGHT
            self.position += self.right * self.speed
    
    def mouse_look(self, dx, dy):
        """Atualiza rotação da câmera baseada no movimento do mouse"""
        self.yaw += dx * self.mouse_sensitivity
        self.pitch -= dy * self.mouse_sensitivity
        
        # Limita pitch para evitar flip
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
        
        # Atualiza vetores de direção
        self.update_vectors()
    
    def update_vectors(self):
        """Atualiza vetores front, right e up baseado em yaw e pitch"""
        front = np.array([
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        ], dtype=np.float32)
        
        self.front = front / np.linalg.norm(front)
        self.right = np.cross(self.front, np.array([0, 1, 0], dtype=np.float32))
        self.right = self.right / np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)
    
    def get_view_matrix(self):
        """Retorna a matriz de visualização (view matrix)"""
        from numpy.linalg import norm
        
        forward = self.front
        right = self.right
        up = self.up
        
        center = self.position + forward
        
        # Criar view matrix manualmente
        view = np.identity(4, dtype=np.float32)
        view[0, 0:3] = right
        view[1, 0:3] = up
        view[2, 0:3] = -forward
        
        view[0, 3] = -np.dot(right, self.position)
        view[1, 3] = -np.dot(up, self.position)
        view[2, 3] = np.dot(forward, self.position)
        
        return view
    
    def add_key_pressed(self, key):
        """Registra tecla pressionada"""
        self.keys_pressed.add(key)
    
    def remove_key_pressed(self, key):
        """Remove tecla do conjunto de pressionadas"""
        self.keys_pressed.discard(key)
