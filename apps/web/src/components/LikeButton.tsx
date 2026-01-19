"use client";

import { useCallback, useMemo, useState } from "react";
import { Heart } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  likeComment,
  likePrompt,
  unlikeComment,
  unlikePrompt,
} from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";

type LikeTargetType = "prompt" | "comment";

export function LikeButton(props: {
  targetType: LikeTargetType;
  targetId: string;
  initialCount: number;
  initialLiked?: boolean;
  size?: "sm" | "default";
  className?: string;
}) {
  const {
    targetType,
    targetId,
    initialCount,
    initialLiked = false,
    size = "sm",
    className,
  } = props;

  const { user } = useAuth();
  const [liked, setLiked] = useState(initialLiked);
  const [count, setCount] = useState(initialCount);
  const [isSaving, setIsSaving] = useState(false);

  const label = useMemo(() => {
    const noun = targetType === "prompt" ? "Flow" : "Comment";
    return liked ? `Unlike ${noun}` : `Like ${noun}`;
  }, [liked, targetType]);

  const toggle = useCallback(async () => {
    if (!user) {
      toast.error("Please log in to like.");
      return;
    }

    if (isSaving) return;

    const optimisticNext = !liked;
    setLiked(optimisticNext);
    setCount((c) => Math.max(0, c + (optimisticNext ? 1 : -1)));

    try {
      setIsSaving(true);
      const res = await (targetType === "prompt"
        ? optimisticNext
          ? likePrompt(targetId)
          : unlikePrompt(targetId)
        : optimisticNext
          ? likeComment(targetId)
          : unlikeComment(targetId));

      // Align with server truth
      setLiked(res.liked);
      setCount(res.likeCount);
    } catch (e) {
      // Rollback
      setLiked((prev) => !prev);
      setCount((c) => Math.max(0, c + (optimisticNext ? -1 : 1)));
      toast.error("Failed to update like.");
      console.error(e);
    } finally {
      setIsSaving(false);
    }
  }, [user, isSaving, liked, targetId, targetType]);

  return (
    <Button
      type="button"
      variant={liked ? "default" : "outline"}
      size={size}
      onClick={toggle}
      aria-label={label}
      className={`${className} transition-transform active:scale-95 duration-150`}
      disabled={isSaving}
    >
      <Heart className={"h-4 w-4" + (liked ? " fill-current" : "")} />
      <span className="ml-2 text-xs font-bold uppercase tracking-widest">
        {count}
      </span>
    </Button>
  );
}
