import React from "react";

import { buildHeatmapScale, formatIntensity } from "../utils/heatmap";

export interface DailySummary {
  date: string;
  openTasks: number;
  completedTasks: number;
  newlyAddedTasks: number;
}

export interface CalendarCell {
  date: string;
  summary?: DailySummary;
}

export interface TaskHeatmapProps {
  weeks: CalendarCell[][];
}

export const TaskHeatmap: React.FC<TaskHeatmapProps> = ({ weeks }) => {
  const intensityScale = buildHeatmapScale(weeks);

  return (
    <div className="task-heatmap">
      {weeks.map((week, weekIndex) => (
        <div className="task-heatmap__week" key={`week-${weekIndex}`}>
          {week.map((cell) => {
            const intensity = cell.summary ? intensityScale(cell.summary) : 0;
            return (
              <div
                className="task-heatmap__cell"
                key={cell.date}
                aria-label={buildTooltip(cell)}
                style={{
                  backgroundColor: formatIntensity(intensity),
                }}
              >
                <span className="visually-hidden">{buildTooltip(cell)}</span>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
};

function buildTooltip(cell: CalendarCell): string {
  if (!cell.summary) {
    return `${cell.date}: no activity`;
  }
  return (
    `${cell.date}: ${cell.summary.openTasks} open, ` +
    `${cell.summary.completedTasks} completed, ` +
    `${cell.summary.newlyAddedTasks} added`
  );
}

export default TaskHeatmap;
