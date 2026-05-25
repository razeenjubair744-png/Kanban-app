# High level steps for project

Part 1: Plan

- Review the existing frontend source and repo structure.
- Create `frontend/AGENTS.md` describing the current frontend architecture, core components, local state model, and existing tests.
- Confirm the implementation sequence and break every phase into substeps.
- Add test requirements and success criteria for each phase.
- Get explicit user approval before making production changes.

Success criteria:
- `frontend/AGENTS.md` exists and accurately documents the current app.
- `docs/PLAN.md` contains a detailed, executable checklist.
- User approves the plan before Part 2 begins.

Part 2: Scaffolding

- Add a minimal backend skeleton under `backend/` using FastAPI.
- Add a static route that serves a built frontend or placeholder HTML from `/`.
- Add a sample API route such as `GET /api/health`.
- Add a `Dockerfile` and local Docker setup for building and running the app.
- Add start/stop scripts in `scripts/` for macOS, Linux, and Windows.

Success criteria:
- Backend starts cleanly and serves the placeholder page at `/`.
- The sample API endpoint returns a known response.
- Docker build completes and the container can run locally.

Tests:
- Backend unit test for the health route.
- Startup smoke test for the placeholder page.

Part 3: Add in Frontend

- Build the existing frontend statically with `npm run build`.
- Configure the backend to serve the built static files.
- Ensure `GET /` loads the Kanban demo in a browser.
- Keep the current client-side behavior unchanged.

Success criteria:
- `npm run build` succeeds.
- The backend serves the static Kanban app at `/`.
- The UI renders and drag-and-drop works in the deployed environment.

Tests:
- End-to-end test that navigates to `/` and confirms the Kanban title appears.
- Build verification test.

Part 4: Add in a fake user sign in experience

- Add a login screen before showing the Kanban board.
- Require the fixed credentials `user` / `password`.
- Store auth state in-memory on the frontend and allow logout.
- Protect the board UI behind the login gate.

Success criteria:
- Unauthenticated visitors see the login experience.
- Correct credentials grant access to the board.
- Logout returns the user to the login screen.

Tests:
- Unit tests for login validation.
- E2E test for sign-in, board access, and logout.

Part 5: Database modeling

- Define a backend data model for users, boards, columns, and cards.
- Use SQLite with a single file database created automatically if it does not exist.
- Store the Kanban board as JSON in the database while keeping the schema flexible.
- Document the database design in `docs/` and obtain user approval before implementing.

Success criteria:
- Database schema proposal is available in `docs/`.
- User confirms the schema before backend persistence work begins.

Part 6: Backend

- Add backend API routes for auth and board CRUD operations.
- Implement database persistence for the user board.
- Ensure database creation at startup if the file is missing.
- Validate inputs and return clear HTTP status codes.

Success criteria:
- Backend can read the stored board for the signed-in user.
- Backend can persist board changes.
- API routes return correct JSON and status codes.

Tests:
- Unit tests for login, fetch board, and update board.
- Database initialization test.

Part 7: Frontend + Backend

- Replace local board state with backend API calls.
- Load the board from the backend after login.
- Persist rename, drag-and-drop, add, and delete operations through API requests.
- Keep the UI responsive and consistent with MVP scope.

Success criteria:
- Frontend uses backend data instead of local-only state.
- All board updates are saved and reflected on refresh.
- The app remains a single-board experience.

Tests:
- Integration tests covering board load and updates.
- E2E tests for the full user flow from login to board editing.

Part 8: AI connectivity

- Add OpenRouter integration in the backend.
- Use `OPENROUTER_API_KEY` from `.env`.
- Add a simple AI test route that sends a fixed prompt like `2+2`.
- Confirm the AI connection works in the current environment.

Success criteria:
- Backend successfully calls OpenRouter.
- The AI route returns a valid text response.
- API keys are not hardcoded.

Tests:
- Backend test for AI connectivity.
- Manual or automated verification that the route receives a response.

Part 9: Structured AI call

- Extend the AI route so the backend sends the current Kanban JSON plus the user prompt and conversation history.
- Require structured AI output with `message` and optional `boardUpdates`.
- Parse and validate the structured response before applying updates.
- Persist updates when the AI returns them.

Success criteria:
- The backend parses structured AI responses reliably.
- AI-driven board updates are applied when present.
- The user receives a clear human-readable response.

Tests:
- Unit tests for response parsing and update application.
- AI flow test with a mocked OpenRouter response.

Part 10: AI sidebar widget

- Add a sidebar chat UI in the frontend.
- Allow users to submit prompts and view AI responses.
- Preserve conversation history in the session.
- Refresh the board automatically when the AI updates it.

Success criteria:
- Users can chat with the AI from the app.
- AI replies appear in the sidebar.
- Board updates from the AI are reflected without manual reload.

Tests:
- UI test for sending a chat message and receiving a response.
- Integration test for AI-triggered board changes.
