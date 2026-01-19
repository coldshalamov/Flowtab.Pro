"use client";

import { Button } from "@/components/ui/button";
import { Bookmark, Check } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export function SaveButton({ className }: { className?: string }) {
    const [saved, setSaved] = useState(false);

    const handleSave = () => {
        setSaved(true);
        toast.success("Flow saved (coming soon)");
        // Revert status after delay? Or keep it? User said "Safe Flow" ... toast ... or disable.
        // I'll keep it saved for visual effect.
    };

    return (
        <Button
            variant="outline"
            onClick={handleSave}
            className={cn("gap-2", className)}
            disabled={saved}
        >
            {saved ? <Check className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
            {saved ? "Saved" : "Save Flow"}
        </Button>
    );
}
