"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

export function ParticleStorm() {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        // --- Configuration ---
        const CONFIG = {
            particleCount: 2500,
            minSize: 0.3,
            maxSize: 1.2,
            minOpacity: 0.3,
            maxOpacity: 1.0,
            baseDrift: 0.012,
            cursorInfluence: 0.15, // Reduced from 0.25 for less intensity
            fieldSize: 35,
            zDepth: 25,
        };

        // --- Create circular dot texture ---
        const createDotTexture = () => {
            const size = 64;
            const canvas = document.createElement("canvas");
            canvas.width = size;
            canvas.height = size;
            const ctx = canvas.getContext("2d")!;

            // Sharp radial gradient: bright center, fast falloff for pinpoint look
            const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
            gradient.addColorStop(0, "rgba(255,255,255,1)");
            gradient.addColorStop(0.1, "rgba(255,255,255,0.9)");
            gradient.addColorStop(0.25, "rgba(255,255,255,0.4)");
            gradient.addColorStop(0.5, "rgba(255,255,255,0.1)");
            gradient.addColorStop(1, "rgba(255,255,255,0)");

            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, size, size);

            const texture = new THREE.CanvasTexture(canvas);
            texture.needsUpdate = true;
            return texture;
        };

        // --- Scene Setup ---
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0a0a);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.z = 15;

        const renderer = new THREE.WebGLRenderer({
            alpha: false,
            antialias: true,
            powerPreference: "high-performance",
        });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.domElement.style.position = "absolute";
        renderer.domElement.style.inset = "0";
        renderer.domElement.style.width = "100%";
        renderer.domElement.style.height = "100%";
        renderer.domElement.style.pointerEvents = "none";
        containerRef.current.appendChild(renderer.domElement);

        // --- Particles with varying sizes ---
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(CONFIG.particleCount * 3);
        const sizes = new Float32Array(CONFIG.particleCount);
        const opacities = new Float32Array(CONFIG.particleCount);
        const velocitiesX = new Float32Array(CONFIG.particleCount);
        const velocitiesY = new Float32Array(CONFIG.particleCount);

        for (let i = 0; i < CONFIG.particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * CONFIG.fieldSize;
            positions[i * 3 + 1] = (Math.random() - 0.5) * CONFIG.fieldSize;
            positions[i * 3 + 2] = (Math.random() - 0.5) * CONFIG.zDepth;

            // Varying sizes: some near (larger), some far (smaller)
            sizes[i] = CONFIG.minSize + Math.random() * (CONFIG.maxSize - CONFIG.minSize);

            // Varying brightness
            opacities[i] = CONFIG.minOpacity + Math.random() * (CONFIG.maxOpacity - CONFIG.minOpacity);

            // Initial velocities (slight random drift)
            velocitiesX[i] = (Math.random() - 0.5) * 0.01;
            velocitiesY[i] = (Math.random() - 0.5) * 0.01;
        }

        geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute("size", new THREE.BufferAttribute(sizes, 1));
        geometry.setAttribute("opacity", new THREE.BufferAttribute(opacities, 1));

        // --- Custom shader for circular dots with variable size/opacity ---
        const dotTexture = createDotTexture();

        const shaderMaterial = new THREE.ShaderMaterial({
            uniforms: {
                uTexture: { value: dotTexture },
                uPixelRatio: { value: Math.min(window.devicePixelRatio, 1.5) },
            },
            vertexShader: `
        attribute float size;
        attribute float opacity;
        varying float vOpacity;
        uniform float uPixelRatio;
        
        void main() {
          vOpacity = opacity;
          vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
          gl_PointSize = size * uPixelRatio * (80.0 / -mvPosition.z);
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
            fragmentShader: `
        uniform sampler2D uTexture;
        varying float vOpacity;
        
        void main() {
          vec4 texColor = texture2D(uTexture, gl_PointCoord);
          gl_FragColor = vec4(1.0, 1.0, 1.0, texColor.a * vOpacity);
        }
      `,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
        });

        const particles = new THREE.Points(geometry, shaderMaterial);
        scene.add(particles);

        // --- Mouse tracking with Inertia ---
        const mouse = { x: 0, y: 0 };
        const momentum = { x: 0, y: 0 };
        let mouseInView = false;
        let lastTime = 0;

        const handleMouseMove = (e: MouseEvent) => {
            mouseInView = true;
            const newX = (e.clientX / window.innerWidth) * 2 - 1;
            const newY = -(e.clientY / window.innerHeight) * 2 + 1;

            // Calculate instantaneous velocity
            const dx = newX - mouse.x;
            const dy = newY - mouse.y;

            // Add to momentum (act as an impulse)
            // We clamp it to prevent massive jumps on fast travel
            momentum.x += dx * 0.8;
            momentum.y += dy * 0.8;

            mouse.x = newX;
            mouse.y = newY;
        };

        const handleMouseLeave = () => {
            mouseInView = false;
        };

        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("mouseleave", handleMouseLeave);

        // --- Resize handler ---
        const handleResize = () => {
            if (!containerRef.current) return;
            const width = containerRef.current.clientWidth;
            const height = containerRef.current.clientHeight;
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
            shaderMaterial.uniforms.uPixelRatio.value = Math.min(window.devicePixelRatio, 1.5);
        };
        window.addEventListener("resize", handleResize);
        handleResize();

        // --- Animation Loop ---
        let frameId: number;
        const clock = new THREE.Clock();

        const animate = () => {
            frameId = requestAnimationFrame(animate);

            // Check for reduced motion preference
            if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
                renderer.render(scene, camera);
                return;
            }

            const dt = Math.min(clock.getDelta(), 0.1); // Cap delta to avoid jumps
            const posAttr = geometry.attributes.position;
            const posArray = posAttr.array as Float32Array;

            // Mouse world position (approximate)
            const mouseWorldX = mouse.x * CONFIG.fieldSize * 0.5;
            const mouseWorldY = mouse.y * CONFIG.fieldSize * 0.5;

            // Calculate momentum strength for this frame
            const momentumSpeed = Math.sqrt(momentum.x * momentum.x + momentum.y * momentum.y);

            for (let i = 0; i < CONFIG.particleCount; i++) {
                const i3 = i * 3;
                let x = posArray[i3];
                let y = posArray[i3 + 1];
                let z = posArray[i3 + 2];

                // Base ambient swirl (very slow circular drift + noise)
                const angle = Math.atan2(y, x);
                const dist = Math.sqrt(x * x + y * y) + 0.1;

                // Gentle orbital motion
                let vx = -Math.sin(angle) * CONFIG.baseDrift * dist * 0.1;
                let vy = Math.cos(angle) * CONFIG.baseDrift * dist * 0.1;

                // --- Cursor influence: Momentum-based ---
                if (mouseInView || momentumSpeed > 0.001) {
                    const dx = x - mouseWorldX;
                    const dy = y - mouseWorldY;
                    const distToCursor = Math.sqrt(dx * dx + dy * dy);

                    // Influence falls off with distance but affects ALL particles
                    // We treat the "mouse" as the source of the force even if it stopped moving, 
                    // spreading the momentum from that point.
                    const influence = CONFIG.cursorInfluence / (1 + distToCursor * 0.5);

                    // 1. Drag Force: Pull particles along the momentum vector
                    vx += momentum.x * influence * 12.0;
                    vy += momentum.y * influence * 12.0;

                    // 2. Swirl Force: Rotate based on momentum magnitude
                    // Tangent vector
                    const tangentX = -dy / (distToCursor + 0.1);
                    const tangentY = dx / (distToCursor + 0.1);

                    // Using momentum magnitude to drive absolute swirl (always CW or CCW relative to movement?)
                    // Let's make it swirl based on the "curl" of the movement? 
                    // For simplicity and fluid feel: Swirl magnitude proportional to momentum speed.
                    vx += tangentX * influence * momentumSpeed * 15.0;
                    vy += tangentY * influence * momentumSpeed * 15.0;
                }

                // Update positions
                x += vx;
                y += vy;
                z += (Math.random() - 0.5) * 0.01; // Tiny z wobble

                // Wrap around boundaries smoothly
                const halfField = CONFIG.fieldSize / 2;
                if (x > halfField) x -= CONFIG.fieldSize;
                if (x < -halfField) x += CONFIG.fieldSize;
                if (y > halfField) y -= CONFIG.fieldSize;
                if (y < -halfField) y += CONFIG.fieldSize;
                if (z > CONFIG.zDepth / 2) z -= CONFIG.zDepth;
                if (z < -CONFIG.zDepth / 2) z += CONFIG.zDepth;

                posArray[i3] = x;
                posArray[i3 + 1] = y;
                posArray[i3 + 2] = z;
            }

            posAttr.needsUpdate = true;

            // Inertia Decay:
            // 0.96 per frame drops to ~1% after ~112 frames (~1.8s at 60fps)
            // This provides the "2 seconds" slide user asked for.
            momentum.x *= 0.96;
            momentum.y *= 0.96;

            renderer.render(scene, camera);
        };

        animate();

        // --- Cleanup ---
        return () => {
            window.removeEventListener("resize", handleResize);
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("mouseleave", handleMouseLeave);
            cancelAnimationFrame(frameId);
            if (containerRef.current && containerRef.current.contains(renderer.domElement)) {
                containerRef.current.removeChild(renderer.domElement);
            }
            geometry.dispose();
            shaderMaterial.dispose();
            dotTexture.dispose();
            renderer.dispose();
        };
    }, []);

    return (
        <div
            ref={containerRef}
            className="absolute inset-0 z-0 pointer-events-none"
            aria-hidden="true"
        />
    );
}
