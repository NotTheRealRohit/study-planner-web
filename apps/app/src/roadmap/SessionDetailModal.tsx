import type { ReactNode } from 'react'
import { format, parseISO } from 'date-fns'
import type { BoundCalendarDay, CalendarBubble, CalendarBubbleStatus } from './calendarModel'
import { statusStyleFor } from './statusStyles'

interface SessionDetailModalProps {
  bubble: CalendarBubble | null
  onClose: () => void
}

interface DayDetailModalProps {
  day: BoundCalendarDay | null
  onClose: () => void
  onSelectBubble: (bubble: CalendarBubble) => void
}

interface StatusCopy {
  pillLabel: string
  actionLabel: string
}

export function statusCopyFor(status: CalendarBubbleStatus): StatusCopy {
  switch (status) {
    case 'done':
      return { pillLabel: 'Completed', actionLabel: 'View session' }
    case 'pending':
      return { pillLabel: 'Planned', actionLabel: 'Start session' }
    case 'skipped':
      return { pillLabel: 'Skipped', actionLabel: 'Log it late' }
    case 'unplanned':
      return { pillLabel: 'Unplanned', actionLabel: 'View session' }
  }
}

function formatDate(date: string): string {
  return format(parseISO(date), 'EEEE, MMM d')
}

function formatMinutes(minutes: number | undefined): string {
  const safeMinutes = Math.max(0, Math.round(minutes ?? 0))
  if (safeMinutes < 60) return `${safeMinutes}m`
  const hours = Math.floor(safeMinutes / 60)
  const rest = safeMinutes % 60
  return rest === 0 ? `${hours}h` : `${hours}h ${rest}m`
}

function sessionBody(bubble: CalendarBubble): string {
  const planned = bubble.plannedMinutes
  const logged = bubble.loggedMinutes ?? (bubble.status === 'unplanned' ? bubble.minutes : 0)

  if (bubble.status === 'done') {
    return `${formatMinutes(logged)} logged against ${formatMinutes(planned)} planned.`
  }

  if (bubble.status === 'pending') {
    return `${formatMinutes(planned)} planned. Nothing has been logged yet.`
  }

  if (bubble.status === 'skipped') {
    return `${formatMinutes(planned)} planned. No matching session was logged.`
  }

  return `${formatMinutes(logged)} logged outside the roadmap.`
}

function ModalFrame({
  ariaLabel,
  children,
  onClose,
}: {
  ariaLabel: string
  children: ReactNode
  onClose: () => void
}) {
  return (
    <div
      className="modal-overlay center roadmap-modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-label={ariaLabel}
      onClick={onClose}
    >
      <div
        className="modal-card roadmap-modal-card"
        onClick={(event) => event.stopPropagation()}
      >
        <button
          type="button"
          className="roadmap-modal-close"
          aria-label="Close modal"
          onClick={onClose}
        >
          <svg className="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M7 7l10 10" />
            <path d="M17 7L7 17" />
          </svg>
        </button>
        {children}
      </div>
    </div>
  )
}

export function SessionDetailModal({ bubble, onClose }: SessionDetailModalProps) {
  if (!bubble) return null

  const style = statusStyleFor(bubble.status)
  const copy = statusCopyFor(bubble.status)

  return (
    <ModalFrame ariaLabel="Roadmap session detail" onClose={onClose}>
      <div className="modal-eyebrow">{formatDate(bubble.date)}</div>
      <div className="modal-title">{bubble.label}</div>
      <div className="roadmap-modal-status-row">
        <span className={`roadmap-status-pill ${style.chipClass}`} data-status={bubble.status}>
          {copy.pillLabel}
        </span>
      </div>
      <div className="modal-body">
        <p>{sessionBody(bubble)}</p>
        {bubble.materialTitle && (
          <p className="roadmap-modal-material">
            Material:{' '}
            {bubble.materialUrl ? (
              <a href={bubble.materialUrl} target="_blank" rel="noreferrer">
                {bubble.materialTitle}
              </a>
            ) : (
              <span>{bubble.materialTitle}</span>
            )}
          </p>
        )}
      </div>
      <button className="btn btn-accent btn-block" type="button" disabled>
        {copy.actionLabel}
      </button>
    </ModalFrame>
  )
}

export function DayDetailModal({
  day,
  onClose,
  onSelectBubble,
}: DayDetailModalProps) {
  if (!day) return null

  return (
    <ModalFrame ariaLabel="Roadmap day sessions" onClose={onClose}>
      <div className="modal-eyebrow">{formatDate(day.date)}</div>
      <div className="modal-title">Sessions for this day</div>
      <div className="roadmap-day-list">
        {day.bubbles.map((bubble) => {
          const style = statusStyleFor(bubble.status)
          const copy = statusCopyFor(bubble.status)
          return (
            <button
              key={bubble.id}
              type="button"
              className="roadmap-day-list-row"
              onClick={() => onSelectBubble(bubble)}
            >
              <span className={`roadmap-day-list-status ${style.chipClass}`} data-status={bubble.status}>
                {copy.pillLabel}
              </span>
              <span className="roadmap-day-list-title">{bubble.label}</span>
              <span className="roadmap-day-list-minutes">{formatMinutes(bubble.minutes)}</span>
            </button>
          )
        })}
      </div>
    </ModalFrame>
  )
}
