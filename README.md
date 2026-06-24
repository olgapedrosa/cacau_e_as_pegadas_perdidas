# Cacau e as Pegadas Perdidas - Passeio Virtual 3D

## Visão Geral

**Cacau e as Pegadas Perdidas** é um passeio virtual 3D narrativo desenvolvido em OpenGL 4.0 (Python/PyOpenGL) para a disciplina de Computação Gráfica. O projeto implementa um cenário interativo onde o usuário assume o papel do dono de uma gata desaparecida e segue suas pegadas pelo quintal.

## Conceito

Em vez de um jogo tradicional com objetivos e pontuação, o projeto oferece uma experiência de exploração narrativa:

- **Ponto de partida**: Quintal de casa
- **Objetivo**: Seguir as pegadas de Cacau e explorar o cenário
- **Estilo**: Mistura de passeio virtual e exploração ambiental
- **Câmera**: Primeira pessoa com controles intuitivos

## Requisitos Implementados

### Requisitos Gerais

- ✅ Movimentação de câmera com projeção perspectiva
- ✅ Sistema de iluminação com modelo de reflexão de Phong
- ✅ Movimentação de fonte de luz
- ✅ Objeto animado por transformações geométricas (luz móvel + pegadas animadas)
- ✅ Objetos com texturas (grama, madeira, brinquedo)
- ✅ Objetos com cores sólidas (casa, árvores, cerca)
- ✅ Renderização exclusiva com OpenGL 4.0
- ✅ Uso permitido de bibliotecas auxiliares (NumPy para álgebra linear)
- ✅ Interação via teclado e mouse

### Requisitos Específicos do Passeio Virtual

- ✅ Câmera em primeira pessoa
- ✅ Controle via teclado (WASD) e mouse
- ✅ Cenário construído manualmente no código
- ✅ Sem necessidade de detecção de colisão realista

## Estrutura do Projeto

```
cacau_e_as_pegadas_perdidas/
├── main.py              # Loop principal de renderização
├── camera.py            # Sistema de câmera em primeira pessoa
├── shaders.py           # Vertex e fragment shaders (Phong)
├── objects.py           # Geração de malhas 3D (cubos, esferas, cilindros, planos)
├── textures.py          # Carregamento e gerenciamento de texturas
├── requirements.txt     # Dependências do projeto
└── README.md            # Este arquivo
```

## Cenário - Primeira Área (Quintal)

### Elementos da Cena

1. **Terreno** - Plano verde escalado representando grama
2. **Casa** - Construída com cubos (paredes, telhado, porta, janelas)
3. **Árvores** - Cilindros + esferas (3 árvores espalhadas pelo cenário)
4. **Cerca** - Cubos finos e altos formando barreira
5. **Pegadas** - Pequenas esferas achatadas seguindo um caminho
6. **Brinquedo** - Esfera vermelha representando brinquedo da gata
7. **Portão Aberto** - Cubo rotacionado no final da cerca

### Mapa do Cenário

```
             Árvore
                    Cerca ------------------

       Pegadas →  Casa                 Portão
           [ ]     /                    [ ]
    Brinquedo     /
      Árvore  [ ]
```

## Texturas Implementadas

O projeto inclui texturas procedurais para:

1. **Grama** - Textura do terreno com tons de verde variados
2. **Madeira** - Textura dos postes da cerca e telhado
3. **Céu** - Gradiente de azul (futuro: implementar skybox)
4. **Brinquedo** - Vermelho sólido

Todas as texturas são geradas proceduralmente no código.

## Controles

| Tecla     | Ação                              |
| --------- | --------------------------------- |
| **W**     | Mover para frente                 |
| **A**     | Mover para esquerda               |
| **S**     | Mover para trás                   |
| **D**     | Mover para direita                |
| **↑**     | Mover para frente (alternativo)   |
| **←**     | Mover para esquerda (alternativo) |
| **↓**     | Mover para trás (alternativo)     |
| **→**     | Mover para direita (alternativo)  |
| **Mouse** | Olhar ao redor                    |
| **ESC**   | Sair do programa                  |

## Instalação e Execução

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação de Dependências

```bash
# No diretório do projeto
pip install -r requirements.txt
```

Se encontrar problemas com PyOpenGL, tente:

```bash
pip install --upgrade pip setuptools wheel
pip install PyOpenGL PyOpenGL_accelerate
```

### Execução

```bash
python main.py
```

A janela do OpenGL deve abrir com tamanho 1200x800 pixels.

## Arquitetura Técnica

### Shaders

O projeto utiliza shaders GLSL 4.1:

- **Vertex Shader**: Cálculo de posição dos vértices e normais
- **Fragment Shader**: Implementação do modelo de Phong com texturas

### Câmera

Sistema de câmera em primeira pessoa com:

- Controle de yaw e pitch baseado em mouse
- Movimento suave via teclas pressionadas
- Cálculo de matriz de visualização via método de negação de pontos

### Iluminação

Implementação do modelo de Phong com:

- **Ambient**: Componente ambiente para iluminação de fundo
- **Diffuse**: Reflexão difusa baseada em ângulo de incidência
- **Specular**: Reflexão especular para efeitos de brilho
- Fonte de luz dinâmica que se move pela cena

### Malhas 3D

Geração procedural de primitivas geométricas:

- Cubos (6 faces, normais por vértice)
- Esferas (parametrizadas por latitude/longitude)
- Cilindros (topo, base e lado)
- Planos (subdivididos para melhor interpolação)

## Detalhes de Implementação

### Otimizações

1. **Cache de Meshes**: Primitivas são criadas uma única vez e reutilizadas
2. **Texturas Procedurais**: Geradas em tempo de execução, sem dependências externas
3. **Culling de Faces**: Apenas faces frontal são renderizadas
4. **Test de Profundidade**: Ordem correta de renderização garantida

### Melhorias Futuras

1. Implementar skybox 360° para céu
2. Adicionar leitor OBJ para modelos externos
3. Implementar detecção de colisão básica
4. Adicionar som ambiental
5. Criar próximas áreas do passeio (jardim, rua, etc.)
6. Implementar partículas para pegadas dinâmicas

## Compilação Alternativa

Se preferir usar C++ com OpenGL nativo:

```bash
# Criar build com CMake
mkdir build
cd build
cmake ..
make
./cacau_3d
```

(Template CMakeLists.txt disponível separadamente)

## Performance

- **FPS Target**: 60 FPS
- **Resolução**: 1200x800
- **Limite de Profundidade**: 0.1 a 100 unidades
- **FOV**: 45 graus

## Documentação Adicional

### Estrutura de Arquivos

Cada arquivo Python contém:

- Docstrings explicando funções principais
- Comentários inline para lógica complexa
- Type hints para melhor legibilidade

### Exemplos de Uso

#### Criar uma esfera personalizada

```python
from objects import create_sphere
sphere = create_sphere(radius=2.0, stacks=40, slices=40)
renderer.render_object(sphere, position=(0, 0, 0), scale=(1, 1, 1), color=(255, 0, 0))
```

#### Carregar textura customizada

```python
from textures import Texture
custom_texture = Texture(image_path="path/to/image.png")
renderer.render_object(mesh, texture=custom_texture, use_texture=True)
```

## Créditos e Referências

### Ferramentas Utilizadas

- OpenGL 4.0+
- Python 3.x
- PyOpenGL
- Pygame (context e input)
- NumPy (álgebra linear)

### Inspirações

- Tutorial de LearnOpenGL (learnopengl.com)
- Documentação oficial OpenGL
- Computer Graphics: Principles and Practice

## Licença

Este projeto foi desenvolvido para fins educacionais na disciplina de Computação Gráfica.

## Autor

Desenvolvido por: [Seu Nome/Equipe]
Data de Entrega: 26 de junho de 2026
Disciplina: Computação Gráfica 2026.1

---

**Nota**: Certifique-se de que seu sistema suporta OpenGL 4.0. Use `glxinfo` (Linux) ou `GPU-Z` (Windows) para verificar a versão suportada.
