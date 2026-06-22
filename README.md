# Cacau e as Pegadas Perdidas

Passeio virtual 3D narrativo desenvolvido para a disciplina de **Computação Gráfica (2026.1)**. O jogador assume o papel do dono da gata Cacau e segue suas pegadas por um quintal, jardim, bosque, lago e campo aberto até reencontrá-la.

## Sobre o projeto

Este é um passeio virtual em primeira pessoa com narrativa ambiental. Não há pontuação nem objetivo de "vencer" — o foco é explorar o cenário e acompanhar a história através da observação do ambiente e de textos que aparecem ao se aproximar de pontos de interesse.

### Áreas do passeio

| Área | Descrição |
|------|-----------|
| **Quintal** | Casa, árvores, cerca, brinquedo da gata e portão aberto |
| **Jardim** | Pote de ração derrubado, novelo de lã e arranhador |
| **Bosque** | Iluminação mais sombria, silhueta da Cacau ao longe, borboletas |
| **Lago** | Água texturizada, pedras e vegetação |
| **Campo final** | Cacau sentada ao centro, luz do sol entre as árvores |

## Requisitos técnicos atendidos

| Requisito | Implementação |
|-----------|---------------|
| WebGL puro (sem Three.js) | Pipeline completo com shaders GLSL 3.0 |
| Câmera em primeira pessoa | `FirstPersonCamera` com WASD + mouse |
| Projeção perspectiva | Matriz de perspectiva com FOV 60° |
| Iluminação Phong | Vertex + fragment shaders com ambiente, difusa e especular |
| Fonte de luz móvel | Sol que gira lentamente ao redor da cena |
| Objeto animado | Gata Cacau (cauda, cabeça, patas) e borboletas no bosque |
| Objeto com textura | Grama, madeira, pedra, tijolo, água e terra (procedurais) |
| Objeto com cor sólida | Cerca, postes, bancos e brinquedos |
| Cenário manual | Toda geometria gerada proceduralmente em código |
| Interação teclado/mouse | WASD/setas para mover, mouse para olhar |

## Estrutura do projeto

```
cacau_e_as_pegadas_perdidas/
├── index.html              # Página principal
├── css/style.css           # Interface (HUD, telas de início/fim)
├── js/
│   ├── main.js             # Loop principal do passeio
│   ├── gl/
│   │   ├── math.js         # Álgebra linear (matrizes e vetores)
│   │   ├── shaders.js      # Shaders GLSL com Phong
│   │   ├── camera.js       # Câmera em primeira pessoa
│   │   └── renderer.js     # Renderizador WebGL
│   ├── world/
│   │   ├── geometry.js     # Malhas 3D procedurais
│   │   ├── textures.js     # Texturas procedurais
│   │   ├── cat.js          # Modelo animado da Cacau
│   │   └── scene.js        # Construção da cena completa
│   └── game/
│       ├── input.js        # Teclado e mouse
│       └── narrative.js    # Sistema narrativo
└── README.md
```

## Como executar

### Pré-requisitos

- Navegador moderno com suporte a **WebGL 2.0** (Chrome, Firefox, Edge)
- Python 3 (para servidor HTTP local) ou qualquer servidor estático

### Passo a passo

1. Clone o repositório:

```bash
git clone https://github.com/SEU_USUARIO/cacau_e_as_pegadas_perdidas.git
cd cacau_e_as_pegadas_perdidas
```

2. Inicie um servidor HTTP local na pasta do projeto:

```bash
python3 -m http.server 8080
```

3. Abra no navegador:

```
http://localhost:8080
```

4. Clique em **"Começar o passeio"** e use o mouse para olhar ao redor.

### Controles

| Tecla | Ação |
|-------|------|
| W / ↑ | Andar para frente |
| S / ↓ | Andar para trás |
| A / ← | Andar para esquerda |
| D / → | Andar para direita |
| Mouse | Olhar ao redor |

## Equipe

<!-- Preencha com os nomes dos integrantes -->
- Nome 1
- Nome 2
- Nome 3

## Links

- **Apresentação (slides):** [inserir link]
- **Vídeo demonstrativo:** [inserir link]

## Tecnologias

- HTML5 Canvas (apenas inicialização do contexto)
- WebGL 2.0 puro
- JavaScript (ES6+)
- Álgebra linear implementada manualmente (`js/gl/math.js`)

## Licença

Projeto acadêmico — Computação Gráfica, UECE, 2026.1.
