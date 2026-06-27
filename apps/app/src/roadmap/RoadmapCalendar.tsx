import { type TouchEvent, useMemo, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useLiveQuery } from 'dexie-react-hooks'
import { format, parseISO } from 'date-fns'
import { deriveSlotStatuses } from '@study-tracker/progress'
import type { RoadmapInput } from '@study-tracker/progress'
import type { Event } from '../events/EventStore'
import { useEventStore } from '../events/useEventStore'
import { useCalibrationState } from '../progress'
import { mapSessions } from '../progress/mapEvents'
import type {
  MaterialAddedPayload,
  RoadmapCreatedPayload,
  RoadmapEditedPayload,
} from '../sync/types'
import { useSync } from '../sync/useSync'
import { ServiceStatusBanner } from '../components/ServiceStatusBanner'
import { useMatchMedia } from '../lib/useMatchMedia'
import {
  bindCells,
  buildMonthGrid,
  calendarMonthBounds,
  clampMonth,
  monthKeyForDate,
  monthKeyToDate,
  shiftMonth,
  type BoundCalendarDay,
  type CalendarBubble,
  type CalendarMaterial,
} from './calendarModel'
import { CalendarCell } from './CalendarCell'
import { DaySheet } from './DaySheet'
import { MonthNav } from './MonthNav'
import { deriveRoadmapLifecycle } from './roadmapLifecycle'
import { DayDetailModal, SessionDetailModal } from './SessionDetailModal'
import { RoadmapEndedBanner } from './RoadmapEndedBanner'
import { summarizeRoadmapProgress } from './roadmapProgress'
import { logRoadmapEdit } from './edit/logRoadmapEdit'
import { resolveRoadmap as resolveRoadmapEvent, type RoadmapResolutionKind } from './resolveRoadmap'
import { deriveRoadmapEndedState } from './useRoadmapEndedState'
import { LEGEND_ITEMS } from './statusStyles'
import './roadmap.css'

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const DAY_SEQUENCE = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as const

function todayISO(): string {
  return new Date().toISOString().slice(0, 10)
}

function nextDayOfWeek(
  dayOfWeek: string,
  weekIndex: number,
): Pick<RoadmapEditedPayload, 'dayOfWeek' | 'weekIndex'> {
  const index = DAY_SEQUENCE.findIndex((day) => day === dayOfWeek)
  if (index === -1) {
    return { dayOfWeek: 'Mon', weekIndex }
  }

  const nextIndex = (index + 1) % DAY_SEQUENCE.length
  return {
    dayOfWeek: DAY_SEQUENCE[nextIndex],
    weekIndex: weekIndex + (nextIndex === 0 ? 1 : 0),
  }
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

function collectMaterialsById(events: Event[]): Map<string, CalendarMaterial> {
  const materials = new Map<string, CalendarMaterial>()
  for (const event of events) {
    if (event.kind !== 'MaterialAdded') continue
    const payload = event.payload as unknown as MaterialAddedPayload
    materials.set(payload.materialId, {
      title: payload.title,
      url: payload.url,
    })
  }
  return materials
}

function roadmapInputFromPayload(payload: RoadmapCreatedPayload): RoadmapInput {
  return {
    startDate: payload.startDate,
    deadline: payload.deadline,
    weeks: payload.weeks,
    weeklyHours: payload.weeklyHours,
    slots: payload.slots.map((slot) => ({
      date: slot.date,
      dayOfWeek: slot.dayOfWeek,
      weekIndex: slot.weekIndex,
      plannedMinutes: slot.plannedMinutes,
      candidateMaterialIds: slot.candidateMaterialIds,
      role: slot.role,
      sessionTitle: slot.sessionTitle ?? null,
    })),
  }
}

function isEditableBubble(
  bubble: CalendarBubble | null,
  today: string,
  readOnly: boolean,
): bubble is CalendarBubble & { slotRef: NonNullable<CalendarBubble['slotRef']> } {
  return !readOnly && bubble?.slotRef !== undefined && bubble.date >= today
}

interface RoadmapCalendarProps {
  roadmapCreatedAt?: string | null
  readOnly?: boolean
}

export function RoadmapCalendar({
  roadmapCreatedAt = null,
  readOnly = false,
}: RoadmapCalendarProps = {}) {
  const eventStore = useEventStore()
  const navigate = useNavigate()
  const { logEvent } = useSync()
  const events = useLiveQuery(() => eventStore.getAll(), [eventStore])
  const [viewMonth, setViewMonth] = useState<string | null>(null)
  const [slideDirection, setSlideDirection] = useState<'prev' | 'next' | 'today'>('today')
  const [selectedBubble, setSelectedBubble] = useState<CalendarBubble | null>(null)
  const [selectedDay, setSelectedDay] = useState<BoundCalendarDay | null>(null)
  const [selectedSheetDay, setSelectedSheetDay] = useState<BoundCalendarDay | null>(null)
  const touchStartX = useRef<number | null>(null)
  const isMobileCalendar = useMatchMedia('(max-width: 560px)')
  const { status } = useCalibrationState()
  const today = todayISO()
  const loadedEvents = events ?? []

  const lifecycle = useMemo(
    () => deriveRoadmapLifecycle(loadedEvents),
    [loadedEvents],
  )
  const roadmapEnded = useMemo(
    () => deriveRoadmapEndedState(loadedEvents, today),
    [loadedEvents, today],
  )
  const selectedRoadmap = useMemo(() => {
    if (roadmapCreatedAt) {
      return lifecycle.all.find((entry) => entry.roadmapCreatedAt === roadmapCreatedAt) ?? null
    }
    return lifecycle.active[0] ?? null
  }, [lifecycle, roadmapCreatedAt])
  const roadmapPayload = selectedRoadmap?.payload ?? null
  const selectedRoadmapEnded = !readOnly &&
    roadmapEnded.ended &&
    roadmapEnded.entry?.roadmapCreatedAt === selectedRoadmap?.roadmapCreatedAt
  const roadmap = useMemo(
    () => roadmapPayload ? roadmapInputFromPayload(roadmapPayload) : null,
    [roadmapPayload],
  )
  const materialsById = useMemo(
    () => collectMaterialsById(loadedEvents),
    [loadedEvents],
  )
  const monthBounds = useMemo(
    () => roadmap ? calendarMonthBounds(roadmap.startDate, roadmap.deadline) : null,
    [roadmap],
  )
  const activeViewMonth = useMemo(() => {
    if (!monthBounds) return monthKeyForDate(today)
    return clampMonth(monthKeyToDate(viewMonth ?? monthKeyForDate(today)), monthBounds)
  }, [monthBounds, today, viewMonth])

  const calendar = useMemo(() => {
    if (!roadmap) return null
    const sessions = mapSessions(loadedEvents)
    const derived = deriveSlotStatuses(roadmap, sessions, today)
    const grid = buildMonthGrid(monthKeyToDate(activeViewMonth))
    return bindCells(grid, derived.slots, derived.unplanned, materialsById)
  }, [activeViewMonth, loadedEvents, materialsById, roadmap, today])

  const progressSummary = selectedRoadmap
    ? summarizeRoadmapProgress(selectedRoadmap, loadedEvents)
    : null
  const loggedMinutes = progressSummary?.loggedMinutes ?? 0
  const toGoMinutes = progressSummary?.toGoMinutes ?? 0
  const percent = progressSummary?.percentComplete ?? 0

  if (!events) {
    return (
      <div className="roadmap-page">
        <p className="t-body" role="status" style={{ color: 'var(--text-secondary)' }}>
          Loading roadmap...
        </p>
      </div>
    )
  }

  if (!roadmap || !calendar || !monthBounds) {
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
  const handleMonthChange = (
    nextMonth: string,
    direction: 'prev' | 'next' | 'today',
  ) => {
    setSlideDirection(direction)
    setViewMonth(nextMonth)
  }
  const handleDayBubbleSelect = (bubble: CalendarBubble) => {
    setSelectedDay(null)
    setSelectedSheetDay(null)
    setSelectedBubble(bubble)
  }
  const handleOverflowSelect = (day: BoundCalendarDay) => {
    if (isMobileCalendar) {
      setSelectedDay(null)
      setSelectedSheetDay(day)
      return
    }
    setSelectedDay(day)
  }
  const handleMobileDaySelect = (day: BoundCalendarDay) => {
    if (!isMobileCalendar) return
    setSelectedDay(null)
    setSelectedSheetDay(day)
  }
  const handleTouchStart = (event: TouchEvent<HTMLElement>) => {
    if (!isMobileCalendar) return
    touchStartX.current = event.changedTouches[0]?.clientX ?? null
  }
  const handleTouchEnd = (event: TouchEvent<HTMLElement>) => {
    if (!isMobileCalendar || !monthBounds || touchStartX.current === null) return

    const endX = event.changedTouches[0]?.clientX
    if (endX === undefined) return

    const deltaX = endX - touchStartX.current
    touchStartX.current = null

    if (Math.abs(deltaX) < 48) return

    const direction = deltaX < 0 ? 'next' : 'prev'
    const nextMonth = shiftMonth(activeViewMonth, direction === 'next' ? 1 : -1, monthBounds)
    if (nextMonth !== activeViewMonth) {
      handleMonthChange(nextMonth, direction)
      setSelectedSheetDay(null)
    }
  }
  const resolveRoadmap = async (kind: RoadmapResolutionKind) => {
    if (!selectedRoadmap || readOnly) return

    const resolved = await resolveRoadmapEvent({
      kind,
      roadmapCreatedAt: selectedRoadmap.roadmapCreatedAt,
      logEvent,
    })
    if (!resolved) return

    navigate('/roadmaps')
  }
  const editPayloadForBubble = (
    bubble: CalendarBubble,
    overrides: Partial<RoadmapEditedPayload> = {},
  ): RoadmapEditedPayload | null => {
    if (!selectedRoadmap || !bubble.slotRef) return null

    return {
      roadmapCreatedAt: selectedRoadmap.roadmapCreatedAt,
      weekIndex: bubble.slotRef.weekIndex,
      dayOfWeek: bubble.slotRef.dayOfWeek as RoadmapEditedPayload['dayOfWeek'],
      materialId: bubble.materialId ?? null,
      sessionTitle: bubble.sessionTitle ?? bubble.label,
      plannedMinutes: bubble.plannedMinutes ?? bubble.minutes,
      ...overrides,
    }
  }
  const handleLogSession = async (bubble: CalendarBubble) => {
    if (!isEditableBubble(bubble, today, readOnly)) return

    await logEvent('SessionLogged', {
      source: 'manual',
      sessionId: crypto.randomUUID(),
      duration: bubble.plannedMinutes ?? bubble.minutes,
      plannedMinutes: bubble.plannedMinutes,
      date: bubble.date,
      description: bubble.label,
      materialId: bubble.materialId,
      role: bubble.slotRef.role,
      timeOfDay: 'morning',
    })
    setSelectedBubble(null)
  }
  const handleRename = async (bubble: CalendarBubble, title: string) => {
    if (!isEditableBubble(bubble, today, readOnly)) return
    const edit = editPayloadForBubble(bubble, { sessionTitle: title })
    if (!edit) return

    await logRoadmapEdit(logEvent, edit)
    setSelectedBubble(null)
  }
  const handleNudgeMinutes = async (bubble: CalendarBubble, deltaMinutes: number) => {
    if (!isEditableBubble(bubble, today, readOnly)) return
    const currentMinutes = bubble.plannedMinutes ?? bubble.minutes
    const edit = editPayloadForBubble(bubble, {
      plannedMinutes: Math.max(15, currentMinutes + deltaMinutes),
    })
    if (!edit) return

    await logRoadmapEdit(logEvent, edit)
    setSelectedBubble(null)
  }
  const handleMoveNextDay = async (bubble: CalendarBubble) => {
    if (!isEditableBubble(bubble, today, readOnly)) return
    const edit = editPayloadForBubble(
      bubble,
      nextDayOfWeek(bubble.slotRef.dayOfWeek, bubble.slotRef.weekIndex),
    )
    if (!edit) return

    await logRoadmapEdit(logEvent, edit)
    setSelectedBubble(null)
  }
  const handleMarkDone = async (bubble: CalendarBubble) => {
    if (!isEditableBubble(bubble, today, readOnly)) return
    if (bubble.status !== 'done') {
      await handleLogSession(bubble)
    }
    const edit = editPayloadForBubble(bubble)
    if (!edit) return

    await logRoadmapEdit(logEvent, edit)
    setSelectedBubble(null)
  }

  return (
    <div className="roadmap-page">
      <ServiceStatusBanner status={status} />

      {selectedRoadmapEnded && selectedRoadmap && (
        <RoadmapEndedBanner
          entry={selectedRoadmap}
          onMarkComplete={() => void resolveRoadmap('RoadmapMarkedComplete')}
          onAbandon={() => void resolveRoadmap('RoadmapMarkedAbandoned')}
        />
      )}

      {(!readOnly || roadmapCreatedAt != null) && (
        <Link className="roadmap-back-link" to="/roadmaps">
          &larr; Roadmaps
        </Link>
      )}

      <header className="roadmap-header">
        <div>
          <div className="mono-caps">
            {readOnly ? 'Roadmap history' : 'Active roadmap'} · {materialsById.size} materials · {roadmap.weeks} weeks
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
        <MonthNav
          viewMonth={activeViewMonth}
          bounds={monthBounds}
          todayMonth={monthKeyForDate(today)}
          onChange={handleMonthChange}
        />
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
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        <div className="roadmap-weekdays" role="row">
          {WEEKDAY_LABELS.map((label) => (
            <div key={label} className="roadmap-weekday" role="columnheader">
              {label}
            </div>
          ))}
        </div>

        <div
          key={calendar.monthKey}
          className="roadmap-calendar-slide"
          data-direction={slideDirection}
          role="grid"
        >
          {calendar.weeks.map((week) => {
            const isCurrentWeek = week.some((day) => day.date === today)
            return (
              <div key={week[0].date} className="roadmap-week-row" role="row">
                {week.map((day) => (
                  <CalendarCell
                    key={day.date}
                    day={day}
                    isToday={day.date === today}
                    isDeadline={day.date === roadmap.deadline && day.isInMonth}
                    isCurrentWeek={isCurrentWeek}
                    onBubbleClick={setSelectedBubble}
                    onOverflowClick={handleOverflowSelect}
                    onDayClick={handleMobileDaySelect}
                  />
                ))}
              </div>
            )
          })}
        </div>
      </section>

      <footer className="roadmap-footer">
        {readOnly ? (
          <span className="roadmap-readonly-note" data-testid="roadmap-readonly">
            Read-only history view
          </span>
        ) : (
          <>
            <button
              className="btn btn-secondary"
              type="button"
              onClick={() => void resolveRoadmap('RoadmapMarkedComplete')}
            >
              Mark roadmap complete
            </button>
            <button
              className="btn btn-secondary"
              type="button"
              onClick={() => void resolveRoadmap('RoadmapMarkedAbandoned')}
            >
              Abandon roadmap
            </button>
          </>
        )}
        <button className="btn btn-ghost" type="button" disabled>
          Edit roadmap
        </button>
        {readOnly ? (
          <button className="btn btn-ghost" type="button" disabled>
            Replan
          </button>
        ) : (
          <Link className="btn btn-ghost" to="/replan">
            Replan
          </Link>
        )}
      </footer>

      <DayDetailModal
        day={selectedDay}
        onClose={() => setSelectedDay(null)}
        onSelectBubble={handleDayBubbleSelect}
      />
      <DaySheet
        day={selectedSheetDay}
        onClose={() => setSelectedSheetDay(null)}
        onSelectBubble={handleDayBubbleSelect}
      />
      <SessionDetailModal
        bubble={selectedBubble}
        onClose={() => setSelectedBubble(null)}
        canEdit={isEditableBubble(selectedBubble, today, readOnly)}
        onLogSession={(bubble) => void handleLogSession(bubble)}
        onRename={(bubble, title) => void handleRename(bubble, title)}
        onNudgeMinutes={(bubble, deltaMinutes) => void handleNudgeMinutes(bubble, deltaMinutes)}
        onMoveNextDay={(bubble) => void handleMoveNextDay(bubble)}
        onMarkDone={(bubble) => void handleMarkDone(bubble)}
      />
    </div>
  )
}
