"use client";

import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { Trash2 } from "lucide-react";

import { useAuth } from "@/components/AuthProvider";
import {
  createComment,
  deleteComment,
  fetchComments,
} from "@/lib/api";
import type { Comment } from "@/lib/apiTypes";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LikeButton } from "@/components/LikeButton";

export function CommentsSection(props: {
  promptSlug: string;
  promptId: string;
}) {
  const { promptSlug, promptId } = props;
  const { user } = useAuth();

  const [items, setItems] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [body, setBody] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const canPost = !!user;

  const title = useMemo(() => {
    const count = items.length;
    return count === 1 ? "1 Comment" : `${count} Comments`;
  }, [items.length]);

  useEffect(() => {
    let alive = true;

    (async () => {
      try {
        setIsLoading(true);
        const res = await fetchComments(promptSlug);
        if (!alive) return;
        setItems(res.items);
      } catch (e) {
        console.error(e);
        if (alive) toast.error("Failed to load comments.");
      } finally {
        if (alive) setIsLoading(false);
      }
    })();

    return () => {
      alive = false;
    };
  }, [promptSlug]);

  const submit = async () => {
    if (!canPost) {
      toast.error("Please log in to comment.");
      return;
    }

    const trimmed = body.trim();
    if (!trimmed) return;

    try {
      setIsSubmitting(true);
      const created = await createComment(promptSlug, trimmed);
      setItems((prev) => [...prev, created]);
      setBody("");
    } catch (e) {
      console.error(e);
      toast.error("Failed to post comment.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const remove = async (commentId: string) => {
    try {
      const ok = await deleteComment(commentId);
      if (!ok) {
        toast.error("Failed to delete comment.");
        return;
      }
      setItems((prev) => prev.filter((c) => c.id !== commentId));
    } catch (e) {
      console.error(e);
      toast.error("Failed to delete comment.");
    }
  };

  const isOwnerOrAdmin = (c: Comment) => {
    if (!user) return false;
    return user.is_superuser || c.author_id === user.id;
  };

  return (
    <Card className="rounded-lg border-border bg-card overflow-hidden">
      <CardHeader className="border-b border-border bg-muted/30 py-4">
        <CardTitle className="text-[10px] font-bold uppercase tracking-[0.3em] text-muted-foreground">
          Signal // {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6 space-y-6">
        <div className="space-y-4">
          <Textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder={canPost ? "Add a comment..." : "Log in to join the discussion"}
            disabled={!canPost || isSubmitting}
            className="min-h-24"
          />
          <div className="flex items-center justify-between">
            <div className="text-xs text-muted-foreground">
              {promptId ? "" : null}
            </div>
            <Button
              type="button"
              onClick={submit}
              disabled={!canPost || isSubmitting || body.trim().length === 0}
              className="h-10 px-4 font-bold uppercase tracking-widest text-xs"
            >
              {isSubmitting ? "Posting..." : "Post"}
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading comments...</div>
        ) : items.length === 0 ? (
          <div className="text-sm text-muted-foreground">
            No signal yet. Start the discussion.
          </div>
        ) : (
          <div className="space-y-4">
            {items.map((c) => (
              <div
                key={c.id}
                className="rounded-lg border border-border/60 bg-muted/10 p-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
                      {c.author_id}
                    </div>
                    <div className="mt-2 text-sm text-foreground/90 whitespace-pre-wrap break-words">
                      {c.body}
                    </div>
                    <div className="mt-3 text-xs text-muted-foreground">
                      {new Date(c.createdAt).toLocaleString()}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <LikeButton
                      targetType="comment"
                      targetId={c.id}
                      initialCount={c.like_count ?? 0}
                      size="sm"
                      className="h-8 px-2"
                    />

                    {isOwnerOrAdmin(c) && (
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        className="h-8 px-2"
                        onClick={() => remove(c.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
