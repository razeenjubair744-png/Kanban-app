"use client";

import { FormEvent, useState } from "react";

type LoginScreenProps = {
  onLogin: (username: string, password: string) => Promise<void>;
  loading: boolean;
  error: string | null;
};

export const LoginScreen = ({ onLogin, loading, error }: LoginScreenProps) => {
  const [username, setUsername] = useState("user");
  const [password, setPassword] = useState("password");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onLogin(username.trim(), password);
  };

  return (
    <div>
      <div className="mb-8 text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
          Sign in to your board
        </p>
        <h2 className="mt-3 text-3xl font-semibold text-[var(--navy-dark)]">
          Welcome back
        </h2>
        <p className="mt-4 text-sm leading-6 text-[var(--gray-text)]">
          Use the demo credentials below to access your kanban board.
        </p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label className="block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
            Username
          </label>
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="w-full rounded-2xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
            placeholder="user"
            autoComplete="username"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-2xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
            placeholder="password"
            autoComplete="current-password"
          />
        </div>

        {error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-full bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </div>
  );
};
