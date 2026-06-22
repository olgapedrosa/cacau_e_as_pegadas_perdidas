/** Geração procedural de malhas 3D (sem modelos externos). */
const Geometry = {
  _pushFace(positions, normals, texCoords, indices, verts, normal, uvs, baseIndex) {
    for (let i = 0; i < verts.length; i += 3) {
      positions.push(verts[i], verts[i + 1], verts[i + 2]);
      normals.push(normal[0], normal[1], normal[2]);
      texCoords.push(uvs[i / 3 * 2] || 0, uvs[i / 3 * 2 + 1] || 0);
    }
    for (const idx of indices) {
      this._indices.push(baseIndex + idx);
    }
  },

  _reset() {
    this._positions = [];
    this._normals = [];
    this._texCoords = [];
    this._indices = [];
  },

  _build() {
    return {
      positions: new Float32Array(this._positions),
      normals: new Float32Array(this._normals),
      texCoords: new Float32Array(this._texCoords),
      indices: new Uint16Array(this._indices),
    };
  },

  box(w, h, d) {
    this._reset();
    const hw = w / 2, hh = h / 2, hd = d / 2;
    const faces = [
      { n: [0, 0, 1], v: [-hw,-hh,hd, hw,-hh,hd, hw,hh,hd, -hw,hh,hd], uv: [0,0,1,0,1,1,0,1], idx: [0,1,2,0,2,3] },
      { n: [0, 0,-1], v: [hw,-hh,-hd,-hw,-hh,-hd,-hw,hh,-hd, hw,hh,-hd], uv: [0,0,1,0,1,1,0,1], idx: [0,1,2,0,2,3] },
      { n: [1, 0, 0], v: [hw,-hh,hd, hw,-hh,-hd, hw,hh,-hd, hw,hh,hd], uv: [0,0,1,0,1,1,0,1], idx: [0,1,2,0,2,3] },
      { n: [-1,0, 0], v: [-hw,-hh,-hd,-hw,-hh,hd,-hw,hh,hd,-hw,hh,-hd], uv: [0,0,1,0,1,1,0,1], idx: [0,1,2,0,2,3] },
      { n: [0, 1, 0], v: [-hw,hh,hd, hw,hh,hd, hw,hh,-hd,-hw,hh,-hd], uv: [0,0,1,0,1,1,0,1], idx: [0,1,2,0,2,3] },
      { n: [0,-1, 0], v: [-hw,-hh,-hd, hw,-hh,-hd, hw,-hh,hd,-hw,-hh,hd], uv: [0,0,1,0,1,1,0,1], idx: [0,1,2,0,2,3] },
    ];
    let base = 0;
    for (const f of faces) {
      Geometry._pushFace(this._positions, this._normals, this._texCoords, this._indices, f.v, f.n, f.uv, base);
      base += 4;
    }
    return this._build();
  },

  plane(w, d, flip = false) {
    this._reset();
    const hw = w / 2, hd = d / 2;
    const y = flip ? 0.01 : 0;
    const n = flip ? [0, -1, 0] : [0, 1, 0];
    const verts = [-hw, y, -hd, hw, y, -hd, hw, y, hd, -hw, y, hd];
    const uv = [0, 0, w * 0.15, 0, w * 0.15, d * 0.15, 0, d * 0.15];
    Geometry._pushFace(this._positions, this._normals, this._texCoords, this._indices, verts, n, uv, 0);
    return this._build();
  },

  cylinder(radius, height, segments = 16) {
    this._reset();
    const halfH = height / 2;
    for (let i = 0; i < segments; i++) {
      const a0 = (i / segments) * Math.PI * 2;
      const a1 = ((i + 1) / segments) * Math.PI * 2;
      const x0 = Math.cos(a0) * radius, z0 = Math.sin(a0) * radius;
      const x1 = Math.cos(a1) * radius, z1 = Math.sin(a1) * radius;
      const nx0 = Math.cos(a0), nz0 = Math.sin(a0);
      const nx1 = Math.cos(a1), nz1 = Math.sin(a1);
      const base = this._positions.length / 3;
      const verts = [
        x0, -halfH, z0, x1, -halfH, z1, x1, halfH, z1, x0, halfH, z0,
      ];
      const uvs = [i / segments, 0, (i + 1) / segments, 0, (i + 1) / segments, 1, i / segments, 1];
      Geometry._pushFace(this._positions, this._normals, this._texCoords, this._indices, verts, [nx0, 0, nz0], uvs, base);
    }
    return this._build();
  },

  cone(radius, height, segments = 12) {
    this._reset();
    const tip = [0, height, 0];
    for (let i = 0; i < segments; i++) {
      const a0 = (i / segments) * Math.PI * 2;
      const a1 = ((i + 1) / segments) * Math.PI * 2;
      const x0 = Math.cos(a0) * radius, z0 = Math.sin(a0) * radius;
      const x1 = Math.cos(a1) * radius, z1 = Math.sin(a1) * radius;
      const base = this._positions.length / 3;
      const verts = [x0, 0, z0, x1, 0, z1, tip[0], tip[1], tip[2]];
      const edge = Vec3.create(x0 + x1, height, z0 + z1);
      Vec3.normalize(edge, edge);
      Geometry._pushFace(this._positions, this._normals, this._texCoords, this._indices, verts, [edge[0], edge[1], edge[2]], [0, 0, 1, 0, 0.5, 1], base);
    }
    return this._build();
  },

  sphere(radius, segments = 12, rings = 8) {
    this._reset();
    for (let ring = 0; ring < rings; ring++) {
      const phi0 = (ring / rings) * Math.PI;
      const phi1 = ((ring + 1) / rings) * Math.PI;
      for (let seg = 0; seg < segments; seg++) {
        const theta0 = (seg / segments) * Math.PI * 2;
        const theta1 = ((seg + 1) / segments) * Math.PI * 2;
        const v = [];
        const pts = [[theta0, phi0], [theta1, phi0], [theta1, phi1], [theta0, phi1]];
        for (const [theta, phi] of pts) {
          const x = radius * Math.sin(phi) * Math.cos(theta);
          const y = radius * Math.cos(phi);
          const z = radius * Math.sin(phi) * Math.sin(theta);
          v.push(x, y, z);
          this._normals.push(x / radius, y / radius, z / radius);
          this._texCoords.push(seg / segments, ring / rings);
        }
        const base = this._positions.length / 3;
        this._positions.push(...v);
        this._indices.push(base, base + 1, base + 2, base, base + 2, base + 3);
      }
    }
    return this._build();
  },

  _addSphereAt(cx, cy, cz, radius, seg, rings) {
    const base = this._positions.length / 3;
    for (let ring = 0; ring < rings; ring++) {
      const phi0 = (ring / rings) * Math.PI;
      const phi1 = ((ring + 1) / rings) * Math.PI;
      for (let s = 0; s < seg; s++) {
        const theta0 = (s / seg) * Math.PI * 2;
        const theta1 = ((s + 1) / seg) * Math.PI * 2;
        const pts = [[theta0, phi0], [theta1, phi0], [theta1, phi1], [theta0, phi1]];
        const vBase = this._positions.length / 3;
        for (const [theta, phi] of pts) {
          const x = cx + radius * Math.sin(phi) * Math.cos(theta);
          const y = cy + radius * Math.cos(phi);
          const z = cz + radius * Math.sin(phi) * Math.sin(theta);
          this._positions.push(x, y, z);
          this._normals.push(Math.sin(phi) * Math.cos(theta), Math.cos(phi), Math.sin(phi) * Math.sin(theta));
          this._texCoords.push(0, 0);
        }
        this._indices.push(vBase, vBase + 1, vBase + 2, vBase, vBase + 2, vBase + 3);
      }
    }
    return base;
  },

  pawPrint() {
    this._reset();
    this._addSphereAt(0, 0.02, 0, 0.12, 8, 6);
    const toes = [[-0.08, 0.05, 0.1], [0, 0.08, 0.12], [0.08, 0.05, 0.1]];
    for (const [tx, ty, tz] of toes) {
      this._addSphereAt(tx, ty, tz, 0.05, 6, 4);
    }
    return this._build();
  },

  skybox() {
    this._reset();
    const s = 200;
    const verts = [
      -s,-s,s, s,-s,s, s,s,s, -s,-s,s, s,s,s, -s,s,s,
      s,-s,-s,-s,-s,-s,-s,s,-s, s,-s,-s,-s,s,-s, s,s,-s,
      s,-s,s, s,-s,-s, s,s,-s, s,-s,s, s,s,-s, s,s,s,
      -s,-s,-s,-s,-s,s,-s,s,s,-s,-s,-s,-s,s,s,-s,s,-s,
      -s,s,s, s,s,s, s,s,-s,-s,s,s, s,s,-s,-s,s,-s,
      -s,-s,-s, s,-s,-s, s,-s,s,-s,-s,-s, s,-s,s,-s,-s,s,
    ];
    for (let i = 0; i < verts.length; i += 3) {
      this._positions.push(verts[i], verts[i + 1], verts[i + 2]);
      this._normals.push(0, 0, 0);
      this._texCoords.push(0, 0);
    }
    for (let i = 0; i < verts.length / 3; i++) this._indices.push(i);
    return this._build();
  },
};

function createGLMesh(gl, geometry) {
  const vao = gl.createVertexArray();
  gl.bindVertexArray(vao);

  const posBuf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, posBuf);
  gl.bufferData(gl.ARRAY_BUFFER, geometry.positions, gl.STATIC_DRAW);
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);

  const normBuf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, normBuf);
  gl.bufferData(gl.ARRAY_BUFFER, geometry.normals, gl.STATIC_DRAW);
  gl.enableVertexAttribArray(1);
  gl.vertexAttribPointer(1, 3, gl.FLOAT, false, 0, 0);

  const texBuf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, texBuf);
  gl.bufferData(gl.ARRAY_BUFFER, geometry.texCoords, gl.STATIC_DRAW);
  gl.enableVertexAttribArray(2);
  gl.vertexAttribPointer(2, 2, gl.FLOAT, false, 0, 0);

  const idxBuf = gl.createBuffer();
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, idxBuf);
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, geometry.indices, gl.STATIC_DRAW);

  gl.bindVertexArray(null);

  return {
    vao,
    indexCount: geometry.indices.length,
    modelMatrix: Mat4.create(),
    _transform: { position: [0, 0, 0], rotation: [0, 0, 0], scale: [1, 1, 1] },
    texture: null,
    solidColor: null,
    shininess: 32,
    specularStrength: 0.4,
    alpha: 1.0,
    animatedWater: false,

    getModelMatrix() {
      const m = Mat4.create();
      Mat4.translate(m, m, this._transform.position);
      Mat4.rotateY(m, m, this._transform.rotation[1]);
      Mat4.rotateX(m, m, this._transform.rotation[0]);
      Mat4.rotateZ(m, m, this._transform.rotation[2]);
      Mat4.scale(m, m, this._transform.scale);
      this.modelMatrix = m;
      return m;
    },

    setPosition(x, y, z) {
      this._transform.position = [x, y, z];
    },

    setRotation(x, y, z) {
      this._transform.rotation = [x, y, z];
    },

    setScale(x, y, z) {
      this._transform.scale = [x, y ?? x, z ?? x];
    },
  };
}
