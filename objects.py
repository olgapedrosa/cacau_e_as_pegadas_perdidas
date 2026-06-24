"""
Funções para criar e renderizar objetos 3D
"""

import numpy as np
import math
from OpenGL.GL import *
from OpenGL.GLU import *


class Mesh:
    """Malha 3D com VAO, VBO e índices"""
    
    def __init__(self, vertices, normals, indices, texcoords=None):
        self.vertex_count = len(indices)
        
        # Criar VAO
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
        
        # Criar VBOs
        self.VBO = glGenBuffers(3)
        
        # Vértices
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO[0])
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        # Normais
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO[1])
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        
        # Coordenadas de textura
        if texcoords is None:
            texcoords = np.zeros((len(vertices), 2), dtype=np.float32)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO[2])
        glBufferData(GL_ARRAY_BUFFER, texcoords.nbytes, texcoords, GL_STATIC_DRAW)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glEnableVertexAttribArray(2)
        
        # EBO para índices
        self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        
        glBindVertexArray(0)
    
    def render(self):
        """Renderiza a malha"""
        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, self.vertex_count, GL_UNSIGNED_INT, None)


def create_cube():
    """Cria um cubo unitário (-1 a 1)"""
    vertices = np.array([
        # Face frontal
        [-1, -1,  1], [ 1, -1,  1], [ 1,  1,  1], [-1,  1,  1],
        # Face traseira
        [-1, -1, -1], [ 1, -1, -1], [ 1,  1, -1], [-1,  1, -1],
        # Face superior
        [-1,  1, -1], [ 1,  1, -1], [ 1,  1,  1], [-1,  1,  1],
        # Face inferior
        [-1, -1, -1], [ 1, -1, -1], [ 1, -1,  1], [-1, -1,  1],
        # Face direita
        [ 1, -1, -1], [ 1,  1, -1], [ 1,  1,  1], [ 1, -1,  1],
        # Face esquerda
        [-1, -1, -1], [-1,  1, -1], [-1,  1,  1], [-1, -1,  1],
    ], dtype=np.float32)
    
    # Normais por vértice
    normals = np.array([
        # Face frontal
        [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],
        # Face traseira
        [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1],
        # Face superior
        [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0],
        # Face inferior
        [0, -1, 0], [0, -1, 0], [0, -1, 0], [0, -1, 0],
        # Face direita
        [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0],
        # Face esquerda
        [-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0],
    ], dtype=np.float32)
    
    # Índices para triângulos
    indices = np.array([
        0, 1, 2, 0, 2, 3,      # Frontal
        4, 6, 5, 4, 7, 6,      # Traseira
        8, 9, 10, 8, 10, 11,   # Superior
        12, 14, 13, 12, 15, 14, # Inferior
        16, 18, 17, 16, 19, 18, # Direita
        20, 21, 22, 20, 22, 23, # Esquerda
    ], dtype=np.uint32)
    
    # Coordenadas de textura
    texcoords = np.array([
        [0, 0], [1, 0], [1, 1], [0, 1],  # Frontal
        [0, 0], [1, 0], [1, 1], [0, 1],  # Traseira
        [0, 0], [1, 0], [1, 1], [0, 1],  # Superior
        [0, 0], [1, 0], [1, 1], [0, 1],  # Inferior
        [0, 0], [1, 0], [1, 1], [0, 1],  # Direita
        [0, 0], [1, 0], [1, 1], [0, 1],  # Esquerda
    ], dtype=np.float32)
    
    return Mesh(vertices, normals, indices, texcoords)


def create_sphere(radius=1.0, stacks=30, slices=30):
    """Cria uma esfera usando latitudes e longitudes"""
    vertices = []
    normals = []
    indices = []
    texcoords = []
    
    for i in range(stacks + 1):
        stack_angle = math.pi / 2 - i * math.pi / stacks
        xy = radius * math.cos(stack_angle)
        z = radius * math.sin(stack_angle)
        
        for j in range(slices + 1):
            slice_angle = j * 2 * math.pi / slices
            
            x = xy * math.cos(slice_angle)
            y = xy * math.sin(slice_angle)
            
            vertices.append([x, z, y])
            
            # Normal é igual à posição normalizada
            normal = np.array([x, z, y]) / radius
            normals.append(normal)
            
            # Coordenadas de textura
            u = j / slices
            v = i / stacks
            texcoords.append([u, v])
    
    # Gerar índices
    for i in range(stacks):
        k1 = i * (slices + 1)
        k2 = k1 + slices + 1
        
        for j in range(slices):
            if i != 0:
                indices.append(k1)
                indices.append(k2)
                indices.append(k1 + 1)
            
            if i != stacks - 1:
                indices.append(k1 + 1)
                indices.append(k2)
                indices.append(k2 + 1)
            
            k1 += 1
            k2 += 1
    
    return Mesh(np.array(vertices, dtype=np.float32),
                np.array(normals, dtype=np.float32),
                np.array(indices, dtype=np.uint32),
                np.array(texcoords, dtype=np.float32))


def create_cylinder(radius=1.0, height=2.0, slices=30):
    """Cria um cilindro"""
    vertices = []
    normals = []
    indices = []
    texcoords = []
    
    # Vértices top
    for i in range(slices):
        angle = 2 * math.pi * i / slices
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        
        vertices.append([x, height / 2, z])
        normals.append([math.cos(angle), 0, math.sin(angle)])
        texcoords.append([i / slices, 1])
    
    # Vértices bottom
    for i in range(slices):
        angle = 2 * math.pi * i / slices
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        
        vertices.append([x, -height / 2, z])
        normals.append([math.cos(angle), 0, math.sin(angle)])
        texcoords.append([i / slices, 0])
    
    # Topo e base (capas)
    # Centro do topo
    vertices.append([0, height / 2, 0])
    normals.append([0, 1, 0])
    texcoords.append([0.5, 0.5])
    
    # Centro da base
    vertices.append([0, -height / 2, 0])
    normals.append([0, -1, 0])
    texcoords.append([0.5, 0.5])
    
    # Lado
    for i in range(slices):
        k1 = i
        k2 = (i + 1) % slices
        k3 = i + slices
        k4 = ((i + 1) % slices) + slices
        
        indices.extend([k1, k3, k2])
        indices.extend([k2, k3, k4])
    
    # Topo
    top_center = 2 * slices
    for i in range(slices):
        indices.extend([top_center, i, (i + 1) % slices])
    
    # Base
    bottom_center = 2 * slices + 1
    for i in range(slices):
        indices.extend([bottom_center, (i + 1) % slices + slices, i + slices])
    
    return Mesh(np.array(vertices, dtype=np.float32),
                np.array(normals, dtype=np.float32),
                np.array(indices, dtype=np.uint32),
                np.array(texcoords, dtype=np.float32))


def create_plane(width=10, height=10, subdivisions=10):
    """Cria um plano para o chão"""
    vertices = []
    normals = []
    indices = []
    texcoords = []
    
    step_x = width / subdivisions
    step_z = height / subdivisions
    
    # Gerar vértices
    for z in range(subdivisions + 1):
        for x in range(subdivisions + 1):
            vx = -width / 2 + x * step_x
            vz = -height / 2 + z * step_z
            
            vertices.append([vx, 0, vz])
            normals.append([0, 1, 0])
            texcoords.append([x / subdivisions, z / subdivisions])
    
    # Gerar índices
    for z in range(subdivisions):
        for x in range(subdivisions):
            a = z * (subdivisions + 1) + x
            b = a + 1
            c = a + subdivisions + 1
            d = c + 1
            
            indices.extend([a, c, b])
            indices.extend([b, c, d])
    
    return Mesh(np.array(vertices, dtype=np.float32),
                np.array(normals, dtype=np.float32),
                np.array(indices, dtype=np.uint32),
                np.array(texcoords, dtype=np.float32))


def create_footprint_quad(width=0.36, depth=0.42):
    """Quad horizontal no chão (plano XZ) para textura de pegada."""
    hw = width / 2
    hd = depth / 2

    vertices = np.array([
        [-hw, 0.0, -hd],
        [ hw, 0.0, -hd],
        [ hw, 0.0,  hd],
        [-hw, 0.0,  hd],
    ], dtype=np.float32)

    normals = np.array([
        [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0],
    ], dtype=np.float32)

    # Dedos da textura (topo da imagem) apontam para +Z (direção da rua)
    texcoords = np.array([
        [0, 1], [1, 1], [1, 0], [0, 0],
    ], dtype=np.float32)

    indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

    return Mesh(vertices, normals, indices, texcoords)


import ctypes

# Exportar meshes pré-criadas para reutilização
_cube = None
_sphere = None
_cylinder = None
_plane = None
_footprint_quad = None

def get_cube():
    global _cube
    if _cube is None:
        _cube = create_cube()
    return _cube

def get_sphere():
    global _sphere
    if _sphere is None:
        _sphere = create_sphere(1.0, 20, 20)
    return _sphere

def get_cylinder():
    global _cylinder
    if _cylinder is None:
        _cylinder = create_cylinder(1.0, 2.0, 20)
    return _cylinder

def get_plane():
    global _plane
    if _plane is None:
        _plane = create_plane(50, 50, 20)
    return _plane

def get_footprint_quad():
    global _footprint_quad
    if _footprint_quad is None:
        _footprint_quad = create_footprint_quad()
    return _footprint_quad
