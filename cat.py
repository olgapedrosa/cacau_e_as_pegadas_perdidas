import math
from OpenGL.GL import *

def render_cacau(renderer, position, time_sec):
    """
    Renderiza a Cacau com tamanho reduzido e perfeitamente ajustada ao chão.
    """
    x, y, z = position
    cat_tex = renderer.cat_texture

    # Habilita a transparência
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glDisable(GL_CULL_FACE)

    # Um pouco maior e com a base apoiada no chão
    escala_gato = (0.03, 0.20, 0.03)

    # Ajuste para a parte inferior encostar no chão sem flutuar
    posicao_ajustada = (x, y + 0.25, z)

    renderer.render_object(
        renderer.plane_mesh,
        position=posicao_ajustada,
        scale=escala_gato,
        color=(255, 255, 255),
        texture=cat_tex,
        use_texture=True,
        rotation=(90, 25, 0), # 90° em X para ficar em pé, 25° em Y para pegar melhor a luz
        brightness_boost=2.1,
    )

    glEnable(GL_CULL_FACE)