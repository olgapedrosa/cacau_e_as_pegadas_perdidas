/** Sistema narrativo com textos e final da história. */
class Narrative {
  constructor() {
    this.overlay = document.getElementById('narrative-text');
    this.startScreen = document.getElementById('start-screen');
    this.endScreen = document.getElementById('end-screen');
    this.hint = document.getElementById('controls-hint');

    this.shownTriggers = new Set();
    this.currentMessage = '';
    this.messageTimer = 0;
    this.state = 'start';
    this.endingTimer = 0;
    this.frozen = false;

    this.cacauPos = Vec3.create(0, 0.35, -128);
    this.endingDistance = 4;
  }

  start() {
    this.state = 'playing';
    this.startScreen.classList.add('hidden');
    this.showMessage('Minha gata Cacau desapareceu esta manhã. Vou seguir suas pegadas.', 6);
    setTimeout(() => {
      this.hint.classList.add('visible');
      setTimeout(() => this.hint.classList.remove('visible'), 8000);
    }, 2000);
  }

  showMessage(text, duration = 4) {
    this.currentMessage = text;
    this.messageTimer = duration;
    this.overlay.textContent = text;
    this.overlay.classList.add('visible');
  }

  hideMessage() {
    this.overlay.classList.remove('visible');
    this.currentMessage = '';
  }

  update(dt, playerPos, triggers) {
    if (this.state === 'start' || this.state === 'ended') return;

    if (this.messageTimer > 0) {
      this.messageTimer -= dt;
      if (this.messageTimer <= 0) this.hideMessage();
    }

    if (this.state === 'playing') {
      for (const trigger of triggers) {
        if (trigger.once && this.shownTriggers.has(trigger.id)) continue;
        const dist = Vec3.distance(playerPos, Vec3.create(...trigger.pos));
        if (dist < trigger.radius) {
          this.showMessage(trigger.text, 5);
          if (trigger.once) this.shownTriggers.add(trigger.id);
        }
      }

      const distCacau = Vec3.distance(playerPos, this.cacauPos);
      if (distCacau < this.endingDistance) {
        this.state = 'ending';
        this.frozen = true;
        this.showMessage('Encontrei você, Cacau.', 5);
        this.endingTimer = 5;
      }
    }

    if (this.state === 'ending') {
      this.endingTimer -= dt;
      if (this.endingTimer <= 0) {
        this.state = 'ended';
        this.hideMessage();
        this.endScreen.classList.add('visible');
      }
    }
  }

  isFrozen() {
    return this.frozen;
  }

  getZoneName(z) {
    if (z > -5) return 'Quintal';
    if (z > -25) return 'Quintal';
    if (z > -45) return 'Jardim';
    if (z > -85) return 'Bosque';
    if (z > -110) return 'Lago';
    return 'Campo Aberto';
  }
}
