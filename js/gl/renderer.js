/** Renderizador WebGL com pipeline Phong. */
class Renderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.gl = canvas.getContext('webgl2', { antialias: true, alpha: false });
    if (!this.gl) throw new Error('WebGL 2 não suportado neste navegador.');

    this.program = this._createProgram(Shaders.vertexSource, Shaders.fragmentSource);
    this.skyProgram = this._createProgram(Shaders.skyVertexSource, Shaders.skyFragmentSource);

    this.uniforms = this._collectUniforms(this.program, [
      'uModel', 'uView', 'uProjection', 'uNormalMatrix', 'uViewPos',
      'uLightPos', 'uLightColor', 'uAmbientColor', 'uShininess',
      'uSpecularStrength', 'uSolidColor', 'uTexture', 'uUseTexture',
      'uUseSolidColor', 'uAlpha', 'uTime', 'uAnimatedWater',
    ]);

    this.skyUniforms = this._collectUniforms(this.skyProgram, [
      'uView', 'uProjection', 'uTopColor', 'uBottomColor', 'uTime',
    ]);

    const gl = this.gl;
    gl.enable(gl.DEPTH_TEST);
    gl.enable(gl.CULL_FACE);
    gl.cullFace(gl.BACK);

    this._normalMatrix = Mat4.create();
    this._modelView = Mat4.create();
    this.lightPos = Vec3.create(30, 40, 20);
    this.lightColor = Vec3.create(1.0, 0.95, 0.85);
    this.ambientColor = Vec3.create(0.55, 0.6, 0.75);
  }

  _createShader(type, source) {
    const gl = this.gl;
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const log = gl.getShaderInfoLog(shader);
      gl.deleteShader(shader);
      throw new Error(`Erro no shader: ${log}`);
    }
    return shader;
  }

  _createProgram(vs, fs) {
    const gl = this.gl;
    const program = gl.createProgram();
    const vShader = this._createShader(gl.VERTEX_SHADER, vs);
    const fShader = this._createShader(gl.FRAGMENT_SHADER, fs);
    gl.attachShader(program, vShader);
    gl.attachShader(program, fShader);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      throw new Error(`Erro ao linkar programa: ${gl.getProgramInfoLog(program)}`);
    }
    gl.deleteShader(vShader);
    gl.deleteShader(fShader);
    return program;
  }

  _collectUniforms(program, names) {
    const gl = this.gl;
    const uniforms = {};
    for (const name of names) {
      uniforms[name] = gl.getUniformLocation(program, name);
    }
    return uniforms;
  }

  resize() {
    const dpr = window.devicePixelRatio || 1;
    const w = this.canvas.clientWidth;
    const h = this.canvas.clientHeight;
    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;
    this.gl.viewport(0, 0, this.canvas.width, this.canvas.height);
    this.aspect = this.canvas.width / this.canvas.height;
  }

  updateLight(time, zone) {
    const t = time * 0.06;
    const radius = 60;
    this.lightPos[0] = Math.cos(t) * radius;
    this.lightPos[1] = 18 + Math.sin(t * 0.5) * 8 + zone * 2;
    this.lightPos[2] = Math.sin(t) * radius - 40;

    const dayFactor = 0.5 + 0.5 * Math.sin(t * 0.3);
    this.lightColor[0] = 0.9 + dayFactor * 0.1;
    this.lightColor[1] = 0.85 + dayFactor * 0.1;
    this.lightColor[2] = 0.7 + dayFactor * 0.15;

    if (zone >= 2) {
      this.ambientColor[0] = 0.25;
      this.ambientColor[1] = 0.35;
      this.ambientColor[2] = 0.3;
    } else {
      this.ambientColor[0] = 0.55;
      this.ambientColor[1] = 0.6;
      this.ambientColor[2] = 0.75;
    }
  }

  clear(zone) {
    const gl = this.gl;
    // Céu azul claro para quintal (zona 0-1)
    const skyTop = zone >= 4
      ? [0.5, 0.8, 0.95]    // Azul puro no campo final
      : zone >= 2
        ? [0.2, 0.4, 0.6]   // Azul mais escuro na floresta
        : [0.3, 0.65, 1.0]; // Azul intenso no quintal
    const skyBottom = zone >= 4
      ? [0.9, 0.9, 0.3]     // Horizonte dourado
      : zone >= 2
        ? [0.1, 0.2, 0.25]  // Horizonte escuro
        : [0.6, 0.8, 1.0];  // Horizonte azul claro
    gl.clearColor(skyBottom[0], skyBottom[1], skyBottom[2], 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    this._skyTop = skyTop;
    this._skyBottom = skyBottom;
  }

  drawSky(view, projection, time) {
    const gl = this.gl;
    gl.depthFunc(gl.LEQUAL);
    gl.useProgram(this.skyProgram);
    gl.uniformMatrix4fv(this.skyUniforms.uView, false, view);
    gl.uniformMatrix4fv(this.skyUniforms.uProjection, false, projection);
    gl.uniform3fv(this.skyUniforms.uTopColor, this._skyTop);
    gl.uniform3fv(this.skyUniforms.uBottomColor, this._skyBottom);
    gl.uniform1f(this.skyUniforms.uTime, time);

    gl.bindVertexArray(this.skyVAO);
    gl.drawArrays(gl.TRIANGLES, 0, 36);
    gl.depthFunc(gl.LESS);
  }

  setSkyMesh(vao) {
    this.skyVAO = vao;
  }

  drawMesh(mesh, view, projection, viewPos, time) {
    const gl = this.gl;
    gl.useProgram(this.program);

    const model = mesh.getModelMatrix();
    Mat4.multiply(this._modelView, view, model);
    Mat4.invert(this._normalMatrix, model);
    Mat4.transpose(this._normalMatrix, this._normalMatrix);

    gl.uniformMatrix4fv(this.uniforms.uModel, false, model);
    gl.uniformMatrix4fv(this.uniforms.uView, false, view);
    gl.uniformMatrix4fv(this.uniforms.uProjection, false, projection);
    gl.uniformMatrix4fv(this.uniforms.uNormalMatrix, false, this._normalMatrix);
    gl.uniform3fv(this.uniforms.uViewPos, viewPos);
    gl.uniform3fv(this.uniforms.uLightPos, this.lightPos);
    gl.uniform3fv(this.uniforms.uLightColor, this.lightColor);
    gl.uniform3fv(this.uniforms.uAmbientColor, this.ambientColor);
    gl.uniform1f(this.uniforms.uShininess, mesh.shininess);
    gl.uniform1f(this.uniforms.uSpecularStrength, mesh.specularStrength);
    gl.uniform1f(this.uniforms.uAlpha, mesh.alpha);
    gl.uniform1f(this.uniforms.uTime, time);
    gl.uniform1i(this.uniforms.uAnimatedWater, mesh.animatedWater ? 1 : 0);

    if (mesh.solidColor) {
      gl.uniform1i(this.uniforms.uUseSolidColor, 1);
      gl.uniform1i(this.uniforms.uUseTexture, 0);
      gl.uniform4fv(this.uniforms.uSolidColor, mesh.solidColor);
    } else if (mesh.texture) {
      gl.uniform1i(this.uniforms.uUseSolidColor, 0);
      gl.uniform1i(this.uniforms.uUseTexture, 1);
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, mesh.texture);
      gl.uniform1i(this.uniforms.uTexture, 0);
    } else {
      gl.uniform1i(this.uniforms.uUseSolidColor, 0);
      gl.uniform1i(this.uniforms.uUseTexture, 0);
    }

    if (mesh.alpha < 1.0) {
      gl.disable(gl.CULL_FACE);
      gl.enable(gl.BLEND);
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    }

    gl.bindVertexArray(mesh.vao);
    gl.drawElements(gl.TRIANGLES, mesh.indexCount, gl.UNSIGNED_SHORT, 0);

    if (mesh.alpha < 1.0) {
      gl.disable(gl.BLEND);
      gl.enable(gl.CULL_FACE);
    }
  }
}
