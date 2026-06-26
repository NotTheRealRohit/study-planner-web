import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useLiveQuery } from 'dexie-react-hooks'
import { format, parseISO } from 'date-fns'
import { deriveSlotStatuses } from '@study-tracker/progress'
import type { Event } from '../events/EventStore'
import { useEventStore } from '../events/useEventStore'
import { useCalibrationState, useProgressSnapshot } from '../progress'
import { findRoadmap, mapSessions } from '../progress/mapEvents'
import type { MaterialAddedPayload, RoadmapCreatedPayload } from '../sync/types'
import { ServiceStatusBanner } from '../components/ServiceStatusBanner'
import { bindCells, buildMonthGrid } from './calendarModel'
import { CalendarCell } from './CalendarCell'
import { LEGEND_ITEMS } from './statusStyles'
import './roadmap.css'

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

function todayISO(): string {
  return new Date().toISOString().slice(0, 10)
}

function formatDateRange(startDate: string, deadline: string): string {
  return `${format(parseISO(startDate), 'MMM d')} to ${format(parseISO(deadline), 'MMM d, yyyy')}`
}

function formatMinutes(totalMinutes: number): string {
  const minutes = Math.max(0, Math.round(totalMinutes))
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  if (hours === 0) return `${rest}m`
  if (rest === 0) return `${hours}h`
  return `${hours}h ${rest}m`
}

function latestRoadmapPayload(events: Event[]): RoadmapCreatedPayload | null {
  const roadmapEvents = events.filter(
    (event) => event.kind === 'RoadmapCreated' || event.kind === 'RoadmapReplanned',
  )
  const latest = roadmapEvents[roadmapEvents.length - 1]
  return latest ? latest.payload as unknown as RoadmapCreatedPayload : null
}

function materialTitlesById(events: Event[]): Map<string, string> {
  const materials = new Map<string, string>()
  for (const event of events) {
    if (event.kind !== 'MaterialAdded') continue
    const payload = event.payload as unknown as MaterialAddedPayload
    materials.set(payload.materialId, payload.title)
  }
  return materials
}

function fallbackProgress(
  plannedMinutes: number,
  loggedMinutes: number,
): { percent: number; toGo: number } {
  if (plannedMinutes <= 0) return { percent: 0, toGo: 0 }
  return {
    percent: Math.min(100, Math.round((loggedMinutes / plannedMinutes) * 100)),
    toGo: Math.max(0, plannedMinutes - loggedMinutes),
  }
}

export function RoadmapCalendar() {
  const eventStore = useEventStore()
  const events = useLiveQuery(() => eventStore.getAll(), [eventStore])
  const { calibration, status } = useCalibrationState()
  const progress = useProgressSnapshot(calibration)
  const today = todayISO()
  const loadedEvents = events ?? []

  const roadmap = useMemo(() => findRoadmap(loadedEvents), [loadedEvents])
  const roadmapPayload = useMemo(
    () => latestRoadmapPayload(loadedEvents),
    [loadedEvents],
  )
  const materialsById = useMemo(
    () => materialTitlesById(loadedEvents),
    [loadedEvents],
  )

  const calendar = useMemo(() => {
    if (!roadmap) return null
    const sessions = mapSessions(loadedEvents)
    const derived = deriveSlotStatuses(roadmap, sessions, today)
    const grid = buildMonthGrid(today)
    return bindCells(grid, derived.slots, derived.unplanned, materialsById)
  }, [loadedEvents, materialsById, roadmap, today])

  const localLoggedMinutes = useMemo(
    () => mapSessions(loadedEvents).reduce((total, session) => total + session.duration, 0),
    [loadedEvents],
  )
  const plannedMinutes = roadmap?.slots.reduce(
    (total, slot) => total + slot.plannedMinutes,
    0,
  ) ?? 0
  const progressFallback = fallbackProgress(plannedMinutes, localLoggedMinutes)
  const loggedMinutes = progress?.totalMinutes ?? localLoggedMinutes
  const toGoMinutes = progress?.totalPlannedMinutes !== undefined && progress.totalMinutes !== undefined
    ? Math.max(0, progress.totalPlannedMinutes - progress.totalMinutes)
    : progressFallback.toGo
  const percent = progress?.completionPercentage ?? progressFallback.percent

  if (!events) {
    return (
      <div className="roadmap-page">
        <p className="t-body" role="status" style={{ color: 'var(--text-secondary)' }}>
          Loading roadmap...
        </p>
      </div>
    )
  }

  if (!roadmap || !calendar) {
    return (
      <div className="roadmap-page roadmap-empty" data-testid="roadmap-empty">
        <div className="roadmap-empty-inner">
          <div className="mono-caps">Active roadmap</div>
          <h1 className="roadmap-empty-title">No active roadmap</h1>
          <p className="t-body" style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-5)' }}>
            Start from onboarding to build a plan, or come back here after your next roadmap is created.
          </p>
          <Link className="btn btn-accent" to="/onboarding">
            Start a roadmap
          </Link>
        </div>
      </div>
    )
  }

  const purpose = roadmapPayload?.purpose
  const title = purpose ? purpose : 'Active roadmap'
  const dateRange = formatDateRange(roadmap.startDate, roadmap.deadline)

  return (
    <div className="roadmap-page">
      <ServiceStatusBanner status={status} />

      <header className="roadmap-header">
        <div>
          <div className="mono-caps">
            Active roadmap · {materialsById.size} materials · {roadmap.weeks} weeks
          </div>
          <h1 className="roadmap-title">{title}</h1>
          <p className="roadmap-subtitle">{dateRange}</p>
        </div>

        <section className="roadmap-progress-card" aria-label="Roadmap progress">
          <div className="roadmap-progress-row">
            <span className="mono-caps">Progress</span>
            <span className="roadmap-progress-percent">{Math.round(percent)}%</span>
          </div>
          <div className="progress" style={{ height: 6, marginBottom: 'var(--space-2)' }}>
            <div className="progress-fill" style={{ width: `${Math.round(percent)}%` }} />
          </div>
          <div className="roadmap-progress-meta">
            <span>{formatMinutes(loggedMinutes)} logged</span>
            <span>{formatMinutes(toGoMinutes)} to go</span>
          </div>
        </section>
      </header>

      <div className="roadmap-toolbar">
        <div>
          <div className="mono-caps">{calendar.monthLabel}</div>
        </div>
        <div className="roadmap-legend" aria-label="Roadmap status legend">
          {LEGEND_ITEMS.map((item) => (
            <span key={item.status} className="roadmap-legend-item">
              <span
                className={`roadmap-legend-swatch ${item.chipClass}`}
                data-status={item.status}
                data-icon={item.icon}
                aria-hidden="true"
              />
              {item.label}
            </span>
          ))}
        </div>
      </div>

      <section
        className="roadmap-calendar-shell"
        data-testid="roadmap-calendar"
        aria-label={`${calendar.monthLabel} roadmap calendar`}
      >
        <div className="roadmap-weekdays" role="row">
          {WEEKDAY_LABELS.map((label) => (
            <div key={label} className="roadmap-weekday" role="columnheader">
              {label}
            </div>
          ))}
        </div>

        <div role="grid">
          {calendar.weeks.map((week) => {
            const isCurrentWeek = week.some((day) => day.date === today)
            return (
              <div key={week[0].date} className="roadmap-week-row" role="row">
                {week.map((day) => (
                  <CalendarCell
                    key={day.date}
                    day={day}
                    isToday={day.date === today}
                    isCurrentWeek={isCurrentWeek}
                  />
                ))}
              </div>
            )
          })}
        </div>
      </section>

      <footer className="roadmap-footer">
        <button className="btn btn-secondary" type="button" disabled>
          Mark roadmap complete
        </button>
        <button className="btn btn-secondary" type="button" disabled>
          Abandon roadmap
        </button>
        <button className="btn btn-ghost" type="button" disabled>
          Edit roadmap
        </button>
        <button className="btn btn-ghost" type="button" disabled>
          Replan
        </button>
      </footer>
    </div>
  )
}
