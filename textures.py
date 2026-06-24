"""
Sistema de carregamento de texturas
"""

import numpy as np
from PIL import Image
from OpenGL.GL import *

class Texture:
    def __init__(self, image_path=None, color=None, width=256, height=256, transparent_black=False):
        """
        Cria uma textura a partir de um arquivo de imagem ou cor sólida
        
        Args:
            image_path: Caminho para o arquivo de imagem
            color: Tupla (R, G, B) para cor sólida (0-255)
            width, height: Dimensões para texturas procedurais
            transparent_black: Torna pixels pretos transparentes (para pegadas)
        """
        self.texture_id = glGenTextures(1)
        self.has_alpha = False
        
        if image_path:
            self.load_from_image(image_path, transparent_black)
        elif color:
            self.load_from_color(color, width, height)
        else:
            self.load_checkerboard(width, height)
    
    def load_from_image(self, image_path, transparent_black=False):
        """Carrega textura de um arquivo PNG/JPG."""
        try:
            img = Image.open(image_path).convert("RGBA")
            img_data = np.array(img, dtype=np.uint8)

            if transparent_black:
                dark = (
                    (img_data[:, :, 0] < 45)
                    & (img_data[:, :, 1] < 45)
                    & (img_data[:, :, 2] < 45)
                )
                img_data[:, :, 3] = np.where(dark, 0, img_data[:, :, 3])

            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RGBA,
                img.width, img.height, 0,
                GL_RGBA, GL_UNSIGNED_BYTE, img_data,
            )
            glGenerateMipmap(GL_TEXTURE_2D)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            self.has_alpha = transparent_black
            print(f"Textura carregada: {image_path}")
        except Exception as e:
            print(f"Erro ao carregar textura {image_path}: {e}")
            self.load_checkerboard(256, 256)
    
    def load_from_color(self, color, width=256, height=256):
        """Carrega textura de cor sólida"""
        r, g, b = color
        img_data = np.full((height, width, 3), [r, g, b], dtype=np.uint8)
        
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    def load_checkerboard(self, width=256, height=256):
        """Carrega textura em padrão xadrez (fallback)"""
        img_data = np.zeros((height, width, 3), dtype=np.uint8)
        
        checker_size = 32
        for i in range(height):
            for j in range(width):
                if ((i // checker_size) + (j // checker_size)) % 2 == 0:
                    img_data[i, j] = [200, 200, 200]
                else:
                    img_data[i, j] = [100, 100, 100]
        
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    def bind(self):
        """Ativa a textura para renderização"""
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
    
    def unbind(self):
        """Desativa a textura"""
        glBindTexture(GL_TEXTURE_2D, 0)


class TextureManager:
    """Gerenciador de texturas com cache"""
    
    def __init__(self):
        self.textures = {}
    
    def load_texture(self, name, image_path=None, color=None):
        """Carrega ou retorna textura em cache"""
        if name in self.textures:
            return self.textures[name]
        
        texture = Texture(image_path, color)
        self.textures[name] = texture
        return texture
    
    def get_texture(self, name):
        """Obtém textura pelo nome"""
        return self.textures.get(name)


# Funções auxiliares para gerar texturas procedurais

def create_grass_texture():
    """Cria textura de grama procedural"""
    width, height = 512, 512
    img_data = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Tons de verde variados
    for i in range(height):
        for j in range(width):
            base_green = np.random.randint(60, 120)
            variation = np.random.randint(-10, 10)
            img_data[i, j] = [
                20,  # R - pouco vermelho
                base_green + variation,  # G
                30   # B
            ]
    
    return img_data

def create_wood_texture():
    """Cria textura de madeira procedural"""
    width, height = 512, 512
    img_data = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Padrão de madeira simples
    for i in range(height):
        for j in range(width):
            wood_value = int(150 + 50 * np.sin(j / 20.0))
            variation = np.random.randint(-15, 15)
            img_data[i, j] = [
                wood_value + variation,
                int(wood_value * 0.8) + variation,
                int(wood_value * 0.6) + variation
            ]
    
    return img_data

def create_sky_texture():
    """Cria textura de céu procedural (gradiente azul)"""
    width, height = 512, 512
    img_data = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Gradiente do azul claro ao azul mais escuro
    for i in range(height):
        gradient = int(200 - (i / height) * 100)
        img_data[i, :] = [
            int(gradient * 0.7),  # R
            int(gradient * 0.9),  # G
            gradient              # B
        ]
    
    return img_data
