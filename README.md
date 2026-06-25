# Cacau e as Pegadas Perdidas

Passeio virtual 3D em OpenGL 4.0, feito em Python com PyOpenGL e Pygame.

A gata Cacau desapareceu do quintal, e o objetivo do jogador e seguir as pegadas ate encontrala. O caminho passa por areas do quintal com casa, arvore, pote de racao, bolinha animada e uma cena com iluminacao Phong.

## Funcionalidades

- Camera em primeira pessoa com mouse e teclado
- Iluminacao Phong com luz em movimento circular lento
- Cena 3D montada com cubos, esferas e planos
- Texturas para grama, parede, pegadas, racao, ceu e gato
- Mensagens narrativas durante o percurso
- Tela inicial e tela final centralizadas
- Pote de racao com frente dupla e topo texturizado

## Controles

- `WASD` ou `Setas`: mover
- `Mouse`: olhar ao redor
- `Enter` ou `Espaco`: iniciar o jogo a partir do menu
- `ESC`: sair

## Como executar

Instale as dependencias e rode o jogo:

```bash
pip install -r requirements.txt
python3 main.py
```

No Linux, voce tambem pode usar:

```bash
bash setup.sh
```

## Estrutura do projeto

```text
cacau_e_as_pegadas_perdidas/
├── main.py
├── camera.py
├── cat.py
├── objects.py
├── shaders.py
├── textures.py
├── DOCUMENTATION.md
├── requirements.txt
├── setup.sh
├── setup.bat
└── images/
    ├── ceu.png
    ├── gato.png
    ├── grama.png
    ├── parede.png
    ├── pegada.png
    └── racao.png
```

## Dependencias

- PyOpenGL
- PyOpenGL-accelerate
- Pygame
- Pillow
- NumPy

## Observacoes do projeto

- O jogo foi construido sem modelos externos, usando primitivas geometricas.
- As mensagens da narrativa aparecem conforme o jogador se aproxima de objetos especificos.
- O sol se move lentamente em orbita para destacar a iluminacao da cena.
- A bolinha do quintal possui animacao lateral curta e discreta.

## Documentacao tecnica

Veja [DOCUMENTATION.md](DOCUMENTATION.md) para detalhes de implementacao, shaders, camera e mapeamento dos requisitos.

## Contexto

Projeto de Computacao Grafica.
