import { CalendarCell, DailySummary } from "../components/TaskHeatmap";

type HeatmapScale = (summary: DailySummary) => number;

export function buildHeatmapScale(weeks: CalendarCell[][]): HeatmapScale {
  let maxIntensity = 1;
  for (const week of weeks) {
    for (const cell of week) {
      if (cell.summary) {
        const intensity =
          cell.summary.openTasks +
          cell.summary.completedTasks +
          cell.summary.newlyAddedTasks;
        maxIntensity = Math.max(maxIntensity, intensity);
      }
    }
  }

  return (summary) => {
    const total =
      summary.openTasks + summary.completedTasks + summary.newlyAddedTasks;
    return total / maxIntensity;
  };
}

export function formatIntensity(intensity: number): string {
  const clamped = Math.max(0, Math.min(intensity, 1));
  const opacity = 0.2 + clamped * 0.8;
  return `rgba(30, 102, 197, ${opacity.toFixed(2)})`;
}
