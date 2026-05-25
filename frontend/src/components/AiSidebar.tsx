"use client";

import { FormEvent, useState } from "react";

type ChatMessage = {
  role: "user" | "assistant";
  text: string;
};

type AiSidebarProps = {
  messages: ChatMessage[];
  onSend: (prompt: string) => Promise<void>;
  loading: boolean;
};

export const AiSidebar = ({ messages, onSend, loading }: AiSidebarProps) => {
  const [inputValue, setInputValue] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const prompt = inputValue.trim();
    if (!prompt) {
      return;
    }
    setInputValue("");
    await onSend(prompt);
  };

  return (
    <div className="flex h-full flex-col gap-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
          AI Assistant
        </p>
        <h2 className="mt-3 text-2xl font-semibold text-[var(--navy-dark)]">
          Board companion
        </h2>
        <p className="mt-3 text-sm leading-6 text-[var(--gray-text)]">
          Ask the AI to update your board, summarize progress, or suggest the
          next priority.
        </p>
      </div>

      <div className="flex-1 overflow-hidden rounded-[32px] border border-[var(--stroke)] bg-[var(--surface-strong)] p-4">
        {messages.length === 0 ? (
          <div className="grid h-full place-items-center text-center text-sm text-[var(--gray-text)]">
            Start a conversation to see AI recommendations.
          </div>
        ) : (
          <div className="flex h-full flex-col gap-3 overflow-y-auto pr-2">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`rounded-3xl p-4 text-sm shadow-[var(--shadow)] ${
                  message.role === "user"
                    ? "bg-white text-[var(--navy-dark)] self-end"
                    : "bg-[var(--surface)] text-[var(--navy-dark)] self-start"
                }`}
              >
                <p className="font-semibold uppercase tracking-[0.18em] text-[var(--gray-text)]">
                  {message.role === "user" ? "You" : "AI assistant"}
                </p>
                <p className="mt-2 whitespace-pre-wrap">{message.text}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          rows={4}
          placeholder="Ask the AI to update the board..."
          className="w-full resize-none rounded-2xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-full bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Thinking..." : "Send to AI"}
        </button>
      </form>
    </div>
  );
};
