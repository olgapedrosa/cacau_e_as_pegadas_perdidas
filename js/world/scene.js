/** Construção manual da cena completa com todas as áreas narrativas. */
class Scene {
  constructor(gl) {
    this.gl = gl;
    this.meshes = [];
    this.animated = [];
    this.triggers = [];
    this.pawPrints = [];
    this.textures = {
      grass: Textures.grass(gl),
      wood: Textures.wood(gl),
      stone: Textures.stone(gl),
      brick: Textures.brick(gl),
      water: Textures.water(gl),
      dirt: Textures.dirt(gl),
    };

    this._buildGround();
    this._buildQuintal();
    this._buildJardim();
    this._buildBosque();
    this._buildLago();
    this._buildCampoFinal();
    this._buildPawPrintTrail();
    this._buildSky();

    this.cacau = new CatModel(gl, new Float32Array([0.6, 0.38, 0.22, 1]));
    this.cacau.setPosition(0, 0.35, -128);
    this.animated.push({ update: (dt, t) => this.cacau.update(dt, t), getMeshes: () => this.cacau.getMeshes() });

    this.silhouette = new CatModel(gl, new Float32Array([0.15, 0.12, 0.1, 0.7]));
    this.silhouettePos = [-8, 0.35, -62];
    this.silhouette.setPosition(...this.silhouettePos);
    this.silhouetteVisible = true;
    this.silhouetteMeshes = this.silhouette.getMeshes();
    for (const m of this.silhouetteMeshes) m.alpha = 0.6;

    this.butterflies = new ButterflySwarm(gl, [-5, 1, -55], 6);
    this.animated.push(this.butterflies);
  }

  _add(mesh) {
    this.meshes.push(mesh);
    return mesh;
  }

  _texBox(w, h, d, tex, x, y, z, ry = 0) {
    const m = createGLMesh(this.gl, Geometry.box(w, h, d));
    m.texture = tex;
    m.setPosition(x, y, z);
    m.setRotation(0, ry, 0);
    return this._add(m);
  }

  _solidBox(w, h, d, color, x, y, z, ry = 0) {
    const m = createGLMesh(this.gl, Geometry.box(w, h, d));
    m.solidColor = new Float32Array([...color, 1]);
    m.setPosition(x, y, z);
    m.setRotation(0, ry, 0);
    return this._add(m);
  }

  _tree(x, z, scale = 1) {
    const trunk = this._texBox(0.5 * scale, 2.5 * scale, 0.5 * scale, this.textures.wood, x, 1.25 * scale, z);
    const foliage = createGLMesh(this.gl, Geometry.cone(1.8 * scale, 3.5 * scale, 10));
    foliage.texture = this.textures.grass;
    foliage.setPosition(x, 2.5 * scale + 1.5 * scale, z);
    this._add(foliage);
    return trunk;
  }

  _fence(x, z, length, alongX = true) {
    const postCount = Math.floor(length / 2) + 1;
    for (let i = 0; i < postCount; i++) {
      const px = alongX ? x + i * 2 : x;
      const pz = alongX ? z : z + i * 2;
      this._solidBox(0.15, 1.2, 0.15, [0.45, 0.28, 0.12], px, 0.6, pz);
      if (i < postCount - 1) {
        const rx = alongX ? px + 1 : px;
        const rz = alongX ? pz : pz + 1;
        this._solidBox(alongX ? 2 : 0.1, 0.08, alongX ? 0.1 : 2, [0.5, 0.32, 0.14], rx, 0.9, rz);
      }
    }
  }

  _buildGround() {
    const zones = [
      { z: 5, w: 30, d: 25, tex: this.textures.grass },
      { z: -15, w: 30, d: 25, tex: this.textures.grass },
      { z: -35, w: 30, d: 25, tex: this.textures.grass },
      { z: -55, w: 35, d: 30, tex: this.textures.dirt },
      { z: -75, w: 35, d: 30, tex: this.textures.dirt },
      { z: -95, w: 35, d: 25, tex: this.textures.dirt },
      { z: -120, w: 40, d: 35, tex: this.textures.grass },
    ];
    for (const zone of zones) {
      const ground = createGLMesh(this.gl, Geometry.plane(zone.w, zone.d));
      ground.texture = zone.tex;
      ground.setPosition(0, 0, zone.z);
      ground.shininess = 8;
      this._add(ground);
    }
  }

  _buildQuintal() {
    this._texBox(8, 4, 6, this.textures.brick, -6, 2, 2);
    this._texBox(8, 0.3, 6.2, this.textures.wood, -6, 4.15, 2);
    this._texBox(1.5, 2.5, 0.15, this.textures.wood, -2.2, 1.25, 4.8);

    this._tree(5, 0, 0.9);
    this._tree(-3, -3, 1.1);
    this._tree(8, -5, 0.8);

    this._fence(-12, -8, 24, true);
    this._fence(-12, 8, 24, true);
    this._fence(-12, -8, 16, false);
    this._fence(12, -8, 16, false);

    const gateL = this._solidBox(0.15, 1.5, 1.5, [0.4, 0.25, 0.1], 0.5, 0.75, -8);
    const gateR = this._solidBox(0.15, 1.5, 1.5, [0.4, 0.25, 0.1], -0.5, 0.75, -8);
    gateL.setRotation(0, -0.8, 0);
    gateR.setRotation(0, 0.8, 0);

    const toy = createGLMesh(this.gl, Geometry.sphere(0.25, 8, 6));
    toy.solidColor = new Float32Array([0.9, 0.2, 0.2, 1]);
    toy.setPosition(3, 0.25, -2);
    this._add(toy);

    const toyStick = this._solidBox(0.05, 0.6, 0.05, [0.6, 0.5, 0.3], 3, 0.3, -2);
    toyStick.setRotation(0.3, 0, 0.2);

    this.triggers.push({
      pos: [3, 0, -2], radius: 3,
      text: 'O brinquedo favorito da Cacau ainda está aqui...',
      once: true, id: 'toy',
    });
  }

  _buildJardim() {
    const bowl = createGLMesh(this.gl, Geometry.cylinder(0.35, 0.15, 12));
    bowl.solidColor = new Float32Array([0.7, 0.15, 0.1, 1]);
    bowl.setPosition(-4, 0.08, -28);
    bowl.setRotation(0.15, 0, 0.3);
    this._add(bowl);

    const yarn = createGLMesh(this.gl, Geometry.sphere(0.3, 10, 8));
    yarn.solidColor = new Float32Array([0.85, 0.75, 0.5, 1]);
    yarn.setPosition(5, 0.3, -32);
    this._add(yarn);

    const scratchBase = this._solidBox(0.4, 0.6, 0.4, [0.35, 0.22, 0.1], -2, 0.3, -38);
    const scratchPost = this._texBox(0.25, 1.2, 0.25, this.textures.wood, -2, 1.1, -38);

    this._tree(8, -25, 1);
    this._tree(-7, -30, 0.9);
    this._solidBox(1.5, 0.4, 0.6, [0.5, 0.35, 0.2], 6, 0.2, -35);

    this.triggers.push({
      pos: [-4, 0, -28], radius: 3,
      text: 'O pote de ração foi derrubado... ela estava com fome.',
      once: true, id: 'bowl',
    });
    this.triggers.push({
      pos: [5, 0, -32], radius: 3,
      text: 'Ela sempre brincava aqui.',
      once: true, id: 'yarn',
    });
    this.triggers.push({
      pos: [-2, 0, -38], radius: 3,
      text: 'As marcas no arranhador são recentes.',
      once: true, id: 'scratch',
    });
  }

  _buildBosque() {
    const treePositions = [
      [-10,-55], [-6,-58], [-12,-62], [8,-54], [12,-60], [6,-65],
      [-8,-68], [10,-70], [-14,-72], [4,-75], [-5,-78], [9,-80],
      [-11,-58], [7,-63], [-3,-70], [11,-76],
    ];
    for (const [x, z] of treePositions) {
      this._tree(x, z, 1.2 + Math.random() * 0.5);
    }

    this.triggers.push({
      pos: [-8, 0, -62], radius: 8,
      text: 'Algo se move entre as árvores...',
      once: true, id: 'silhouette_hint',
    });
  }

  _buildLago() {
    const water = createGLMesh(this.gl, Geometry.plane(18, 12));
    water.texture = this.textures.water;
    water.animatedWater = true;
    water.shininess = 128;
    water.specularStrength = 0.8;
    water.setPosition(0, 0.05, -92);
    this._add(water);

    const rocks = [[-6,-88], [5,-90], [-3,-96], [7,-94], [-8,-95], [4,-87]];
    for (const [x, z] of rocks) {
      const r = createGLMesh(this.gl, Geometry.sphere(0.6 + Math.random() * 0.4, 8, 6));
      r.texture = this.textures.stone;
      r.setPosition(x, 0.3, z);
      r.setScale(1, 0.6, 1);
      this._add(r);
    }

    this._tree(-12, -88, 0.8);
    this._tree(12, -96, 0.9);
    this._tree(-10, -98, 0.7);

    this.triggers.push({
      pos: [0, 0, -92], radius: 6,
      text: 'As pegadas levam até aqui... estou perto.',
      once: true, id: 'lake',
    });
  }

  _buildCampoFinal() {
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      const x = Math.cos(angle) * 15;
      const z = -125 + Math.sin(angle) * 8;
      this._tree(x, z, 1.3);
    }

    this._solidBox(2, 0.15, 0.6, [0.45, 0.3, 0.15], 4, 0.08, -122);
    this._solidBox(0.15, 1.5, 0.15, [0.4, 0.25, 0.1], 8, 0.75, -118);
    this._solidBox(0.15, 1.5, 0.15, [0.4, 0.25, 0.1], -8, 0.75, -118);
  }

  _buildPawPrintTrail() {
    const path = [
      [0, 4], [0.3, 0], [0, -4], [-0.2, -8], [0.3, -12], [0, -16],
      [0.2, -20], [-0.3, -24], [0, -28], [0.4, -32], [-0.2, -36],
      [0, -40], [0.3, -44], [-0.3, -48], [0, -52], [0.2, -56],
      [-0.4, -60], [0, -64], [0.3, -68], [-0.2, -72], [0, -76],
      [0.2, -80], [-0.3, -84], [0, -88], [0, -92], [0.2, -96],
      [-0.2, -100], [0, -104], [0.3, -108], [0, -112], [0, -116],
      [0, -120], [0, -124],
    ];
    for (let i = 0; i < path.length; i++) {
      const [x, z] = path[i];
      const paw = createGLMesh(this.gl, Geometry.pawPrint());
      paw.solidColor = new Float32Array([0.35, 0.25, 0.18, 1]);
      paw.setPosition(x, 0.03, z);
      paw.setRotation(0, (i % 2 === 0 ? 0.1 : -0.1), 0);
      paw.setScale(1.2, 0.3, 1.2);
      paw.shininess = 4;
      this._add(paw);
      this.pawPrints.push(paw);
    }
  }

  _buildSky() {
    this.skyMesh = createGLMesh(this.gl, Geometry.skybox());
  }

  getZone(z) {
    if (z > -5) return 0;
    if (z > -25) return 0;
    if (z > -45) return 1;
    if (z > -85) return 2;
    if (z > -110) return 3;
    return 4;
  }

  update(dt, time, playerPos) {
    for (const anim of this.animated) {
      anim.update(dt, time);
    }

    if (this.silhouetteVisible) {
      const dist = Vec3.distance(playerPos, Vec3.create(...this.silhouettePos));
      if (dist < 6) {
        this.silhouetteVisible = false;
      } else {
        this.silhouette.setPosition(
          this.silhouettePos[0] + Math.sin(time) * 0.5,
          this.silhouettePos[1],
          this.silhouettePos[2] + Math.cos(time * 0.7) * 0.5,
        );
        this.silhouette.update(dt, time);
      }
    }
  }

  getAllMeshes(playerPos) {
    const all = [...this.meshes];
    for (const anim of this.animated) {
      all.push(...anim.getMeshes());
    }
    if (this.silhouetteVisible) {
      all.push(...this.silhouetteMeshes);
    }
    return all.sort((a, b) => {
      const da = Vec3.distance(playerPos, a._transform.position);
      const db = Vec3.distance(playerPos, b._transform.position);
      return db - da;
    });
  }

  getSkyMesh() {
    return this.skyMesh;
  }
}
