# todoist-helper

## Vision

The frontend will automatically sync with Todoist and maintain a hosted SQL database of all open tasks. This data store keeps an up-to-date mirror of outstanding items so that downstream experiences can query task status in real time without repeatedly hitting the Todoist API.

## Contribution-Style Task Calendar

* Render a calendar heat map inspired by the GitHub contribution grid.
* Color cells by task activity intensity and completion status, highlighting the balance between outstanding and completed tasks.
* Allow users to hover for daily summaries and drill into the underlying tasks.

## Conversational Productivity Copilot

* Provide a chat interface powered by OpenAI's Responses API.
* Orchestrate several specialized agents to help users plan their work:
  * **Web Search Agent** for gathering context from the public web when additional research is needed.
  * **Planning Agent** to determine whether to reuse an existing Todoist project or create a new one, and to organize parent/child tasks.
  * **Scheduling Agent** to arrange tasks on an appropriate cadence that reflects the user's stated preferences and current workload.
* Support natural language references to existing tasks so the assistant can modify, re-sequence, or create new tasks on demand.
* Continuously sync changes back to the SQL task mirror and to Todoist, ensuring parity across the conversational experience, the calendar heat map, and the user's actual task list.

## Next Steps

1. Define the database schema and synchronization pipeline between Todoist and the hosted SQL instance.
2. Prototype the contribution-style calendar component and data aggregation layer.
3. Design agent workflows and prompt templates for planning, scheduling, and search actions.
4. Integrate the conversational UI with the Responses API and underlying agents, ensuring task updates propagate everywhere.


## Quickstart

### Backend API

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the FastAPI server (defaults to http://127.0.0.1:8000):
   ```bash
   uvicorn backend.api:app --reload
   ```
4. The interactive docs are available at http://127.0.0.1:8000/docs once the server is running.

### Frontend Prototype

1. Use Node.js 18+ and install project dependencies from the `frontend` directory:
   ```bash
   cd frontend
   npm install
   ```
2. Start the development server (Vite or your preferred React toolchain):
   ```bash
   npm run dev
   ```
3. Ensure the dev server proxies API requests to the FastAPI backend. With Vite, add the following to `vite.config.ts`:
   ```ts
   export default defineConfig({
     server: {
       proxy: {
         "/heatmap": "http://127.0.0.1:8000",
         "/chat": "http://127.0.0.1:8000",
         "/sync": "http://127.0.0.1:8000",
       },
     },
   });
   ```
4. Visit the frontend (typically http://127.0.0.1:5173) while the backend remains running so API calls succeed.


## Implementation Overview

* The backend schema and synchronization pipeline live in `backend/schema.py` and `backend/sync.py`, providing SQLAlchemy models and sync helpers.
* Contribution calendar data aggregation is handled by `backend/analytics.py` and exposed to the UI via `backend/api.py`.
* Agent workflows and prompt templates are defined in `agents/workflows.py`, which the chat endpoint uses to plan multi-step responses.
* Prototype React components for the calendar and chat integration reside in `frontend/src/components` with shared utilities in `frontend/src/utils`.
