document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('canvas-matrix');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = canvas.parentElement.offsetWidth;
        canvas.height = canvas.parentElement.offsetHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Partículas de poeira solar flutuantes
    class SunDust {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.radius = Math.random() * 2 + 0.6;
            this.vx = (Math.random() - 0.5) * 0.3;
            this.vy = -Math.random() * 0.4 - 0.1; // Flutua suavemente para cima
            this.alpha = Math.random() * 0.5 + 0.2;
            this.fadeSpeed = Math.random() * 0.004 + 0.002;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.alpha -= this.fadeSpeed;

            if (this.alpha <= 0 || this.y < 0) {
                this.reset();
                this.y = canvas.height + 10;
            }
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 240, 210, ${this.alpha})`;
            ctx.shadowBlur = 6;
            ctx.shadowColor = 'rgba(255, 255, 255, 0.7)';
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    // Luzes emergindo do ponto de fuga no centro do corredor
    class CorridorLight {
        constructor() {
            this.reset();
        }

        reset() {
            this.progress = Math.random();
            this.speed = Math.random() * 0.003 + 0.001;
            this.angle = Math.random() * Math.PI * 2;
        }

        update() {
            this.progress += this.speed;
            if (this.progress >= 1) {
                this.reset();
                this.progress = 0;
            }
        }

        draw() {
            // Ponto de fuga central alinhado com o fundo do corredor da foto
            const centerX = canvas.width * 0.5;
            const centerY = canvas.height * 0.52;

            const maxDist = Math.max(canvas.width, canvas.height);
            const currentDist = this.progress * maxDist;

            const x = centerX + Math.cos(this.angle) * currentDist;
            const y = centerY + Math.sin(this.angle) * currentDist;

            const alpha = Math.sin(this.progress * Math.PI) * 0.35;

            ctx.beginPath();
            ctx.arc(x, y, this.progress * 3.5, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(100, 181, 246, ${alpha})`;
            ctx.fill();
        }
    }

    const dustParticles = Array.from({ length: 40 }, () => new SunDust());
    const corridorLights = Array.from({ length: 25 }, () => new CorridorLight());

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Brilho suave no centro do corredor (ponto de fuga)
        const centerX = canvas.width * 0.5;
        const centerY = canvas.height * 0.52;
        const gradient = ctx.createRadialGradient(
            centerX, centerY, 5,
            centerX, centerY, 220
        );
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.25)');
        gradient.addColorStop(0.4, 'rgba(100, 181, 246, 0.08)');
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Animar pontos de iluminação em perspectiva
        corridorLights.forEach(light => {
            light.update();
            light.draw();
        });

        // Animar poeira de luz
        dustParticles.forEach(dust => {
            dust.update();
            dust.draw();
        });

        requestAnimationFrame(animate);
    }

    animate();
});