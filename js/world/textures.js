/** Texturas procedurais geradas em código (sem arquivos externos). */
const Textures = {
  _createCanvas(w, h, drawFn) {
    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d');
    drawFn(ctx, w, h);
    return canvas;
  },

  _upload(gl, canvas) {
    const tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, canvas);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.generateMipmap(gl.TEXTURE_2D);
    return tex;
  },

  grass(gl) {
    const canvas = this._createCanvas(128, 128, (ctx, w, h) => {
      ctx.fillStyle = '#3a7d32';
      ctx.fillRect(0, 0, w, h);
      for (let i = 0; i < 400; i++) {
        const x = Math.random() * w;
        const y = Math.random() * h;
        const g = 80 + Math.random() * 80;
        ctx.fillStyle = `rgb(${g * 0.4 | 0}, ${g | 0}, ${g * 0.3 | 0})`;
        ctx.fillRect(x, y, 2, 4 + Math.random() * 4);
      }
    });
    return this._upload(gl, canvas);
  },

  wood(gl) {
    const canvas = this._createCanvas(128, 128, (ctx, w, h) => {
      ctx.fillStyle = '#8B5A2B';
      ctx.fillRect(0, 0, w, h);
      for (let y = 0; y < h; y++) {
        const shade = 0.85 + Math.sin(y * 0.3) * 0.1 + Math.random() * 0.05;
        ctx.fillStyle = `rgb(${139 * shade | 0}, ${90 * shade | 0}, ${43 * shade | 0})`;
        ctx.fillRect(0, y, w, 1);
      }
      for (let i = 0; i < 8; i++) {
        ctx.strokeStyle = 'rgba(60,30,10,0.3)';
        ctx.beginPath();
        ctx.moveTo(Math.random() * w, 0);
        ctx.lineTo(Math.random() * w, h);
        ctx.stroke();
      }
    });
    return this._upload(gl, canvas);
  },

  stone(gl) {
    const canvas = this._createCanvas(128, 128, (ctx, w, h) => {
      ctx.fillStyle = '#7a7a72';
      ctx.fillRect(0, 0, w, h);
      for (let i = 0; i < 200; i++) {
        const x = Math.random() * w;
        const y = Math.random() * h;
        const s = 3 + Math.random() * 8;
        const g = 100 + Math.random() * 60;
        ctx.fillStyle = `rgb(${g | 0}, ${g | 0}, ${(g - 10) | 0})`;
        ctx.beginPath();
        ctx.arc(x, y, s, 0, Math.PI * 2);
        ctx.fill();
      }
    });
    return this._upload(gl, canvas);
  },

  brick(gl) {
    const canvas = this._createCanvas(128, 128, (ctx, w, h) => {
      const bw = 32, bh = 16;
      for (let row = 0; row < h / bh; row++) {
        const offset = (row % 2) * (bw / 2);
        for (let col = -1; col < w / bw + 1; col++) {
          const shade = 0.8 + Math.random() * 0.2;
          ctx.fillStyle = `rgb(${180 * shade | 0}, ${90 * shade | 0}, ${70 * shade | 0})`;
          ctx.fillRect(col * bw + offset, row * bh, bw - 2, bh - 2);
        }
      }
    });
    return this._upload(gl, canvas);
  },

  water(gl) {
    const canvas = this._createCanvas(128, 128, (ctx, w, h) => {
      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
          const wave = Math.sin(x * 0.15) * Math.cos(y * 0.12);
          const r = 30 + wave * 15;
          const g = 100 + wave * 30;
          const b = 180 + wave * 20;
          ctx.fillStyle = `rgb(${r | 0},${g | 0},${b | 0})`;
          ctx.fillRect(x, y, 1, 1);
        }
      }
    });
    return this._upload(gl, canvas);
  },

  dirt(gl) {
    const canvas = this._createCanvas(128, 128, (ctx, w, h) => {
      ctx.fillStyle = '#6b4c2a';
      ctx.fillRect(0, 0, w, h);
      for (let i = 0; i < 300; i++) {
        const shade = 0.7 + Math.random() * 0.4;
        ctx.fillStyle = `rgb(${107 * shade | 0}, ${76 * shade | 0}, ${42 * shade | 0})`;
        ctx.fillRect(Math.random() * w, Math.random() * h, 3, 3);
      }
    });
    return this._upload(gl, canvas);
  },
};
