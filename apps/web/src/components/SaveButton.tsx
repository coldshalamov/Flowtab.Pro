"use client";

import { Button } from "@/components/ui/button";
import { Bookmark, Check } from "lucide-react";
import { useState, useCallback } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { savePrompt, unsavePrompt } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";

interface SaveButtonProps {
  slug: string;
  initialSaved?: boolean;
  initialCount?: number;
  className?: string;
}

export function SaveButton({ 
  slug, 
  initialSaved = false, 
  initialCount = 0,
  className 
}: SaveButtonProps) {
  const { user } = useAuth();
  const [saved, setSaved] = useState(initialSaved);
  const [count, setCount] = useState(initialCount);
  const [isLoading, setIsLoading] = useState(false);

  const handleSave = useCallback(async () => {
    if (!user) {
      toast.error("Please log in to save flows.");
      return;
    }

    if (isLoading) return;

    const nextSaved = !saved;
    
    // Optimistic update
    setSaved(nextSaved);
    setCount(c => Math.max(0, c + (nextSaved ? 1 : -1)));
    setIsLoading(true);

    try {
      const res = await (nextSaved ? savePrompt(slug) : unsavePrompt(slug));
      // Align with server truth
      setSaved(res.liked);
      setCount(res.likeCount);
      toast.success(nextSaved ? "Flow saved to your library." : "Flow removed from saved.");
    } catch (e) {
      // Rollback on error
      setSaved(saved);
      setCount(c => Math.max(0, c + (nextSaved ? -1 : 1)));
      toast.error("Failed to update save status.");
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, [user, isLoading, saved, slug]);

  return (
    <Button
      variant="outline"
      onClick={handleSave}
      disabled={isLoading}
      className={cn("gap-2", className)}
    >
      {saved ? <Check className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
      {saved ? "Saved" : "Save Flow"}
      {count > 0 && (
        <span className="ml-1 text-xs font-bold uppercase tracking-widest">
          {count}
        </span>
      )}
    </Button>
  );
}
