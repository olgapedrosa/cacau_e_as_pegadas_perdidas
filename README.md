# 🐾 Cacau e as Pegadas Perdidas

**Passeio Virtual 3D desenvolvido para a disciplina de Computação Gráfica**

## 👥 Participantes

- **Olga Pedrosa de Sousa**
- **Marília Milfont Rangel Lima**

---

# 📖 Sobre o Projeto

**Cacau e as Pegadas Perdidas** é um passeio virtual tridimensional desenvolvido utilizando **Python** e **OpenGL Moderno (OpenGL 4.1)**.

O projeto coloca o usuário na perspectiva do dono de Cacau, uma gata curiosa e aventureira que saiu para explorar o quintal e demorou mais do que o habitual para voltar para casa. Preocupado, o jogador precisa percorrer o ambiente em busca de pistas que indiquem onde ela está.

Durante a exploração, o jogador encontra objetos importantes da rotina de Cacau, como sua árvore favorita, seu pote de ração e sua bolinha de brinquedo. Cada ponto do cenário apresenta uma breve narrativa que ajuda a contar a história e conduz o jogador até o reencontro com a gata.

Além de proporcionar uma experiência de exploração em primeira pessoa, o projeto aplica diversos conceitos estudados na disciplina de Computação Gráfica, como renderização 3D, iluminação, texturização, transformações geométricas e interação com o usuário.

---

# 📚 História

Cacau sempre adorou explorar o quintal da casa. Subir em árvores, brincar com sua bolinha e passear entre os arbustos fazia parte da sua rotina.

Em um determinado dia, porém, ela saiu para mais uma aventura e acabou demorando para retornar. Seu dono, preocupado com seu desaparecimento, decide procurá-la pelo quintal.

Durante o passeio, diversos objetos despertam lembranças da gata e servem como pistas do caminho percorrido por ela. Seguindo essas pistas, o jogador finalmente encontra Cacau em segurança, encerrando a aventura com um reencontro feliz.

---

# 🎯 Objetivos

Este projeto tem como objetivo aplicar, de forma prática, os principais conceitos estudados na disciplina de Computação Gráfica, incluindo:

- Construção de um ambiente tridimensional;
- Sistema de câmera em primeira pessoa;
- Renderização utilizando OpenGL Moderno;
- Iluminação baseada no modelo de reflexão de Phong;
- Aplicação de texturas;
- Utilização de objetos com cores sólidas;
- Transformações geométricas;
- Interação por teclado e mouse;
- Organização modular do código.

---

# ✨ Funcionalidades

O passeio virtual oferece as seguintes funcionalidades:

- Movimentação em primeira pessoa utilizando teclado;
- Controle da visão através do mouse;
- Cenário tridimensional desenvolvido manualmente;
- Sistema de iluminação baseado no modelo de Phong;
- Objetos texturizados;
- Objetos com cores sólidas;
- Mensagens narrativas distribuídas ao longo da exploração;
- Experiência interativa de exploração.

---

# 🛠️ Tecnologias Utilizadas

- Python 3
- PyOpenGL
- Pygame
- NumPy
- Pillow (PIL)

---

# 📁 Estrutura do Projeto

```text
Projeto/
│
├── main.py                # Arquivo principal
├── camera.py              # Sistema de câmera em primeira pessoa
├── objects.py             # Construção dos objetos da cena
├── shaders.py             # Vertex e Fragment Shaders
├── textures.py            # Sistema de gerenciamento de texturas
├── cat.py                 # Renderização da personagem Cacau
│
├── imagens/
│   ├── grama.png
│   ├── ceu.png
│   ├── parede.png
│   ├── racao.png
│   ├── pegada.png
│   └── gato.png
│
└── README.md
```

---

# 🎮 Controles

| Tecla | Função |
|--------|--------|
| **W** | Andar para frente |
| **S** | Andar para trás |
| **A** | Mover para a esquerda |
| **D** | Mover para a direita |
| **↑ ↓ ← →** | Movimentação alternativa |
| **Mouse** | Controlar a direção da câmera |
| **ESC** | Encerrar a aplicação |

---

# 🌳 Elementos do Cenário

O cenário foi construído manualmente e inclui diversos elementos, entre eles:

- Casa;
- Quintal;
- Chão;
- Muros;
- Árvores;
- Arbustos;
- Céu;
- Pegadas;
- Pote de ração;
- Bolinha de brinquedo;
- Personagem Cacau.

---

# 💡 Recursos de Computação Gráfica

Durante o desenvolvimento foram utilizados diversos conceitos estudados na disciplina:

- Projeção em perspectiva;
- Sistema de câmera em primeira pessoa;
- Matrizes de transformação (translação, rotação e escala);
- Vertex Shader;
- Fragment Shader;
- Iluminação utilizando o modelo de reflexão de Phong;
- Aplicação de texturas;
- Objetos com cores sólidas;
- Buffer de profundidade (Depth Test);
- OpenGL 4.1 Core Profile.

---

# ▶️ Como Executar

## 1. Instale as dependências

```bash
pip install pygame PyOpenGL PyOpenGL_accelerate numpy pillow
```

## 2. Execute o projeto

```bash
python main.py
```

---

# 🧭 Experiência do Usuário

Ao iniciar o passeio virtual, o jogador assume a perspectiva do dono de Cacau e inicia sua busca pelo quintal.

Ao longo do percurso, diferentes elementos do ambiente apresentam pequenas mensagens narrativas que ajudam a contar a história e conduzem o jogador pela exploração.

O objetivo é percorrer o quintal, observar as pistas deixadas por Cacau e encontrá-la em segurança, concluindo a aventura.

---

# 🎥 Vídeo de Demonstração

O funcionamento completo do projeto pode ser visualizado no vídeo disponível no link abaixo:

**🔗 Link do vídeo:**

> **https://coloque-aqui-o-link-do-video**

---

# 📌 Considerações Finais

O desenvolvimento de **Cacau e as Pegadas Perdidas** possibilitou a aplicação prática dos principais conceitos abordados na disciplina de Computação Gráfica, integrando renderização 3D, iluminação, texturização, transformações geométricas e interação em um único projeto.

Além dos aspectos técnicos, buscou-se desenvolver uma experiência simples, intuitiva e envolvente, utilizando uma narrativa leve para tornar a exploração do ambiente mais interessante.

O resultado é um passeio virtual que demonstra a utilização dos principais recursos estudados ao longo da disciplina, evidenciando a integração entre programação, matemática aplicada e computação gráfica na construção de ambientes tridimensionais interativos.