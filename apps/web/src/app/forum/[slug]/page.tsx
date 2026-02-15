import { fetchPrompt } from "@/lib/api";
import { CommentsSection } from "@/components/CommentsSection";
import ReactMarkdown from "react-markdown";
import { Suspense } from "react";
import { formatDistanceToNow } from "date-fns";
import { User, MessageSquare, Clock } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function ThreadDetailPage({
    params,
}: {
    params: { slug: string };
}) {
    const discussion = await fetchPrompt(params.slug);

    if (!discussion || (discussion.type && discussion.type !== "discussion")) {
        notFound();
    }

    return (
        <div className="min-h-screen bg-black text-white">
            <div className="container mx-auto px-4 py-8 max-w-4xl">
                <Link
                    href="/forum"
                    className="text-gray-500 hover:text-white mb-6 inline-block transition-colors text-sm"
                >
                    ← Back to Forum
                </Link>

                {/* Header */}
                <div className="border-b border-gray-800 pb-8 mb-8">
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 mb-4 leading-tight">
                        {discussion.title}
                    </h1>

                    <div className="flex items-center gap-6 text-sm text-gray-400">
                        <div className="flex items-center gap-2">
                            <User size={16} className="text-blue-500" />
                            <span className="font-medium text-gray-300">{discussion.author_id || "Anonymous"}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Clock size={16} />
                            <span>{formatDistanceToNow(new Date(discussion.createdAt))} ago</span>
                        </div>

                        <div className="flex gap-2 ml-auto">
                            {discussion.tags.map(tag => (
                                <span key={tag} className="px-2 py-0.5 rounded-full bg-gray-900 border border-gray-800 text-xs">
                                    #{tag}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Body */}
                <div className="prose prose-invert prose-lg max-w-none mb-16">
                    <ReactMarkdown>{discussion.promptText}</ReactMarkdown>
                </div>

                {/* Comments */}
                <div className="pt-8 border-t border-gray-800">
                    <div className="flex items-center gap-3 mb-8">
                        <MessageSquare className="text-blue-500" />
                        <h2 className="text-2xl font-semibold">Comments</h2>
                    </div>

                    <Suspense fallback={<div className="text-sm text-gray-500">Loading comments...</div>}>
                        <CommentsSection promptSlug={params.slug} promptId={discussion.id} />
                    </Suspense>
                </div>
            </div>
        </div>
    );
}
