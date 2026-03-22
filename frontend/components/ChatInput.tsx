"use client";

import { type KeyboardEvent, useState } from "react";

type ChatInputProps = {
  onSend: (text: string) => void;
  disabled?: boolean;
};

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");

  const send = () => {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
  };

  const onKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="shrink-0 border-t border-zinc-200/90 bg-zinc-50/95 px-4 py-3 backdrop-blur-md dark:border-zinc-800/90 dark:bg-zinc-950/95">
      <div className="mx-auto flex max-w-3xl gap-2">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Message…"
          disabled={disabled}
          className="min-w-0 flex-1 rounded-xl border border-zinc-200 bg-white px-4 py-3 text-sm text-zinc-900 outline-none ring-emerald-500/40 placeholder:text-zinc-400 focus:border-emerald-500/50 focus:ring-2 disabled:opacity-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:placeholder:text-zinc-500"
          autoComplete="off"
          aria-label="Message input"
        />
        <button
          type="button"
          onClick={send}
          disabled={disabled || !value.trim()}
          className="shrink-0 rounded-xl bg-emerald-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-emerald-600 dark:hover:bg-emerald-500"
        >
          Send
        </button>
      </div>
    </div>
  );
}
