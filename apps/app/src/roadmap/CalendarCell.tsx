import type { BoundCalendarDay, CalendarBubble } from './calendarModel'
import { statusStyleFor, type StatusIconName } from './statusStyles'

interface CalendarCellProps {
  day: BoundCalendarDay
  isToday: boolean
  isCurrentWeek: boolean
  onBubbleClick?: (bubble: CalendarBubble) => void
  onOverflowClick?: (day: BoundCalendarDay) => void
}

function StatusIcon({ name }: { name: StatusIconName }) {
  if (name === 'ti-check') {
    return (
      <svg className="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M5 12l4 4L19 6" />
      </svg>
    )
  }

  if (name === 'ti-clock') {
    return (
      <svg className="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="8" />
        <path d="M12 8v5l3 2" />
      </svg>
    )
  }

  if (name === 'ti-x') {
    return (
      <svg className="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M7 7l10 10" />
        <path d="M17 7L7 17" />
      </svg>
    )
  }

  return (
    <svg className="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </svg>
  )
}

function formatMinutes(minutes: number): string {
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  return rest === 0 ? `${hours}h` : `${hours}h ${rest}m`
}

export function CalendarCell({
  day,
  isToday,
  isCurrentWeek,
  onBubbleClick = () => undefined,
  onOverflowClick = () => undefined,
}: CalendarCellProps) {
  const visibleBubbles = day.bubbles.slice(0, 3)
  const hiddenCount = Math.max(0, day.bubbles.length - visibleBubbles.length)
  const classes = [
    'roadmap-day',
    day.isInMonth ? 'roadmap-day-in-month' : 'roadmap-day-outside',
    isCurrentWeek && 'roadmap-day-current-week',
    isToday && 'roadmap-day-today',
  ].filter(Boolean).join(' ')

  return (
    <div
      className={classes}
      role="gridcell"
      data-date={day.date}
      data-testid={isToday ? 'roadmap-today-cell' : undefined}
    >
      <div className="roadmap-day-head">
        <span className="roadmap-day-number">{day.dayOfMonth}</span>
        {isToday && <span className="roadmap-today-pill">Today</span>}
      </div>

      <div className="roadmap-bubble-stack">
        {visibleBubbles.map((bubble) => {
          const style = statusStyleFor(bubble.status)
          return (
            <button
              key={bubble.id}
              type="button"
              className={`roadmap-bubble ${style.chipClass}`}
              data-status={bubble.status}
              data-icon={style.icon}
              disabled={!day.isInMonth}
              onClick={() => onBubbleClick(bubble)}
              aria-label={`${style.label}: ${bubble.label}, ${formatMinutes(bubble.minutes)}`}
            >
              <StatusIcon name={style.icon} />
              <span className="roadmap-bubble-label">{bubble.label}</span>
              <span className="roadmap-bubble-minutes">{formatMinutes(bubble.minutes)}</span>
            </button>
          )
        })}

        {hiddenCount > 0 && (
          <button
            type="button"
            className="roadmap-overflow"
            disabled={!day.isInMonth}
            onClick={() => onOverflowClick(day)}
          >
            +{hiddenCount} more
          </button>
        )}
      </div>
    </div>
  )
}
