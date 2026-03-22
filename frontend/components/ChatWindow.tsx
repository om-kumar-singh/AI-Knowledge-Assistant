"use client";

import { useEffect, useRef } from "react";

import MessageBubble from "./MessageBubble";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

type ChatWindowProps = {
  messages: ChatMessage[];
  isLoading: boolean;
};

function TypingIndicator() {
  return (
    <div className="flex justify-start" aria-live="polite" aria-label="Assistant is typing">
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-md border border-zinc-200/80 bg-zinc-100 px-4 py-3 dark:border-zinc-700/80 dark:bg-zinc-800">
        <span className="size-1.5 animate-bounce rounded-full bg-zinc-500 [animation-delay:-0.3s] dark:bg-zinc-400" />
        <span className="size-1.5 animate-bounce rounded-full bg-zinc-500 [animation-delay:-0.15s] dark:bg-zinc-400" />
        <span className="size-1.5 animate-bounce rounded-full bg-zinc-500 dark:bg-zinc-400" />
      </div>
    </div>
  );
}

export default function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
      <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-4 py-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-4">
          {messages.length === 0 && !isLoading && (
            <div className="rounded-2xl border border-dashed border-zinc-300/80 bg-zinc-100/50 px-6 py-10 text-center dark:border-zinc-700 dark:bg-zinc-900/40">
              <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                Ask anything about your uploaded documents
              </p>
              <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-500">
                Answers use your backend RAG pipeline at{" "}
                <code className="rounded bg-zinc-200/80 px-1.5 py-0.5 font-mono text-[11px] dark:bg-zinc-800">
                  POST /api/query
                </code>
              </p>
            </div>
          )}
          {messages.map((m) => (
            <MessageBubble key={m.id} role={m.role} content={m.content} />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={bottomRef} className="h-px shrink-0" aria-hidden />
        </div>
      </div>
    </div>
  );
}
