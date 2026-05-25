# Code Review: Project Management MVP

Review date: 2026-05-25
Reviewer: AI-assisted code review

---

## 1. Critical Issues (must fix)

### 1.1 Dockerfile is broken

**Files:** `Dockerfile`

Three interconnected bugs:

1. **Wrong `uv` command:** `RUN uv install` is not a valid `uv` command. Should be `RUN uv sync` or `RUN uv pip install -e .`.

2. **Double-nested `backend/` directory:** After `WORKDIR /app/backend`, the instruction `COPY backend ./backend` copies the build context's `backend/` directory into `/app/backend/backend/`. Combined with the earlier `COPY backend/pyproject.toml ./backend/pyproject.toml` which put the file at the intended `/app/backend/pyproject.toml`, the Python package lands at `/app/backend/backend/` (e.g., `/app/backend/backend/main.py`). The `CMD` runs from `/app`, so Python cannot find the `backend` module.

3. **Static files mislocated:** The frontend build output is copied to `/app/backend/frontend/out/` (relative to `WORKDIR /app/backend`), but `main.py` expects it at `frontend/out` relative to the project root (i.e., `/app/frontend/out`). The fallback path in `main.py` uses `Path(__file__).resolve().parents[1] / "frontend" / "out"` which resolves to `/app/frontend/out`. The Dockerfile copies it to `/app/backend/frontend/out/`. These don't match, so the static file mount silently fails at runtime.

**Repro:** `docker build -t pm-app . && docker run pm-app` fails or serves placeholder page instead of the app.

### 1.2 API key exposed in `.env.example`

**Files:** `.env.example`, `.env`

The `.env.example` file (committed to the repo) contains a real-looking OpenRouter API key. The `.env` file (which should be gitignored) has the same key. If `.env.example` is ever committed (it is), the key is exposed in the repository history.

**Fix:** Replace the key in `.env.example` with a placeholder like `sk-or-v1-your-key-here` and rotate the exposed key if it was ever active.

### 1.3 AI message format sends wrong field name to OpenRouter

**File:** `backend/ai.py:37-44`

```python
# Current code sends "text" field:
base.append({"role": turn.get("role", "user"), "content": turn.get("text", "")})
```

The `history` list in `AIRequest` is typed as `List[Dict[str, str]]` with keys `role` and `text` (from the frontend `ChatMessage` type). When building the OpenRouter API payload, the code maps these directly. However, history entries from the frontend have `{ role, text }` keys, but the system prompt + user prompt messages are built with `"content"` key. The history is appended with `"content": turn.get("text", "")` which is correct (mapping `text` to the OpenAI `content` field). So the mapping itself is fine.

However, looking at the frontend `KanbanApp.tsx:147`:
```typescript
body: JSON.stringify({ prompt, board, history: nextMessages }),
```

The `history` sent to the backend includes the *current* messages (including the one just added). `nextMessages` includes the new user message AND all previous history. This means the backend receives the message history with the latest user prompt already included in `history`, and then also sends `request.prompt` separately. The AI will see the user's prompt twice. This is a duplicate content bug.

**Side note:** The `AIRequest.history` field should use a properly typed model instead of `List[Dict[str, str]]`.

### 1.4 Duplicate header in Kanban UI

**Files:** `frontend/src/components/KanbanApp.tsx:188-215`, `frontend/src/components/KanbanBoard.tsx:34-70`

Both `KanbanApp` and `KanbanBoard` render nearly identical header content:
- "Single Board Kanban" label
- "Kanban Studio" heading
- "Keep momentum visible..." description

`KanbanApp` also has the signed-in-as/logout bar. `KanbanBoard` has the gradient circles, column pill tags, and a "Focus" card. Result: the user sees the main title and subtitle duplicated on the page. The `KanbanBoard` component should only render the column-area content and the DndContext, not its own hero header.

### 1.5 E2E tests cannot run in current setup

**File:** `frontend/playwright.config.ts`, `frontend/tests/kanban.spec.ts`

The Playwright config starts only the Next.js dev server (`npm run dev` on port 3000). The E2E tests expect to log in via `/api/auth/login` and interact with the board. These API calls will fail because the FastAPI backend is not running. The test runner needs to either start both servers or the test needs to point at a running full-stack instance.

---

## 2. High Priority

### 2.1 Fire-and-forget save with no error recovery

**File:** `frontend/src/components/KanbanApp.tsx:116-119`

```typescript
const handleBoardChange = async (nextBoard: BoardData) => {
  setBoard(nextBoard);
  void saveBoard(nextBoard);
};
```

The optimistic update immediately updates local state (`setBoard`) and fires `saveBoard` with `void`. If the PATCH request fails, the UI shows the new state but the server still has the old data. On page refresh, the user's unsaved work is lost. The error is swallowed in `saveBoard` - it catches and sets `error` state, but there is no retry mechanism or rollback.

### 2.2 Model name mismatch

**File:** `backend/ai.py:9`, `AGENTS.md`

- AGENTS.md specifies the model as `openai/gpt-oss-120b`
- Actual code uses `meta-llama/llama-3.3-70b-instruct:free`

Both the config/documentation and code should agree.

### 2.3 Database connection management

**File:** `backend/db.py:26-30`, `backend/main.py:34-38`

`get_connection()` creates a new `sqlite3.connect()` each call. While `check_same_thread=False` enables sharing across threads, this pattern risks:
- Leaving connections open (though `get_db()` dependency in FastAPI has `finally: connection.close()`)
- No connection pooling for concurrent requests

The `initialize_database()` function creates a connection but never explicitly closes it (it is closed in the `finally` block after the `try`, so this is fine).

### 2.4 Card IDs not validated on board update

**File:** `backend/schemas.py:15`

The PATCH `/api/board` endpoint accepts any `BoardData` JSON. There is no validation that `cardIds` in each column actually reference existing keys in `cards`, or that referenced cards exist. Corrupt or malicious payloads can silently create invalid board state.

---

## 3. Medium Priority

### 3.1 Board data duplicated between frontend and backend

**Files:** `frontend/src/lib/kanban.ts:18-72`, `backend/db.py:47-79`

The `initialData` in the frontend and `DEFAULT_BOARD` in the backend contain identical card/column data. These can drift independently. The frontend should either fetch initial data from the backend or both should derive from a single source of truth.

### 3.2 No input sanitization on column rename

**File:** `frontend/src/components/KanbanColumn.tsx:42-47`

The column title input directly updates state with no length or character restrictions. Users (or API callers) could set empty titles or excessively long names. The backend stores whatever it receives.

### 3.3 `get_db_path()` is called more than needed

**File:** `backend/db.py:24`

`get_db_path()` is called each time `get_connection()` is called. The `DATA_DIR` is computed once at module level (`Path(__file__).resolve().parent.parent / "data"`) but then `DATA_DIR.mkdir(parents=True, exist_ok=True)` is called on every `get_db_path()` invocation. This is a minor performance issue (filesystem stat on every DB access).

### 3.4 JSON extraction is fragile

**File:** `backend/ai.py:15-25`

The `_extract_json_block` function counts braces to find the JSON object. This breaks if:
- JSON contains braces inside string values
- The AI returns multiple JSON blocks
- The AI wraps the JSON in markdown code fences (the system prompt tells it not to, but LLMs are unreliable)

Consider using a regex-based approach or instructing the model to use a more constrained output format.

### 3.5 AI response parsing silently falls through

**File:** `backend/ai.py:64-73`

If `content` doesn't start/end with `{}` and `_extract_json_block` returns `None`, or if JSON parsing fails, the function falls through to return `AIResponse(message=trimmed, boardUpdates=None)`. The caller has no way to distinguish between "AI intentionally returned no board updates" and "JSON parsing failed."

### 3.6 `createId` collisions are possible

**File:** `frontend/src/lib/kanban.ts:164-168`

```typescript
export const createId = (prefix: string) => {
  const randomPart = Math.random().toString(36).slice(2, 8);
  const timePart = Date.now().toString(36);
  return `${prefix}-${randomPart}${timePart}`;
};
```

`Math.random()` is not cryptographically secure (fine for this use case), but in rapid succession within the same millisecond, `Date.now()` returns the same value and `Math.random()` could theoretically collide. Not a practical concern for an MVP.

---

## 4. Low Priority / Observations

### 4.1 Color CSS variables not in Tailwind theme

**File:** `frontend/src/app/globals.css`

The color scheme (yellow, blue, purple, navy, gray) is defined as CSS custom properties but is not mapped into Tailwind's `theme.extend.colors`. Most components reference them via `var(--xxx)` in inline className strings rather than using Tailwind utility classes (e.g., `text-[var(--navy-dark)]` instead of `text-navy-dark`). This works but is less ergonomic.

### 4.2 `pyproject.toml` missing explicit `pydantic` dependency

**File:** `backend/pyproject.toml`

`pydantic` is a transitive dependency of `fastapi` but is used directly in `schemas.py`. Best practice is to list it explicitly.

### 4.3 Hardcoded auth credentials

**File:** `backend/db.py:22`

Username `user` and password `password` are hardcoded constants. The PLAN.md says this is intentional for MVP. A `TODO` comment noting the security limitation would help future contributors.

### 4.4 No request size limits

**File:** `backend/main.py`

FastAPI has no `max_request_size` or upload limits configured. A large board JSON payload in a PATCH request could cause memory issues.

### 4.5 Graceful degradation for missing `.env`

**File:** `backend/main.py:1-17`, `backend/ai.py:52-59`

`load_dotenv()` silently does nothing if `.env` doesn't exist. `call_openrouter()` gracefully returns an explanatory message if `OPENROUTER_API_KEY` is not set. This is good.

### 4.6 E2E drag-and-drop uses raw mouse events

**File:** `frontend/tests/kanban.spec.ts:26-45`

The drag-and-drop E2E test uses `page.mouse.move/down/up` with manual coordinate calculation. This is fragile across viewport sizes and can be flaky. Consider using `@dnd-kit`'s programmatic drag simulation or Playwright's `dragTo` method if supported.

### 4.7 `backend/AGENTS.md` and `scripts/AGENTS.md` are stubs

Both files contain placeholder text. These should either be filled in or removed.

### 4.8 No health check for Docker container

The Dockerfile does not include a `HEALTHCHECK` instruction. The container health cannot be monitored by orchestration tools.

---

## 5. Summary

| Severity | Count |
|----------|-------|
| Critical | 5 |
| High     | 4 |
| Medium   | 6 |
| Low      | 8 |

**Code quality score: 6.5/10**

The project has solid architecture overall:
- Clean separation of concerns (frontend/backend)
- Good use of modern libraries (Next.js 16, React 19, FastAPI, Pydantic)
- Sensible data flow (API calls from frontend, SQLite persistence)
- Tests exist for core logic

The critical issues are concentrated in the Docker setup (entirely non-functional) and a few frontend/backend integration bugs. Once the Dockerfile is fixed and the duplicate header removed, the project should be deployable for the MVP.
