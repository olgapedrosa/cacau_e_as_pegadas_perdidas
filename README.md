# Cacau e as Pegadas Perdidas — Passeio Virtual 3D

Passeio virtual 3D em OpenGL 4.0 (Python/PyOpenGL) para Computação Gráfica.

A gata **Cacau** saiu de casa e desapareceu. O jogador segue as pegadas pelo quintal, pela rua, e encontra a Cacau no final do caminho.

## Mapa

```
+----------------+
|    QUINTAL     |  grama, casa, pote de ração, pegadas
+----------------+
         |
         |  caminho único
         v
+----------------+
|      RUA       |  asfalto, calçadas, postes, árvores, pegadas
+----------------+
         |
         v
      CACAU 🐱
```

## Requisitos implementados

| Requisito | Implementação |
|-----------|---------------|
| Câmera 1ª pessoa + perspectiva | `camera.py` — WASD/Setas + mouse |
| Iluminação Phong | `shaders.py` — ambient + diffuse + specular |
| Luz móvel | `lightX = 20·cos(t)`, `lightZ = 20·sin(t)` |
| Objeto animado | Cauda da Cacau: `sin(t) × 20°` |
| Textura | `images/grama.png` no quintal (+ asfalto.png na rua) |
| Cor sólida | Casa azul, postes cinza |
| Cenário manual | Cubos, esferas e planos — sem OBJ externo |
| Narrativa | Texto inicial + "Você encontrou a Cacau!" ao chegar perto |

## Controles

| Tecla | Ação |
|-------|------|
| **W/A/S/D** | Mover |
| **Setas** | Mover (alternativo) |
| **Mouse** | Olhar ao redor |
| **ESC** | Sair |

## Instalação e execução

```bash
pip install -r requirements.txt
python3 main.py
```

## Estrutura do projeto

```
cacau_e_as_pegadas_perdidas/
├── main.py          # Loop principal, cena quintal + rua
├── cat.py           # Modelo da Cacau com cauda animada
├── camera.py        # Câmera em primeira pessoa
├── shaders.py       # Shaders GLSL 4.1 (Phong)
├── objects.py       # Malhas 3D (cubo, esfera, plano)
├── textures.py      # Carregamento de texturas PNG
├── images/          # grama.png, asfalto.png, gato.png, arvore.png
└── requirements.txt
```

## Detecção do final

Quando a distância entre o jogador e a Cacau for menor que 3 unidades:

```
"Você encontrou a Cacau!"
```

Disciplina: Computação Gráfica 2026.1 — Entrega: 26/06/2026
