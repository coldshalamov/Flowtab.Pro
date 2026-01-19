"use client";

import dynamic from "next/dynamic";

const ParticleStorm = dynamic(() => import("@/components/ParticleStorm").then(mod => mod.ParticleStorm), { ssr: false });

export function HeroBackground() {
    return <ParticleStorm />;
}
