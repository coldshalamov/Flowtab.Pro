import { fetchPrompts } from "@/lib/api";
import { Prompt } from "@/lib/apiTypes";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { MessageSquare, Plus, User as UserIcon } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function ForumPage() {
    const { items: discussions } = await fetchPrompts({ type: "discussion" });

    return (
        <div className="min-h-screen bg-black text-white">
            <div className="container mx-auto px-4 py-8 max-w-5xl">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500 mb-2">
                            Forum
                        </h1>
                        <p className="text-gray-400">
                            Discuss automation strategies, request flows, and share tips.
                        </p>
                    </div>
                    <Link
                        href="/forum/new"
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                        <Plus size={18} />
                        New Thread
                    </Link>
                </div>

                <div className="space-y-4">
                    {discussions.length === 0 ? (
                        <div className="text-center py-12 border border-gray-800 rounded-xl bg-gray-900/50">
                            <MessageSquare size={48} className="mx-auto text-gray-700 mb-4" />
                            <h3 className="text-xl font-semibold text-gray-300">No threads yet</h3>
                            <p className="text-gray-500 max-w-sm mx-auto mt-2">
                                Be the first to start a conversation in the community!
                            </p>
                        </div>
                    ) : (
                        discussions.map((discussion) => (
                            <DiscussionCard key={discussion.id} discussion={discussion} />
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}

function DiscussionCard({ discussion }: { discussion: Prompt }) {
    return (
        <Link
            href={`/forum/${discussion.slug}`}
            className="block p-6 border border-gray-800 rounded-xl bg-gray-900/40 hover:bg-gray-800/60 transition-colors group"
        >
            <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-100 group-hover:text-blue-400 transition-colors mb-2">
                        {discussion.title}
                    </h3>
                    <p className="text-gray-400 text-sm line-clamp-2 mb-4">
                        {discussion.summary}
                    </p>

                    <div className="flex items-center gap-4 text-xs text-gray-500">
                        <div className="flex items-center gap-1.5">
                            <UserIcon size={14} />
                            <span>{discussion.author_id || "Anonymous"}</span>
                        </div>
                        <span>•</span>
                        <span>{formatDistanceToNow(new Date(discussion.createdAt))} ago</span>
                        <span>•</span>
                        <div className="flex items-center gap-1.5 text-gray-400">
                            <MessageSquare size={14} />
                            <span>{0} comments</span> {/* TODO: Add comment count to list response */}
                        </div>
                    </div>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 justify-end max-w-[200px]">
                    {discussion.tags.slice(0, 3).map((tag) => (
                        <span
                            key={tag}
                            className="px-2 py-1 text-xs bg-gray-800 text-gray-300 rounded-full border border-gray-700"
                        >
                            #{tag}
                        </span>
                    ))}
                </div>
            </div>
        </Link>
    );
}
