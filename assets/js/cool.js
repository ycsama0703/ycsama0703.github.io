(function () {
  // ---------- Particle / starfield canvas ----------
  const canvas = document.createElement("canvas");
  canvas.id = "cool-canvas";
  document.body.appendChild(canvas);
  const ctx = canvas.getContext("2d");

  let w, h, particles;
  const PARTICLE_COUNT = 70;
  const LINK_DIST = 130;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }
  window.addEventListener("resize", resize);
  resize();

  function rand(min, max) {
    return Math.random() * (max - min) + min;
  }

  function initParticles() {
    particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: rand(0, w),
        y: rand(0, h),
        vx: rand(-0.25, 0.25),
        vy: rand(-0.25, 0.25),
        r: rand(0.6, 1.8),
      });
    }
  }
  initParticles();

  const mouse = { x: -9999, y: -9999 };
  window.addEventListener("mousemove", (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  function step() {
    ctx.clearRect(0, 0, w, h);

    for (const p of particles) {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > w) p.vx *= -1;
      if (p.y < 0 || p.y > h) p.vy *= -1;

      // mouse repel
      const dx = p.x - mouse.x;
      const dy = p.y - mouse.y;
      const d2 = dx * dx + dy * dy;
      if (d2 < 120 * 120) {
        const d = Math.sqrt(d2) || 1;
        p.x += (dx / d) * 0.6;
        p.y += (dy / d) * 0.6;
      }

      // pixel-style square particle
      const s = Math.max(2, Math.round(p.r * 1.6));
      ctx.fillStyle = "rgba(255, 200, 110, 0.9)";
      ctx.fillRect(Math.round(p.x), Math.round(p.y), s, s);
    }

    // link nearby particles
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const a = particles[i], b = particles[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < LINK_DIST) {
          ctx.strokeStyle = `rgba(255, 200, 110, ${0.22 * (1 - d / LINK_DIST)})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(step);
  }
  step();

})();
