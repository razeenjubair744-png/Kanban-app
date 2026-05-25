"use client";

import { useCallback, useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { AiSidebar } from "@/components/AiSidebar";
import { LoginScreen } from "@/components/LoginScreen";
import { initialData, type BoardData } from "@/lib/kanban";

type ChatMessage = {
  role: "user" | "assistant";
  text: string;
};

const authHeader = (token: string) => ({ Authorization: `Bearer ${token}` });

export const KanbanApp = () => {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [board, setBoard] = useState<BoardData>(initialData);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const loadBoard = useCallback(async () => {
    if (!token) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/board", {
        headers: authHeader(token),
      });

      if (!response.ok) {
        throw new Error("Unable to load board.");
      }

      const boardData = await response.json();
      setBoard(boardData);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Unable to load board.",
      );
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      void loadBoard();
    }
  }, [token, loadBoard]);

  const handleLogin = async (usernameValue: string, password: string) => {
    setError(null);
    setLoading(true);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: usernameValue, password }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail || "Invalid username or password.");
      }

      const data = await response.json();
      setToken(data.token);
      setUsername(data.username);
      setMessages([]);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Invalid username or password.",
      );
    } finally {
      setLoading(false);
    }
  };

  const saveBoard = async (nextBoard: BoardData) => {
    if (!token) {
      return;
    }

    try {
      const response = await fetch("/api/board", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          ...authHeader(token),
        },
        body: JSON.stringify(nextBoard),
      });
      if (!response.ok) {
        throw new Error("Unable to save board.");
      }
      const savedBoard = await response.json();
      setBoard(savedBoard);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Unable to save board.",
      );
    }
  };

  const handleBoardChange = async (nextBoard: BoardData) => {
    setBoard(nextBoard);
    void saveBoard(nextBoard);
  };

  const handleLogout = () => {
    setToken(null);
    setUsername(null);
    setBoard(initialData);
    setMessages([]);
    setError(null);
  };

  const handleAiSubmit = async (prompt: string) => {
    if (!token) {
      return;
    }

    const userMessage: ChatMessage = { role: "user", text: prompt };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setAiLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/ai", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeader(token),
        },
        body: JSON.stringify({ prompt, board, history: nextMessages }),
      });

      if (!response.ok) {
        throw new Error("Unable to contact AI service.");
      }

      const result = await response.json();
      setMessages((current) => [
        ...current,
        { role: "assistant", text: result.message },
      ]);

      if (result.boardUpdates) {
        setBoard(result.boardUpdates);
      }
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to contact AI service.",
      );
    } finally {
      setAiLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-[#f7f8fb] px-6 py-10">
        <div className="mx-auto max-w-xl rounded-[32px] border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)]">
          <LoginScreen onLogin={handleLogin} loading={loading} error={error} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f7f8fb] px-6 py-10">
      <div className="mx-auto max-w-[1500px] space-y-6">
        <header className="flex flex-col gap-4 rounded-[32px] border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)] md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
              Single Board Kanban
            </p>
            <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
              Kanban Studio
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--gray-text)]">
              Keep momentum visible. Rename columns, move cards, and let the AI
              help you polish the board.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <p className="text-sm text-[var(--gray-text)]">
              Signed in as{" "}
              <span className="font-semibold text-[var(--navy-dark)]">
                {username}
              </span>
            </p>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-full bg-[var(--secondary-purple)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-white transition hover:brightness-110"
            >
              Logout
            </button>
          </div>
        </header>

        {error ? (
          <div className="rounded-3xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <div className="grid gap-6 xl:grid-cols-[1.7fr_0.9fr]">
          <div className="rounded-[32px] border border-[var(--stroke)] bg-white p-6 shadow-[var(--shadow)]">
            <KanbanBoard board={board} onBoardChange={handleBoardChange} />
            {loading ? (
              <p className="mt-4 text-sm text-[var(--gray-text)]">
                Loading board data...
              </p>
            ) : null}
          </div>
          <div className="rounded-[32px] border border-[var(--stroke)] bg-white p-6 shadow-[var(--shadow)]">
            <AiSidebar
              messages={messages}
              onSend={handleAiSubmit}
              loading={aiLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
