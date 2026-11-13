
document.addEventListener('DOMContentLoaded', () => {

    const canvas = document.getElementById('canvas-matrix');

    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    const LARANJA = '#FF6D00';
    const LARANJA_RGB = '255, 109, 0';

    // =====================================
    // CONFIGURAÇÃO DO CANVAS
    // =====================================

    function resize() {
        canvas.width = canvas.parentElement.offsetWidth;
        canvas.height = canvas.parentElement.offsetHeight;
    }

    resize();

    window.addEventListener('resize', resize);

    // =====================================
    // PARTÍCULAS DE BRASAS
    // =====================================

    class Ember {

        constructor() {
            this.reset();
        }

        reset() {

            this.x = Math.random() * canvas.width;

            this.y = canvas.height * (0.65 + Math.random() * 0.3);

            this.radius = Math.random() * 2.5 + 1;

            this.vx = (Math.random() - 0.5) * 0.5;

            this.vy = -(Math.random() * 1 + 0.4);

            this.alpha = Math.random() * 0.6 + 0.3;

            this.life = 1;

            this.decay = Math.random() * 0.004 + 0.002;

        }

        update() {

            this.x += this.vx;

            this.y += this.vy;

            this.life -= this.decay;

            this.alpha = this.life;

            if (this.life <= 0 || this.y < 0) {

                this.reset();

                this.y = canvas.height + 10;

            }

        }

        draw() {

            ctx.beginPath();

            ctx.arc(
                this.x,
                this.y,
                this.radius,
                0,
                Math.PI * 2
            );

            ctx.fillStyle =
                `rgba(${LARANJA_RGB}, ${this.alpha})`;

            ctx.shadowBlur = 15;

            ctx.shadowColor = LARANJA;

            ctx.fill();

            ctx.shadowBlur = 0;

        }

    }

    // =====================================
    // FUMAÇA DO FORNO
    // =====================================

    class Smoke {

        constructor() {
            this.reset();
        }

        reset() {

            this.x = canvas.width * 0.5 +
                (Math.random() - 0.5) * 180;

            this.y = canvas.height * 0.78;

            this.radius = Math.random() * 15 + 8;

            this.vx = (Math.random() - 0.5) * 0.7;

            this.vy = -Math.random() * 0.9 - 0.3;

            this.alpha = Math.random() * 0.10 + 0.03;

        }

        update() {

            this.x += this.vx;

            this.y += this.vy;

            this.radius += 0.15;

            this.alpha -= 0.0007;

            if (this.alpha <= 0 || this.y < 0) {

                this.reset();

            }

        }

        draw() {

            const gradient = ctx.createRadialGradient(
                this.x,
                this.y,
                0,
                this.x,
                this.y,
                this.radius
            );

            gradient.addColorStop(
                0,
                `rgba(${LARANJA_RGB}, ${this.alpha})`
            );

            gradient.addColorStop(
                1,
                `rgba(${LARANJA_RGB}, 0)`
            );

            ctx.beginPath();

            ctx.fillStyle = gradient;

            ctx.arc(
                this.x,
                this.y,
                this.radius,
                0,
                Math.PI * 2
            );

            ctx.fill();

        }

    }

    // =====================================
    // ILUMINAÇÃO DO FORNO
    // =====================================

    class FireLight {

        constructor() {
            this.reset();
        }

        reset() {

            this.x = canvas.width * 0.5 +
                (Math.random() - 0.5) * 280;

            this.y = canvas.height * 0.85;

            this.radius = Math.random() * 40 + 20;

            this.alpha = Math.random() * 0.25 + 0.1;

            this.speed = Math.random() * 0.02 + 0.01;

        }

        update() {

            this.y -= this.speed * 15;

            this.radius += 0.3;

            this.alpha -= 0.003;

            if (this.alpha <= 0) {

                this.reset();

            }

        }

        draw() {

            const gradient = ctx.createRadialGradient(
                this.x,
                this.y,
                0,
                this.x,
                this.y,
                this.radius
            );

            gradient.addColorStop(
                0,
                `rgba(${LARANJA_RGB}, ${this.alpha})`
            );

            gradient.addColorStop(
                0.4,
                `rgba(${LARANJA_RGB}, ${this.alpha * 0.6})`
            );

            gradient.addColorStop(
                1,
                `rgba(${LARANJA_RGB}, 0)`
            );

            ctx.fillStyle = gradient;

            ctx.beginPath();

            ctx.arc(
                this.x,
                this.y,
                this.radius,
                0,
                Math.PI * 2
            );

            ctx.fill();

        }

    }

    // =====================================
    // EXPLOSÃO INICIAL (APENAS UMA VEZ)
    // =====================================

    const particulasExplosao = [];

    function explosaoInicial() {

        const centroX = canvas.width * 0.5;

        const centroY = canvas.height * 0.82;

        for (let i = 0; i < 35; i++) {

            const angulo = Math.random() * Math.PI * 2;

            const velocidade = Math.random() * 4 + 2;

            const particula = {

                x: centroX,

                y: centroY,

                vx: Math.cos(angulo) * velocidade,

                vy: Math.sin(angulo) * velocidade,

                alpha: 1,

                radius: Math.random() * 3 + 1

            };

            particulasExplosao.push(particula);

        }

    }

    explosaoInicial();

    // =====================================
    // LUZ PULSANTE CONTÍNUA
    // =====================================

    function luzPulsante() {

        const pulsacao = 0.5 + Math.sin(
            performance.now() * 0.002
        ) * 0.5;

        const centroX = canvas.width * 0.5;

        const centroY = canvas.height * 0.82;

        const gradient = ctx.createRadialGradient(
            centroX,
            centroY,
            5,
            centroX,
            centroY,
            320
        );

        gradient.addColorStop(
            0,
            `rgba(${LARANJA_RGB}, ${0.10 + pulsacao * 0.20})`
        );

        gradient.addColorStop(
            0.5,
            `rgba(${LARANJA_RGB}, ${0.04 + pulsacao * 0.08})`
        );

        gradient.addColorStop(
            1,
            'rgba(255, 109, 0, 0)'
        );

        ctx.fillStyle = gradient;

        ctx.fillRect(
            0,
            0,
            canvas.width,
            canvas.height
        );

    }

    // =====================================
    // CRIAÇÃO DAS PARTÍCULAS
    // =====================================

    const brasas = Array.from(
        { length: 65 },
        () => new Ember()
    );

    const fumacas = Array.from(
        { length: 20 },
        () => new Smoke()
    );

    const luzes = Array.from(
        { length: 15 },
        () => new FireLight()
    );

    // =====================================
    // ANIMAÇÃO PRINCIPAL
    // =====================================

    function animate() {

        ctx.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );

        // Luz pulsante

        luzPulsante();

        // Explosão inicial de partículas

        for (
            let i = particulasExplosao.length - 1;
            i >= 0;
            i--
        ) {

            const p = particulasExplosao[i];

            p.x += p.vx;

            p.y += p.vy;

            p.vx *= 0.97;

            p.vy *= 0.97;

            p.alpha -= 0.015;

            ctx.beginPath();

            ctx.arc(
                p.x,
                p.y,
                p.radius,
                0,
                Math.PI * 2
            );

            ctx.fillStyle =
                `rgba(${LARANJA_RGB}, ${Math.max(0, p.alpha)})`;

            ctx.shadowBlur = 15;

            ctx.shadowColor = LARANJA;

            ctx.fill();

            ctx.shadowBlur = 0;

            if (p.alpha <= 0) {

                particulasExplosao.splice(i, 1);

            }

        }

        // Fumaça

        fumacas.forEach(fumaca => {

            fumaca.update();

            fumaca.draw();

        });

        // Iluminação do forno

        luzes.forEach(luz => {

            luz.update();

            luz.draw();

        });

        // Brasas flutuantes

        brasas.forEach(brasa => {

            brasa.update();

            brasa.draw();

        });

        requestAnimationFrame(animate);

    }

    animate();

});
