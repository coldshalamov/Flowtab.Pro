"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface FeaturedFlow {
    title: string;
    slug: string;
    like_count: number;
}

interface FeaturedRotatorProps {
    flows: FeaturedFlow[];
}

export function FeaturedRotator({ flows }: FeaturedRotatorProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isAnimating, setIsAnimating] = useState(false);

    // Sort by likes and take top 5
    const topFlows = [...flows]
        .sort((a, b) => (b.like_count || 0) - (a.like_count || 0))
        .slice(0, 5);

    useEffect(() => {
        if (topFlows.length <= 1) return;

        const interval = setInterval(() => {
            // Start animation
            setIsAnimating(true);

            // Wait for transition to finish, then swap state and reset positions instantly
            setTimeout(() => {
                setIsAnimating(false);
                setCurrentIndex((prev) => (prev + 1) % topFlows.length);
            }, 700); // Matches CSS duration

        }, 4500); // 3800ms pause + 700ms animation

        return () => clearInterval(interval);
    }, [topFlows.length]);

    if (topFlows.length === 0) {
        return null;
    }

    const currentFlow = topFlows[currentIndex];
    const nextFlow = topFlows[(currentIndex + 1) % topFlows.length];

    return (
        <p className="text-sm font-medium text-foreground/60 pt-6 animate-in fade-in duration-1000 delay-500">
            <span className="relative inline-block overflow-hidden h-[1.4em] align-bottom">
                {/* Slot 1: The 'Current' item. 
                    - Idle: Center (Visible)
                    - Anim: Moves Bottom (Hidden) 
                    - Reset: Jumps back to Center (With NEW text)
                */}
                <Link
                    href={`/p/${currentFlow.slug}`}
                    className={`
            inline-block underline-offset-2 hover:text-primary hover:underline
            ${isAnimating ? 'transition-all duration-700 ease-in-out' : ''}
            ${isAnimating ? 'translate-y-full opacity-0' : 'translate-y-0 opacity-100'}
          `}
                >
                    {currentFlow.title}
                </Link>

                {/* Slot 2: The 'Next' item.
                    - Idle: Top (Hidden)
                    - Anim: Moves Center (Visible)
                    - Reset: Jumps back to Top (With NEW text)
                */}
                <Link
                    href={`/p/${nextFlow.slug}`}
                    className={`
            absolute left-0 top-0 inline-block underline-offset-2 hover:text-primary hover:underline
            ${isAnimating ? 'transition-all duration-700 ease-in-out' : ''}
            ${isAnimating ? 'translate-y-0 opacity-100' : '-translate-y-full opacity-0'}
          `}
                >
                    {nextFlow.title}
                </Link>
            </span>
        </p>
    );
}
