type MessageBubbleProps = {
  role: "user" | "assistant";
  content: string;
};

export default function MessageBubble({ role, content }: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}
      role="article"
      aria-label={isUser ? "You" : "Assistant"}
    >
      <div
        className={`max-w-[min(85%,42rem)] whitespace-pre-wrap break-words rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm ${
          isUser
            ? "rounded-br-md bg-emerald-600 text-white dark:bg-emerald-600"
            : "rounded-bl-md border border-zinc-200/80 bg-zinc-100 text-zinc-900 dark:border-zinc-700/80 dark:bg-zinc-800 dark:text-zinc-100"
        }`}
      >
        {content}
      </div>
    </div>
  );
}
