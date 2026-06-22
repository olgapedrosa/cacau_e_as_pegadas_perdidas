/** Álgebra linear para transformações 3D (WebGL puro). */
const Mat4 = {
  create() {
    return new Float32Array([
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1,
    ]);
  },

  identity(out) {
    out[0] = 1; out[1] = 0; out[2] = 0; out[3] = 0;
    out[4] = 0; out[5] = 1; out[6] = 0; out[7] = 0;
    out[8] = 0; out[9] = 0; out[10] = 1; out[11] = 0;
    out[12] = 0; out[13] = 0; out[14] = 0; out[15] = 1;
    return out;
  },

  multiply(out, a, b) {
    const a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
    const a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
    const a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
    const a30 = a[12], a31 = a[13], a32 = a[14], a33 = a[15];
    let b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3];
    out[0] = a00 * b0 + a10 * b1 + a20 * b2 + a30 * b3;
    out[1] = a01 * b0 + a11 * b1 + a21 * b2 + a31 * b3;
    out[2] = a02 * b0 + a12 * b1 + a22 * b2 + a32 * b3;
    out[3] = a03 * b0 + a13 * b1 + a23 * b2 + a33 * b3;
    b0 = b[4]; b1 = b[5]; b2 = b[6]; b3 = b[7];
    out[4] = a00 * b0 + a10 * b1 + a20 * b2 + a30 * b3;
    out[5] = a01 * b0 + a11 * b1 + a21 * b2 + a31 * b3;
    out[6] = a02 * b0 + a12 * b1 + a22 * b2 + a32 * b3;
    out[7] = a03 * b0 + a13 * b1 + a23 * b2 + a33 * b3;
    b0 = b[8]; b1 = b[9]; b2 = b[10]; b3 = b[11];
    out[8] = a00 * b0 + a10 * b1 + a20 * b2 + a30 * b3;
    out[9] = a01 * b0 + a11 * b1 + a21 * b2 + a31 * b3;
    out[10] = a02 * b0 + a12 * b1 + a22 * b2 + a32 * b3;
    out[11] = a03 * b0 + a13 * b1 + a23 * b2 + a33 * b3;
    b0 = b[12]; b1 = b[13]; b2 = b[14]; b3 = b[15];
    out[12] = a00 * b0 + a10 * b1 + a20 * b2 + a30 * b3;
    out[13] = a01 * b0 + a11 * b1 + a21 * b2 + a31 * b3;
    out[14] = a02 * b0 + a12 * b1 + a22 * b2 + a32 * b3;
    out[15] = a03 * b0 + a13 * b1 + a23 * b2 + a33 * b3;
    return out;
  },

  perspective(out, fov, aspect, near, far) {
    const f = 1.0 / Math.tan(fov / 2);
    out[0] = f / aspect; out[1] = 0; out[2] = 0; out[3] = 0;
    out[4] = 0; out[5] = f; out[6] = 0; out[7] = 0;
    out[8] = 0; out[9] = 0; out[11] = -1;
    out[10] = (far + near) / (near - far);
    out[12] = 0; out[13] = 0; out[14] = (2 * far * near) / (near - far);
    out[15] = 0;
    return out;
  },

  lookAt(out, eye, center, up) {
    let zx = eye[0] - center[0], zy = eye[1] - center[1], zz = eye[2] - center[2];
    let len = Math.hypot(zx, zy, zz);
    if (len === 0) { zz = 1; } else { zx /= len; zy /= len; zz /= len; }
    let xx = up[1] * zz - up[2] * zy;
    let xy = up[2] * zx - up[0] * zz;
    let xz = up[0] * zy - up[1] * zx;
    len = Math.hypot(xx, xy, xz);
    if (len !== 0) { xx /= len; xy /= len; xz /= len; }
    const yx = zy * xz - zz * xy;
    const yy = zz * xx - zx * xz;
    const yz = zx * xy - zy * xx;
    out[0] = xx; out[1] = yx; out[2] = zx; out[3] = 0;
    out[4] = xy; out[5] = yy; out[6] = zy; out[7] = 0;
    out[8] = xz; out[9] = yz; out[10] = zz; out[11] = 0;
    out[12] = -(xx * eye[0] + xy * eye[1] + xz * eye[2]);
    out[13] = -(yx * eye[0] + yy * eye[1] + yz * eye[2]);
    out[14] = -(zx * eye[0] + zy * eye[1] + zz * eye[2]);
    out[15] = 1;
    return out;
  },

  translate(out, a, v) {
    const x = v[0], y = v[1], z = v[2];
    if (a === out) {
      out[12] = a[0] * x + a[4] * y + a[8] * z + a[12];
      out[13] = a[1] * x + a[5] * y + a[9] * z + a[13];
      out[14] = a[2] * x + a[6] * y + a[10] * z + a[14];
      out[15] = a[3] * x + a[7] * y + a[11] * z + a[15];
    } else {
      const a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
      const a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
      const a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
      out[0] = a00; out[1] = a01; out[2] = a02; out[3] = a03;
      out[4] = a10; out[5] = a11; out[6] = a12; out[7] = a13;
      out[8] = a20; out[9] = a21; out[10] = a22; out[11] = a23;
      out[12] = a00 * x + a10 * y + a20 * z + a[12];
      out[13] = a01 * x + a11 * y + a21 * z + a[13];
      out[14] = a02 * x + a12 * y + a22 * z + a[14];
      out[15] = a03 * x + a13 * y + a23 * z + a[15];
    }
    return out;
  },

  rotateY(out, a, rad) {
    const s = Math.sin(rad), c = Math.cos(rad);
    const a00 = a[0], a02 = a[2], a10 = a[4], a12 = a[6];
    const a20 = a[8], a22 = a[10], a30 = a[12], a32 = a[14];
    out[0] = a00 * c + a20 * s; out[2] = a02 * c + a22 * s;
    out[4] = a10 * c + a12 * s; out[6] = a10 * -s + a12 * c;
    out[8] = a20 * c - a00 * s; out[10] = a22 * c - a02 * s;
    out[12] = a30 * c + a32 * s; out[14] = a32 * c - a30 * s;
    out[1] = a[1]; out[3] = a[3]; out[5] = a[5]; out[7] = a[7];
    out[9] = a[9]; out[11] = a[11]; out[13] = a[13]; out[15] = a[15];
    return out;
  },

  rotateX(out, a, rad) {
    const s = Math.sin(rad), c = Math.cos(rad);
    const a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
    const a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
    out[4] = a10 * c + a20 * s; out[5] = a11 * c + a21 * s;
    out[6] = a12 * c + a22 * s; out[7] = a13 * c + a23 * s;
    out[8] = a20 * c - a10 * s; out[9] = a21 * c - a11 * s;
    out[10] = a22 * c - a12 * s; out[11] = a23 * c - a13 * s;
    out[0] = a[0]; out[1] = a[1]; out[2] = a[2]; out[3] = a[3];
    out[12] = a[12]; out[13] = a[13]; out[14] = a[14]; out[15] = a[15];
    return out;
  },

  rotateZ(out, a, rad) {
    const s = Math.sin(rad), c = Math.cos(rad);
    const a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
    const a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
    out[0] = a00 * c + a10 * s; out[1] = a01 * c + a11 * s;
    out[2] = a02 * c + a12 * s; out[3] = a03 * c + a13 * s;
    out[4] = a10 * c - a00 * s; out[5] = a11 * c - a01 * s;
    out[6] = a12 * c - a02 * s; out[7] = a13 * c - a03 * s;
    out[8] = a[8]; out[9] = a[9]; out[10] = a[10]; out[11] = a[11];
    out[12] = a[12]; out[13] = a[13]; out[14] = a[14]; out[15] = a[15];
    return out;
  },

  scale(out, a, v) {
    const x = v[0], y = v[1], z = v[2];
    out[0] = a[0] * x; out[1] = a[1] * x; out[2] = a[2] * x; out[3] = a[3] * x;
    out[4] = a[4] * y; out[5] = a[5] * y; out[6] = a[6] * y; out[7] = a[7] * y;
    out[8] = a[8] * z; out[9] = a[9] * z; out[10] = a[10] * z; out[11] = a[11] * z;
    out[12] = a[12]; out[13] = a[13]; out[14] = a[14]; out[15] = a[15];
    return out;
  },

  invert(out, a) {
    const a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
    const a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
    const a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
    const a30 = a[12], a31 = a[13], a32 = a[14], a33 = a[15];
    const b00 = a00 * a11 - a01 * a10;
    const b01 = a00 * a12 - a02 * a10;
    const b02 = a00 * a13 - a03 * a10;
    const b03 = a01 * a12 - a02 * a11;
    const b04 = a01 * a13 - a03 * a11;
    const b05 = a02 * a13 - a03 * a12;
    const b06 = a20 * a31 - a21 * a30;
    const b07 = a20 * a32 - a22 * a30;
    const b08 = a20 * a33 - a23 * a30;
    const b09 = a21 * a32 - a22 * a31;
    const b10 = a21 * a33 - a23 * a31;
    const b11 = a22 * a33 - a23 * a32;
    let det = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06;
    if (!det) return null;
    det = 1.0 / det;
    out[0] = (a11 * b11 - a12 * b10 + a13 * b09) * det;
    out[1] = (a02 * b10 - a01 * b11 - a03 * b09) * det;
    out[2] = (a31 * b05 - a32 * b04 + a33 * b03) * det;
    out[3] = (a22 * b04 - a21 * b05 - a23 * b03) * det;
    out[4] = (a12 * b08 - a10 * b11 - a13 * b07) * det;
    out[5] = (a00 * b11 - a02 * b08 + a03 * b07) * det;
    out[6] = (a32 * b02 - a30 * b05 - a33 * b01) * det;
    out[7] = (a20 * b05 - a22 * b02 + a23 * b01) * det;
    out[8] = (a10 * b10 - a11 * b08 + a13 * b06) * det;
    out[9] = (a01 * b08 - a00 * b10 - a03 * b06) * det;
    out[10] = (a30 * b04 - a31 * b02 + a33 * b00) * det;
    out[11] = (a21 * b02 - a20 * b04 - a23 * b00) * det;
    out[12] = (a11 * b07 - a10 * b09 - a12 * b06) * det;
    out[13] = (a00 * b09 - a01 * b07 + a02 * b06) * det;
    out[14] = (a31 * b01 - a30 * b03 - a32 * b00) * det;
    out[15] = (a20 * b03 - a21 * b01 + a22 * b00) * det;
    return out;
  },

  transpose(out, a) {
    out[0] = a[0]; out[1] = a[4]; out[2] = a[8]; out[3] = a[12];
    out[4] = a[1]; out[5] = a[5]; out[6] = a[9]; out[7] = a[13];
    out[8] = a[2]; out[9] = a[6]; out[10] = a[10]; out[11] = a[14];
    out[12] = a[3]; out[13] = a[7]; out[14] = a[11]; out[15] = a[15];
    return out;
  },
};

const Vec3 = {
  create(x = 0, y = 0, z = 0) {
    return new Float32Array([x, y, z]);
  },

  subtract(out, a, b) {
    out[0] = a[0] - b[0];
    out[1] = a[1] - b[1];
    out[2] = a[2] - b[2];
    return out;
  },

  normalize(out, a) {
    const len = Math.hypot(a[0], a[1], a[2]);
    if (len > 0.00001) {
      out[0] = a[0] / len;
      out[1] = a[1] / len;
      out[2] = a[2] / len;
    }
    return out;
  },

  distance(a, b) {
    const dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
    return Math.hypot(dx, dy, dz);
  },

  transformMat4(out, a, m) {
    const x = a[0], y = a[1], z = a[2];
    const w = m[3] * x + m[7] * y + m[11] * z + m[15] || 1.0;
    out[0] = (m[0] * x + m[4] * y + m[8] * z + m[12]) / w;
    out[1] = (m[1] * x + m[5] * y + m[9] * z + m[13]) / w;
    out[2] = (m[2] * x + m[6] * y + m[10] * z + m[14]) / w;
    return out;
  },
};
