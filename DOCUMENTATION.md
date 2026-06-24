# Documentação Técnica - Cacau e as Pegadas Perdidas

## Mapeamento de Requisitos

### 1. Movimentação de Câmera com Projeção Perspectiva

**Arquivo**: `camera.py` + `main.py`

```python
# Câmera em primeira pessoa
camera = Camera(position=(5, 2, 10))

# Matriz de projeção perspectiva
projection = np.identity(4, dtype=np.float32)
aspect = WINDOW_WIDTH / WINDOW_HEIGHT
f = 1.0 / math.tan(math.radians(45) / 2)  # FOV = 45°
projection[0, 0] = f / aspect
projection[1, 1] = f
projection[2, 2] = -(far + near) / (far - near)
projection[2, 3] = -(2 * far * near) / (far - near)
```

**Funcionalidades**:

- Câmera segue o posicionamento 3D
- Projeção perspectiva com FOV 45°
- Matriz de visualização baseada em yaw/pitch
- Near plane: 0.1, Far plane: 100.0

### 2. Sistema de Iluminação com Modelo de Phong

**Arquivo**: `shaders.py` (Fragment Shader)

```glsl
// Componentes de Phong
vec3 ambient = ambientStrength * lightColor;

vec3 norm = normalize(Normal);
vec3 lightDir = normalize(lightPos - FragPos);
float diff = max(dot(norm, lightDir), 0.0);
vec3 diffuse = diff * lightColor;

float specularStrength = 0.5;
vec3 viewDir = normalize(viewPos - FragPos);
vec3 reflectDir = reflect(-lightDir, norm);
float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
vec3 specular = specularStrength * spec * lightColor;

vec3 result = (ambient + diffuse + specular) * objectColor;
```

**Especificações**:

- Coeficiente de reflexão especular (shininess): 32.0
- Força ambiente: 0.3
- Força especular: 0.5
- Luz RGB branca: (1.0, 1.0, 1.0)

### 3. Movimentação de Fonte de Luz

**Arquivo**: `main.py` (função `update()`)

```python
# Luz se move em trajetória circular + oscilação vertical
self.animation_angle += 0.005
self.light_pos[0] = 5 + 3 * math.cos(self.animation_angle)
self.light_pos[2] = 3 * math.sin(self.animation_angle)
self.light_pos[1] = 4 + math.sin(self.animation_angle * 2) * 0.5
```

**Comportamento**:

- Centro da órbita: (5, 4, 0)
- Raio da órbita: 3 unidades
- Oscilação vertical: ±0.5 unidades
- Velocidade: 0.005 radianos/frame

### 4. Objeto Animado por Transformações Geométricas

**Arquivo**: `main.py` (renderização da luz)

A fonte de luz é renderizada como esfera animada:

- Posição: atualizada continuamente
- Escala: fixa em (0.3, 0.3, 0.3)
- Cor: amarelo (255, 255, 100)

Além disso, há animação implícita nas pegadas que seguem a narrativa.

### 5. Objeto com Textura

**Arquivo**: `textures.py` + `main.py`

```python
# Textura de grama no chão
self.render_object(
    self.plane_mesh,
    position=(0, 0, 0),
    scale=(1, 1, 1),
    color=(100, 150, 80),
    texture=self.grass_texture,
    use_texture=True
)

# Textura procedural
grass_data = create_grass_texture()  # 512x512 RGB
```

**Texturas implementadas**:

1. Grama (chão)
2. Madeira (cerca, telhado, troncos)
3. Cor sólida para outros objetos

### 6. Objeto com Cor Sólida

**Arquivo**: `main.py` (vários objetos)

```python
# Casa com cor sólida (bege)
self.render_object(
    self.cube_mesh,
    position=(0, 1.5, -5),
    scale=(2, 1.5, 2),
    color=(200, 180, 140),  # RGB
    use_texture=False
)

# Implementação no shader
if (useTexture)
    result = (ambient + diffuse + specular) * texColor;
else
    result = (ambient + diffuse + specular) * objectColor;
```

### 7. Renderização Exclusiva com OpenGL 4.0

**Arquivo**: `shaders.py`

```glsl
#version 410  // Versão GLSL 4.1

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
```

**Características OpenGL 4.0+**:

- VAO (Vertex Array Objects)
- VBO (Vertex Buffer Objects)
- EBO (Element Buffer Objects)
- Layout qualifiers
- Uniform blocks (implícito)

### 8. Câmera em Primeira Pessoa

**Arquivo**: `camera.py`

```python
class Camera:
    def __init__(self, position=(5, 2, 10), target=(0, 1, 0)):
        self.position = np.array(position, dtype=np.float32)
        self.front = np.array([0, 0, -1], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.array([1, 0, 0], dtype=np.float32)

        # Yaw e Pitch para rotação
        self.yaw = -90.0
        self.pitch = 0.0
```

**Funcionalidades**:

- Movimento nos 3 eixos (XYZ)
- Rotação via yaw/pitch
- Atualização de vetores front/right/up
- Cálculo de view matrix

### 9. Controle via Teclado e Mouse

**Arquivo**: `camera.py` + `main.py`

```python
# Teclado (WASD + Setas)
if ord('w') in self.keys_pressed:
    self.position += self.front * self.speed

# Mouse (rotação)
def mouse_look(self, dx, dy):
    self.yaw += dx * self.mouse_sensitivity
    self.pitch -= dy * self.mouse_sensitivity
```

**Velocidades**:

- Movimento: 0.1 unidades/frame
- Rotação do mouse: 0.1° por pixel

## Estrutura de Dados

### Mesh (objects.py)

```python
class Mesh:
    VAO: GLuint          # Vertex Array Object
    VBO: GLuint[3]       # Vertex Buffer Objects (pos, normal, texcoord)
    EBO: GLuint          # Element Buffer Object (índices)
    vertex_count: int    # Número de vértices a renderizar
```

### Matriz Model-View-Projection

```
Transformação do vértice:
gl_Position = projection * view * model * position

Onde:
- model: Transforma de espaço local para mundial
- view: Transforma de espaço mundial para câmera
- projection: Transforma de espaço câmera para clip space
```

## Otimizações Implementadas

### 1. Cache de Primitivas

```python
_cube = None
_sphere = None
_cylinder = None
_plane = None

def get_cube():
    global _cube
    if _cube is None:
        _cube = create_cube()
    return _cube
```

**Benefício**: Cada malha é criada uma única vez

### 2. Culling de Faces

```python
glEnable(GL_CULL_FACE)
glCullFace(GL_BACK)  # Não renderiza faces traseiras
```

**Benefício**: Reduz carga de GPU em ~50%

### 3. Texturas Procedurais

Todas as texturas são geradas em tempo de execução, sem dependências de arquivos externos.

### 4. Mipmapping

```python
glGenerateMipmap(GL_TEXTURE_2D)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
```

**Benefício**: Melhor qualidade em perspectivas distantes

## Performance

### Métricas Esperadas

- **FPS**: 60 (com V-Sync)
- **Renderização por frame**: ~15-20ms
- **Memória VRAM**: ~50-100MB
- **Memória RAM**: ~150-200MB

### Bottlenecks Possíveis

1. **Número de draw calls**: ~25-30 por frame
2. **Número de vértices**: ~100k-200k total
3. **Número de texturas**: 4 (todas 512x512)

## Extensibilidade

### Adicionar Nova Cena

```python
def render_scene_2(self):
    """Render da próxima área"""
    # Implementar similarmente a render_scene()
    pass
```

### Adicionar Novo Objeto

```python
def create_pyramid():
    """Cria um cubo (cena 2)"""
    vertices = np.array([...], dtype=np.float32)
    normals = np.array([...], dtype=np.float32)
    indices = np.array([...], dtype=np.uint32)
    return Mesh(vertices, normals, indices)
```

### Adicionar Novo Shader

```python
CUSTOM_SHADER = """
#version 410
// Implementação...
"""

program = glCreateProgram()
glAttachShader(program, vertex)
glAttachShader(program, custom_fragment)
glLinkProgram(program)
```

## Debugging

### Verificar Versão OpenGL

```python
version = glGetString(GL_VERSION).decode()
print(f"OpenGL: {version}")
```

### Verificar Erros de Shader

```python
error = glGetShaderInfoLog(shader).decode()
if error:
    print(f"Shader Error: {error}")
```

### Visualizar Normais

Ativar modo wireframe:

```python
glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
```

## Referências Usadas

1. **LearnOpenGL** - https://learnopengl.com/
2. **OpenGL Tutorial** - https://www.opengl-tutorial.org/
3. **Real-Time Rendering** - Akenine-Möller et al.
4. **Computer Graphics: Principles and Practice** - Foley et al.

## Próximas Implementações

- [ ] Skybox 360°
- [ ] Leitor OBJ
- [ ] Detecção de colisão
- [ ] Sistema de partículas
- [ ] Áudio 3D
- [ ] Normal mapping
- [ ] Shadow mapping
- [ ] Instancing (rendering múltiplos objetos iguais)
