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
