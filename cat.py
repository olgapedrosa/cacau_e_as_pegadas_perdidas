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

    # --- NOVA ESCALA REDUZIDA ---
    # Diminuímos proporcionalmente para ficar do tamanho ideal em relação à cerca
    escala_gato = (0.022, 0.16, 0.022) 
    
    # Ajuste preciso para a base do plano tocar o chão (Y=0) com a nova escala
    posicao_ajustada = (x, y + 0.52, z)

    renderer.render_object(
        renderer.plane_mesh,
        position=posicao_ajustada,
        scale=escala_gato,
        color=(255, 255, 255),
        texture=cat_tex,
        use_texture=True,
        rotation=(90, 45, 0) # 90° em X para ficar em pé, 45° em Y para olhar a trilha
    )

    glEnable(GL_CULL_FACE)