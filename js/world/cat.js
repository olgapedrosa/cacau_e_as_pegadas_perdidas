/** Modelo procedural da gata Cacau com partes animáveis. */
class CatModel {
  constructor(gl, solidColor) {
    this.parts = [];
    this.basePosition = [0, 0, 0];
    this.time = 0;

    const body = createGLMesh(gl, Geometry.box(0.5, 0.35, 0.8));
    body.solidColor = solidColor || new Float32Array([0.55, 0.35, 0.2, 1]);
    body.shininess = 16;
    this.body = body;
    this.parts.push(body);

    const head = createGLMesh(gl, Geometry.sphere(0.22, 10, 8));
    head.solidColor = body.solidColor;
    head.setPosition(0, 0.3, 0.45);
    this.head = head;
    this.parts.push(head);

    const earL = createGLMesh(gl, Geometry.cone(0.08, 0.15, 6));
    earL.solidColor = body.solidColor;
    earL.setPosition(-0.12, 0.48, 0.42);
    this.earL = earL;
    this.parts.push(earL);

    const earR = createGLMesh(gl, Geometry.cone(0.08, 0.15, 6));
    earR.solidColor = body.solidColor;
    earR.setPosition(0.12, 0.48, 0.42);
    this.earR = earR;
    this.parts.push(earR);

    const tail = createGLMesh(gl, Geometry.cylinder(0.05, 0.6, 8));
    tail.solidColor = body.solidColor;
    tail.setPosition(0, 0.15, -0.5);
    tail.setRotation(0.8, 0, 0);
    this.tail = tail;
    this.parts.push(tail);

    const legFL = createGLMesh(gl, Geometry.cylinder(0.06, 0.25, 6));
    legFL.solidColor = body.solidColor;
    legFL.setPosition(-0.15, -0.25, 0.25);
    this.legFL = legFL;
    this.parts.push(legFL);

    const legFR = createGLMesh(gl, Geometry.cylinder(0.06, 0.25, 6));
    legFR.solidColor = body.solidColor;
    legFR.setPosition(0.15, -0.25, 0.25);
    this.legFR = legFR;
    this.parts.push(legFR);

    const legBL = createGLMesh(gl, Geometry.cylinder(0.06, 0.25, 6));
    legBL.solidColor = body.solidColor;
    legBL.setPosition(-0.15, -0.25, -0.25);
    this.legBL = legBL;
    this.parts.push(legBL);

    const legBR = createGLMesh(gl, Geometry.cylinder(0.06, 0.25, 6));
    legBR.solidColor = body.solidColor;
    legBR.setPosition(0.15, -0.25, -0.25);
    this.legBR = legBR;
    this.parts.push(legBR);
  }

  setPosition(x, y, z) {
    this.basePosition = [x, y, z];
    this.body.setPosition(x, y, z);
  }

  setRotation(y) {
    this.body.setRotation(0, y, 0);
  }

  update(dt, time) {
    this.time = time;
    const wag = Math.sin(time * 4) * 0.5;
    const headBob = Math.sin(time * 2) * 0.08;
    const walk = Math.sin(time * 3) * 0.15;

    const [bx, by, bz] = this.basePosition;
    const rotY = this.body._transform.rotation[1];

    this.head.setPosition(bx, by + 0.3 + headBob, bz + 0.45);
    this.earL.setPosition(bx - 0.12, by + 0.48 + headBob, bz + 0.42);
    this.earR.setPosition(bx + 0.12, by + 0.48 + headBob, bz + 0.42);

    this.tail.setPosition(bx, by + 0.15, bz - 0.5);
    this.tail.setRotation(0.8 + wag, rotY, wag * 0.3);

    this.legFL.setPosition(bx - 0.15, by - 0.25 + walk, bz + 0.25);
    this.legFR.setPosition(bx + 0.15, by - 0.25 - walk, bz + 0.25);
    this.legBL.setPosition(bx - 0.15, by - 0.25 - walk, bz - 0.25);
    this.legBR.setPosition(bx + 0.15, by - 0.25 + walk, bz - 0.25);
  }

  getMeshes() {
    const meshes = [this.body, this.head, this.earL, this.earR, this.tail,
      this.legFL, this.legFR, this.legBL, this.legBR];
    for (const m of meshes) {
      const parentRot = this.body._transform.rotation[1];
      if (m !== this.body) {
        m._transform.rotation[1] = parentRot;
      }
    }
    return meshes;
  }
}

/** Borboletas animadas no bosque. */
class ButterflySwarm {
  constructor(gl, center, count = 5) {
    this.butterflies = [];
    this.center = center;
    for (let i = 0; i < count; i++) {
      const mesh = createGLMesh(gl, Geometry.box(0.15, 0.02, 0.25));
      mesh.solidColor = new Float32Array([
        0.9 + Math.random() * 0.1,
        0.3 + Math.random() * 0.5,
        0.1 + Math.random() * 0.3,
        1,
      ]);
      mesh.phase = Math.random() * Math.PI * 2;
      mesh.orbitR = 1 + Math.random() * 2;
      mesh.speed = 0.5 + Math.random() * 0.8;
      mesh.height = 1.5 + Math.random() * 2;
      this.butterflies.push(mesh);
    }
  }

  update(time) {
    for (const b of this.butterflies) {
      const t = time * b.speed + b.phase;
      const x = this.center[0] + Math.cos(t) * b.orbitR;
      const z = this.center[2] + Math.sin(t) * b.orbitR;
      const y = this.center[1] + b.height + Math.sin(t * 2) * 0.5;
      b.setPosition(x, y, z);
      b.setRotation(0, t, Math.sin(t * 5) * 0.4);
    }
  }

  getMeshes() {
    return this.butterflies;
  }
}
