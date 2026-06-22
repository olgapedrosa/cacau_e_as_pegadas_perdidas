/** Captura de eventos de teclado e mouse. */
class Input {
  constructor(canvas) {
    this.canvas = canvas;
    this.keys = {};
    this.mouseLocked = false;
    this.moveForward = 0;
    this.moveRight = 0;

    window.addEventListener('keydown', (e) => {
      this.keys[e.code] = true;
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Space'].includes(e.code)) {
        e.preventDefault();
      }
    });
    window.addEventListener('keyup', (e) => { this.keys[e.code] = false; });

    canvas.addEventListener('click', () => {
      if (!this.mouseLocked) {
        canvas.requestPointerLock();
      }
    });

    document.addEventListener('pointerlockchange', () => {
      this.mouseLocked = document.pointerLockElement === canvas;
    });

    document.addEventListener('mousemove', (e) => {
      if (this.mouseLocked) {
        this.mouseDX = e.movementX || 0;
        this.mouseDY = e.movementY || 0;
      }
    });

    this.mouseDX = 0;
    this.mouseDY = 0;
  }

  update() {
    this.moveForward = 0;
    this.moveRight = 0;

    if (this.keys['KeyW'] || this.keys['ArrowUp']) this.moveForward += 1;
    if (this.keys['KeyS'] || this.keys['ArrowDown']) this.moveForward -= 1;
    if (this.keys['KeyA'] || this.keys['ArrowLeft']) this.moveRight -= 1;
    if (this.keys['KeyD'] || this.keys['ArrowRight']) this.moveRight += 1;
  }

  consumeMouse() {
    const dx = this.mouseDX;
    const dy = this.mouseDY;
    this.mouseDX = 0;
    this.mouseDY = 0;
    return { dx, dy };
  }
}
