# Cacau e as Pegadas Perdidas — Passeio Virtual 3D

Um passeio virtual 3D narrativo desenvolvido em **WebGL 2 puro**, seguindo os requisitos da disciplina Computação Gráfica 2026.1 (UFPE).

## 🎮 Descrição

O projeto implementa um passeio virtual em primeira pessoa onde o jogador assume o papel do dono da gata Cacau. Após seu desaparecimento, o jogador segue suas pegadas através de cinco cenários distintos:

1. **Quintal** — O ponto de partida com a casa, árvores, cerca e o brinquedo favorito de Cacau
2. **Jardim** — Pistas do comportamento da gata (pote de ração, novelo de lã, arranhador)
3. **Bosque** — Área florestada com iluminação dinâmica e uma silhueta misteriosa
4. **Lago** — Paisagem aquática com água animada e pedras
5. **Campo Final** — O encontro final com Cacau

O projeto integra narrativa visual, exploração ambiental e mecânicas de câmera para criar uma experiência imersiva que evita necessidades de gameplay complexo.

## ✅ Requisitos Técnicos Atendidos

### Requisitos Gerais
- ✅ **Movimentação de câmera com projeção perspectiva** — Câmera em primeira pessoa com suporte a rotação livre e movimento em 4 direções
- ✅ **Sistema de iluminação Phong com fonte de luz móvel** — Luz do sol que se move ao longo do tempo, criando variação de iluminação
- ✅ **Objetos animados por transformações geométricas** — Gata Cacau com animações de corpo, cauda e pernas
- ✅ **Objetos com textura** — Grama, madeira, pedra, água (com animação procedural)
- ✅ **Objetos com cor sólida** — Cerca, brinquedos, pote, etc.
- ✅ **WebGL 2 puro** — Sem bibliotecas gráficas de alto nível (three.js)
- ✅ **Apenas bibliotecas auxiliares para álgebra linear** — Math.js nativo (sem dependências externas)
- ✅ **Canvas HTML5** — Inicialização do contexto WebGL sem funções gráficas adicionais
- ✅ **Captura de eventos teclado/mouse** — Suporte completo a WASD + mouse look

### Requisitos Específicos do Passeio Virtual 3D
- ✅ **Câmera em primeira pessoa** — Visão pelos olhos do personagem
- ✅ **Controle via teclado (WASD)** — Controle completo de movimentação
- ✅ **Controle opcional de mouse** — Mouse look (Pointer Lock API)
- ✅ **Sem detecção de colisão realista** — Apenas limitação de limites do mundo
- ✅ **Cenário construído manualmente** — Todas as geometrias geradas proceduralmente em código

## 🚀 Instruções de Compilação e Execução

### Requisitos
- **Navegador moderno** com suporte a WebGL 2 (Chrome, Firefox, Edge — versões recentes)
- **Servidor HTTP** local (obrigatório para evitar erros de CORS)

### Opção 1: Python (mais simples)

```bash
cd caminho/para/cacau_e_as_pegadas_perdidas
python -m http.server 8000
```

Depois acesse `http://localhost:8000` no navegador.

### Opção 2: Node.js + http-server

```bash
npm install -g http-server
cd caminho/para/cacau_e_as_pegadas_perdidas
http-server
```

### Opção 3: VS Code + Live Server

- Instale a extensão "Live Server" no VS Code
- Clique com botão direito em `index.html` → "Open with Live Server"

### Opção 4: PHP (se disponível)

```bash
cd caminho/para/cacau_e_as_pegadas_perdidas
php -S localhost:8000
```

## ⌨️ Controles

| Tecla | Ação |
|-------|------|
| **W** / **↑** | Andar para frente |
| **S** / **↓** | Andar para trás |
| **A** / **←** | Andar para esquerda |
| **D** / **→** | Andar para direita |
| **Mouse** | Olhar em volta (após clicar no canvas) |

**Dica:** Clique no canvas para ativar o pointer lock (controle de mouse). Pressione ESC para sair.

## 📁 Estrutura do Projeto

```
cacau_e_as_pegadas_perdidas/
├── index.html                 # Página principal (HTML5)
├── README.md                  # Este arquivo
├── css/
│   └── style.css              # Estilos e UI (HUD, telas)
├── js/
│   ├── main.js                # Ponto de entrada e loop principal
│   ├── game/
│   │   ├── input.js           # Captura de eventos (teclado/mouse)
│   │   └── narrative.js       # Sistema narrativo e triggers
│   ├── gl/
│   │   ├── camera.js          # Câmera em primeira pessoa
│   │   ├── math.js            # Álgebra linear (Mat4, Vec3)
│   │   ├── renderer.js        # Pipeline WebGL 2 com shading Phong
│   │   └── shaders.js         # Shaders GLSL (vertex + fragment)
│   └── world/
│       ├── cat.js             # Modelo procedural da gata + swarm de borboletas
│       ├── geometry.js        # Geração procedural de formas 3D
│       ├── scene.js           # Construção da cena (5 áreas + triggers)
│       └── textures.js        # Texturas procedurais (via Canvas 2D)
```

## 🔬 Implementação Técnica

### Câmera (Primeira Pessoa)
```javascript
- Matriz de visualização via Mat4.lookAt()
- Projeção perspectiva: FOV = 60°, near = 0.1, far = 300
- Mouse look com Pointer Lock API (clique para ativar)
- Altura fixa em 1.7 m (altura dos olhos)
- Movimento suave com delta time
```

### Iluminação (Modelo Phong)
```glsl
Fórmula: Color = Ambient + Diffuse + Specular
- Ambient:    Ka * Ia (luz ambiente dinâmica)
- Diffuse:    Kd * Id * (N · L)
- Specular:   Ks * Is * (R · V)^shininess
- Fonte de luz: órbita elíptica movendo-se ao longo do tempo
```

### Geometria Procedural (sem modelos externos)
Todas as formas construídas via geração de vértices:

| Forma | Implementação | Uso |
|-------|---------------|----|
| **Box** | 6 faces com normais | Paredes, casas, cerca, brinquedos |
| **Cilindro** | Segmentos 3D | Troncos, potes, pernas da gata |
| **Cone** | Pirâmide | Folhagem de árvores |
| **Esfera** | Latitude/longitude | Cabeça e corpo da gata, brinquedos |
| **Plano** | Quad simples | Terreno, água |
| **Pegadas** | Esfera + 3 toques | Trail no chão |

### Texturas Procedurais (Canvas 2D)
Todas as texturas geradas em runtime:

| Textura | Algoritmo |
|---------|-----------|
| **Grama** | Pontos aleatórios de verde com variação |
| **Madeira** | Padrão senoidal com linhas de nó |
| **Pedra** | Granito com dots aleatórios |
| **Tijolos** | Padrão de alvenaria com offset de linhas |
| **Água** | Ondulações sine/cos animadas em tempo real |
| **Terra** | Ruído aleatório de tons de marrom |

### Animações em Tempo Real

**Gata Cacau:**
```javascript
- Cauda: sin(time * 4) * 0.5 radianos
- Patas: sin(time * 3) * 0.15 movimento vertical
- Cabeça: sin(time * 2) * 0.08 movimento de bob
```

**Borboletas:** Órbita parametrizada com 3 eixos independentes

**Água:** Deslocamento de UV coordenadas via sin/cos

**Silhueta:** Movimento aleatório para criar impressão de criatura observando

### Sistema Narrativo
- Triggers baseados em distância (raio)
- Mensagens contextuais aparecem automaticamente
- Congelamento de câmera ao alcançar Cacau
- Estados: `start` → `playing` → `ending` → `ended`

## 📊 Checklist de Requisitos

| Critério | Peso | Implementado |
|----------|------|--------------|
| Projeção perspectiva e câmera | 10% | ✅ |
| Iluminação com modelo Phong | 10% | ✅ |
| Transformações geométricas e animações 3D | 10% | ✅ |
| Texturização 3D | 10% | ✅ |
| Leitor próprio de OBJ | — | ⭐ Opcional |
| Interação via teclado/mouse | 5% | ✅ |
| Criatividade, complexidade, design visual | 25% | ✅ Narrativa imersiva |
| Organização do código e documentação | 10% | ✅ |
| Apresentação em sala de aula | 25% | — |
| **TOTAL TÉCNICO** | **40%** | **✅ 100%** |

## 🎬 Experiência do Usuário

1. **Tela de início** — Contexto narrativo e instruções
2. **Exploração progressiva** — Quintal → Jardim → Bosque → Lago → Campo
3. **Feedback narrativo** — Mensagens ao se aproximar de pontos de interesse
4. **Iluminação dinâmica** — Luz muda conforme tempo passa (simulando día)
5. **Conclusão cinematográfica** — Câmera congela ao encontrar Cacau

## 🛠️ Tecnologias Utilizadas

- **WebGL 2** — Renderização 3D
- **GLSL 3.0 ES** — Shaders (Vertex + Fragment)
- **JavaScript ES6+** — Lógica e game loop
- **HTML5 Canvas** — Contexto gráfico e geração de texturas
- **CSS 3** — Interface do usuário
- **Pointer Lock API** — Controle de mouse immersivo

## 📈 Performance

- **Target:** 60 FPS em navegadores modernos
- **Otimizações:**
  - Delta time capped em 50ms
  - Frustum culling automático por distância
  - Texturas mipmapped com LINEAR_MIPMAP_LINEAR
  - Blend alpha apenas para meshes semi-transparentes

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| WebGL 2 não suportado | Use navegador moderno (Chrome 56+, Firefox 51+, Safari 11+) |
| Tela preta/vazia | Verifique console (F12) para erros; reinstale servidor HTTP |
| Câmera congelada | Aguarde 5 segundos no final ou recarregue a página |
| Performance baixa | Reduza a qualidade das texturas ou use navegador diferente |
| Mouse não funciona | Clique no canvas para ativar pointer lock |

## 👤 Créditos

**Disciplina:** Computação Gráfica 2026.1  
**Universidade:** UFPE  
**Tipo de Trabalho:** Passeio Virtual 3D com WebGL 2 Puro  
**Data de Entrega:** 26 de junho de 2026

---

**Nota:** Este projeto atende 100% dos requisitos técnicos obrigatórios da disciplina com foco em qualidade visual, narrativa imersiva e código bem estruturado.

Para questões técnicas, consulte o console do navegador (F12 → Console).

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

- Olga Pedrosa de Sousa
- Marília Milfont Rangel Lima

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
