# Frontend AGENTS.md

## Overview

The frontend is a Next.js app that currently runs as a static, client-side demo. It implements a single Kanban board with drag-and-drop card movement, column renaming, card creation, and card deletion.

## Key files

- `src/app/page.tsx`
  - Renders the root `KanbanBoard` component.

- `src/components/KanbanBoard.tsx`
  - Client component with board state held in React.
  - Uses `@dnd-kit/core` for drag-and-drop.
  - Handles column rename, add card, delete card, and card move.
  - Renders the board header, columns, and drag overlay.

- `src/components/KanbanColumn.tsx`
  - Droppable column container.
  - Renders the column title input, card list, and new card form.
  - Uses `SortableContext` from `@dnd-kit/sortable`.

- `src/components/KanbanCard.tsx`
  - Draggable card component.
  - Uses `useSortable` and applies transform/transition styling.
  - Includes a remove button.

- `src/components/KanbanCardPreview.tsx`
  - Rendered inside `DragOverlay` when dragging a card.
  - Shows the card title and details.

- `src/components/NewCardForm.tsx`
  - Toggles between an "Add a card" button and a form.
  - Posts new card title/details back to the parent.

- `src/lib/kanban.ts`
  - Defines `Card`, `Column`, and `BoardData` types.
  - Provides `initialData` for the demo board.
  - Includes `moveCard()` for board drag-and-drop logic.
  - Includes `createId()` for new card IDs.

## Existing tests

- `src/components/KanbanBoard.test.tsx`
  - Existing unit test for the board component.

- `src/lib/kanban.test.ts`
  - Existing unit test for the board logic.

## Build and run

- `npm run dev` — start Next.js dev server.
- `npm run build` — build the frontend.
- `npm run start` — run the built app.

## Dependencies

- `next` `16.1.6`
- `react` `19.2.3`
- `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`
- `tailwindcss` `4`
- `vitest`, `@playwright/test`, `@testing-library/react`

## Current limitations

- No backend connectivity.
- No auth flow.
- No persistent storage.
- No AI chat feature.
- Board state is local to the browser session.
