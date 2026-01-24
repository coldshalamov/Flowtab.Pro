"use client";

import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { submitPrompt } from "@/lib/api";
import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";

interface ThreadForm {
    title: string;
    summary: string;
    body: string;
    tags: string;
}

export default function NewThreadPage() {
    const router = useRouter();
    const { user, isLoading } = useAuth();
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        if (!isLoading && !user) {
            router.push("/login?redirect=/forum/new");
        }
    }, [isLoading, user, router]);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<ThreadForm>();

    const onSubmit = async (data: ThreadForm) => {
        if (!user) {
            router.push("/login?redirect=/forum/new");
            return;
        }

        setIsSubmitting(true);
        try {
            const success = await submitPrompt({
                title: data.title,
                summary: data.summary,
                promptText: data.body, // We map body -> promptText
                tags: data.tags.split(",").map((t) => t.trim()).filter(Boolean),
                type: "discussion",
                // Dummy values for required prompt fields
                worksWith: [],
                targetSites: [],
                steps: [],
                notes: "",
            });

            if (success) {
                router.push("/forum");
                router.refresh();
            } else {
                alert("Failed to create thread. You may need to log in again.");
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-black text-white p-4 flex items-center justify-center">
                <Loader2 className="animate-spin text-blue-500" size={32} />
            </div>
        );
    }

    if (!user) {
        return null; // Will redirect via useEffect
    }

    return (
        <div className="min-h-screen bg-black text-white p-4">
            <div className="max-w-2xl mx-auto py-12">
                <h1 className="text-3xl font-bold mb-8">Start a Thread</h1>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300">Title</label>
                        <input
                            {...register("title", { required: true, minLength: 5 })}
                            className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-gray-600"
                            placeholder="What's on your mind?"
                        />
                        {errors.title && <span className="text-red-500 text-xs">Title is required (min 5 chars)</span>}
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300">Category / Tags</label>
                        <input
                            {...register("tags")}
                            className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-gray-600"
                            placeholder="e.g. question, showcase, help (comma separated)"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300">Short Summary</label>
                        <input
                            {...register("summary", { required: true })}
                            className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-gray-600"
                            placeholder="One line description..."
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300">Body</label>
                        <textarea
                            {...register("body", { required: true, minLength: 20 })}
                            rows={10}
                            className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-gray-600 resize-none font-mono text-sm"
                            placeholder="Write your post here... Markdown supported."
                        />
                        {errors.body && <span className="text-red-500 text-xs">Body is required (min 20 chars)</span>}
                    </div>

                    <div className="flex gap-4 pt-4">
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {isSubmitting && <Loader2 className="animate-spin" size={18} />}
                            {isSubmitting ? "Posting..." : "Create Thread"}
                        </button>
                        <button
                            type="button"
                            onClick={() => router.back()}
                            className="px-6 py-3 text-gray-400 hover:text-white transition-colors"
                        >
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
