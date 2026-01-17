"use client";

import { Button } from "@/components/ui/button";
import { Copy, Check } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export function CopyButton({
    text,
    label = "Copy",
    variant = "outline",
    className
}: {
    text: string,
    label?: string,
    variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link",
    className?: string
}) {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            toast.success("Copied to clipboard!");
            setTimeout(() => setCopied(false), 2000);
        } catch {
            toast.error("Failed to copy");
        }
    };

    return (
        <Button variant={variant} size="sm" onClick={handleCopy} className={cn("gap-2 transition-all", className)}>
            {copied ? <Check className="h-4 w-4 animate-in zoom-in" /> : <Copy className="h-4 w-4" />}
            {copied ? "Copied" : label}
        </Button>
    );
}
