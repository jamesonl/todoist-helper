import type { CalendarCell } from "../components/TaskHeatmap";

interface HeatmapResponse {
  weeks: {
    date: string;
    summary: {
      date: string;
      openTasks: number;
      completedTasks: number;
      newlyAddedTasks: number;
    } | null;
  }[][];
}

export async function fetchHeatmap(days = 70): Promise<CalendarCell[][]> {
  const response = await fetch(`/heatmap?days=${days}`);
  if (!response.ok) {
    throw new Error(`Failed to load heatmap: ${response.status}`);
  }
  const json: HeatmapResponse = await response.json();
  return json.weeks.map((week) =>
    week.map((cell) => ({
      date: cell.date,
      summary: cell.summary
        ? {
            date: cell.summary.date,
            openTasks: cell.summary.openTasks,
            completedTasks: cell.summary.completedTasks,
            newlyAddedTasks: cell.summary.newlyAddedTasks,
          }
        : undefined,
    }))
  );
}
