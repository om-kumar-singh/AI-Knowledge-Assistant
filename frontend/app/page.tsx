"use client";

import { useCallback, useState } from "react";

import ChatInput from "@/components/ChatInput";
import ChatWindow, { type ChatMessage } from "@/components/ChatWindow";
import { postQuery } from "@/lib/api";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = useCallback(
    async (text: string) => {
      setError(null);
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      try {
        const data = await postQuery(text, sessionId);
        setSessionId(data.session_id);

        let assistantContent = data.answer;
        if (data.sources?.length) {
          assistantContent += `\n\n— ${data.sources.length} source chunk(s) used`;
        }

        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: assistantContent,
          },
        ]);
      } catch (e) {
        const msg =
          e instanceof Error ? e.message : "Something went wrong. Is the API running?";
        setError(msg);
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content:
              "Could not reach the backend. Ensure FastAPI is running (e.g. http://localhost:8000) and CORS allows this origin.",
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId],
  );

  return (
    <div className="flex h-screen min-h-0 bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-zinc-200/90 bg-white/90 dark:border-zinc-800 dark:bg-zinc-950/90 md:flex">
        <div className="border-b border-zinc-200/90 px-4 py-4 dark:border-zinc-800">
          <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-500">
            Sessions
          </p>
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
            Placeholder — thread is tracked via{" "}
            <code className="rounded bg-zinc-100 px-1 font-mono text-xs dark:bg-zinc-900">
              session_id
            </code>
          </p>
          {sessionId && (
            <p
              className="mt-3 truncate font-mono text-[10px] text-zinc-400 dark:text-zinc-500"
              title={sessionId}
            >
              Current: {sessionId.slice(0, 8)}…
            </p>
          )}
        </div>
        <div className="flex-1 p-4">
          <p className="text-xs text-zinc-400 dark:text-zinc-600">More sessions soon.</p>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="shrink-0 border-b border-zinc-200/90 bg-white/80 px-4 py-3 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/80">
          <div className="mx-auto flex max-w-3xl items-center justify-between gap-3">
            <div>
              <h1 className="text-base font-semibold tracking-tight">AI Knowledge Assistant</h1>
              <p className="text-xs text-zinc-500 dark:text-zinc-500">Local RAG · Chat</p>
            </div>
          </div>
        </header>

        {error && (
          <div
            className="shrink-0 border-b border-red-200/80 bg-red-50 px-4 py-2 text-center text-xs text-red-800 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-200"
            role="alert"
          >
            {error}
          </div>
        )}

        <ChatWindow messages={messages} isLoading={isLoading} />
        <ChatInput onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  );
}
