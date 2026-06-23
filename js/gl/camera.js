/** Câmera em primeira pessoa com projeção perspectiva. */
class FirstPersonCamera {
  constructor() {
    this.position = Vec3.create(-10, 2.5, 6);
    this.yaw = 0.2;
    this.pitch = -0.3;
    this.speed = 6.0;
    this.mouseSensitivity = 0.002;
    this.fov = Math.PI / 3;
    this.near = 0.1;
    this.far = 300;
    this.view = Mat4.create();
    this.projection = Mat4.create();
    this.front = Vec3.create(0, 0, -1);
    this.right = Vec3.create(1, 0, 0);
    this.up = Vec3.create(0, 1, 0);
    this._updateVectors();
  }

  _updateVectors() {
    const cosPitch = Math.cos(this.pitch);
    this.front[0] = Math.cos(this.yaw) * cosPitch;
    this.front[1] = Math.sin(this.pitch);
    this.front[2] = Math.sin(this.yaw) * cosPitch;
    Vec3.normalize(this.front, this.front);

    const worldUp = Vec3.create(0, 1, 0);
    this.right[0] = this.front[2];
    this.right[1] = 0;
    this.right[2] = -this.front[0];
    Vec3.normalize(this.right, this.right);

    this.up[0] = worldUp[1] * this.front[2] - worldUp[2] * this.front[1];
    this.up[1] = worldUp[2] * this.front[0] - worldUp[0] * this.front[2];
    this.up[2] = worldUp[0] * this.front[1] - worldUp[1] * this.front[0];
    Vec3.normalize(this.up, this.up);
  }

  rotate(dx, dy) {
    this.yaw += dx * this.mouseSensitivity;
    this.pitch -= dy * this.mouseSensitivity;
    const limit = Math.PI / 2 - 0.05;
    this.pitch = Math.max(-limit, Math.min(limit, this.pitch));
    this._updateVectors();
  }

  move(forward, right, dt) {
    const dist = this.speed * dt;
    if (forward !== 0) {
      this.position[0] += this.front[0] * forward * dist;
      this.position[2] += this.front[2] * forward * dist;
    }
    if (right !== 0) {
      this.position[0] += this.right[0] * right * dist;
      this.position[2] += this.right[2] * right * dist;
    }
    this.position[1] = 1.7;
    this._clampBounds();
  }

  _clampBounds() {
    const minX = -35, maxX = 35;
    const minZ = -145, maxZ = 20;
    this.position[0] = Math.max(minX, Math.min(maxX, this.position[0]));
    this.position[2] = Math.max(minZ, Math.min(maxZ, this.position[2]));
  }

  getLookTarget() {
    return Vec3.create(
      this.position[0] + this.front[0],
      this.position[1] + this.front[1],
      this.position[2] + this.front[2],
    );
  }

  updateMatrices(aspect) {
    const center = this.getLookTarget();
    Mat4.lookAt(this.view, this.position, center, Vec3.create(0, 1, 0));
    Mat4.perspective(this.projection, this.fov, aspect, this.near, this.far);
  }
}
