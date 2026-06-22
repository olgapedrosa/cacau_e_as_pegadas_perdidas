/** Ponto de entrada do passeio virtual 3D. */
(function main() {
  const canvas = document.getElementById('glcanvas');
  const zoneLabel = document.getElementById('zone-label');
  const startBtn = document.getElementById('start-btn');

  const renderer = new Renderer(canvas);
  const camera = new FirstPersonCamera();
  const input = new Input(canvas);
  const narrative = new Narrative();
  const scene = new Scene(renderer.gl);

  renderer.setSkyMesh(scene.getSkyMesh().vao);

  let lastTime = performance.now();

  function resize() {
    renderer.resize();
  }
  window.addEventListener('resize', resize);
  resize();

  startBtn.addEventListener('click', () => {
    canvas.requestPointerLock();
    narrative.start();
  });

  function frame(now) {
    const dt = Math.min((now - lastTime) / 1000, 0.05);
    lastTime = now;
    const time = now / 1000;

    input.update();

    if (!narrative.isFrozen()) {
      const { dx, dy } = input.consumeMouse();
      if (input.mouseLocked) camera.rotate(dx, dy);
      camera.move(input.moveForward, input.moveRight, dt);
    }

    const zone = scene.getZone(camera.position[2]);
    scene.update(dt, time, camera.position);
    narrative.update(dt, camera.position, scene.triggers);

    renderer.updateLight(time, zone);
    camera.updateMatrices(renderer.aspect);

    renderer.clear(zone);
    renderer.drawSky(camera.view, camera.projection, time);

    const meshes = scene.getAllMeshes(camera.position);
    for (const mesh of meshes) {
      renderer.drawMesh(mesh, camera.view, camera.projection, camera.position, time);
    }

    zoneLabel.textContent = narrative.getZoneName(camera.position[2]);
    requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
})();
