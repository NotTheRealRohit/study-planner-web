import {
  addDays,
  endOfMonth,
  endOfISOWeek,
  format,
  isSameMonth,
  parseISO,
  startOfMonth,
  startOfISOWeek,
} from 'date-fns'
import type {
  DerivedSlot,
  SlotStatus,
  UnplannedSession,
} from '@study-tracker/progress'
import type { RoadmapSlot } from '@study-tracker/progress'

export interface CalendarDay {
  date: string
  dayOfMonth: number
  isInMonth: boolean
}

export interface MonthGrid {
  monthLabel: string
  monthKey: string
  weeks: CalendarDay[][]
}

export type CalendarBubbleStatus = SlotStatus | 'unplanned'

export interface CalendarBubble {
  id: string
  date: string
  status: CalendarBubbleStatus
  label: string
  materialTitle?: string
  materialId?: string
  sessionTitle?: string | null
  minutes: number
  plannedMinutes?: number
  loggedMinutes?: number
  sessionIds: string[]
  sessionId?: string
  slotRef?: RoadmapSlot
}

export interface BoundCalendarDay extends CalendarDay {
  bubbles: CalendarBubble[]
}

export interface BoundMonthGrid {
  monthLabel: string
  monthKey: string
  weeks: BoundCalendarDay[][]
}

function toDate(monthDate: string | Date): Date {
  return typeof monthDate === 'string' ? parseISO(monthDate) : monthDate
}

function toISODate(date: Date): string {
  return format(date, 'yyyy-MM-dd')
}

export function buildMonthGrid(monthDate: string | Date): MonthGrid {
  const date = toDate(monthDate)
  const monthStart = startOfMonth(date)
  const monthEnd = endOfMonth(date)
  const gridStart = startOfISOWeek(monthStart)
  const gridEnd = endOfISOWeek(monthEnd)
  const weeks: CalendarDay[][] = []

  let cursor = gridStart
  while (cursor <= gridEnd) {
    const week: CalendarDay[] = []
    for (let day = 0; day < 7; day += 1) {
      week.push({
        date: toISODate(cursor),
        dayOfMonth: Number(format(cursor, 'd')),
        isInMonth: isSameMonth(cursor, monthStart),
      })
      cursor = addDays(cursor, 1)
    }
    weeks.push(week)
  }

  return {
    monthLabel: format(monthStart, 'MMMM yyyy'),
    monthKey: format(monthStart, 'yyyy-MM'),
    weeks,
  }
}

function firstMaterialTitle(
  slot: RoadmapSlot,
  materialsById: Map<string, string>,
): string | undefined {
  const materialId = slot.candidateMaterialIds[0]
  if (!materialId) return undefined
  return materialsById.get(materialId)
}

function bubbleForSlot(
  derived: DerivedSlot,
  materialsById: Map<string, string>,
): CalendarBubble {
  const materialId = derived.slot.candidateMaterialIds[0]
  const materialTitle = firstMaterialTitle(derived.slot, materialsById)
  const label =
    derived.slot.sessionTitle?.trim() ||
    materialTitle ||
    (derived.slot.role ? `${derived.slot.role} session` : 'Study session')

  return {
    id: `slot:${derived.slot.weekIndex}:${derived.slot.dayOfWeek}:${derived.slot.date}:${materialId ?? 'rest'}`,
    date: derived.slot.date,
    status: derived.status,
    label,
    materialTitle,
    materialId,
    sessionTitle: derived.slot.sessionTitle ?? null,
    minutes: derived.loggedMinutes > 0 ? derived.loggedMinutes : derived.slot.plannedMinutes,
    plannedMinutes: derived.slot.plannedMinutes,
    loggedMinutes: derived.loggedMinutes,
    sessionIds: derived.sessionIds,
    slotRef: derived.slot,
  }
}

function bubbleForUnplanned(
  session: UnplannedSession,
  materialsById: Map<string, string>,
  index: number,
): CalendarBubble {
  const materialTitle = session.materialId
    ? materialsById.get(session.materialId)
    : undefined

  return {
    id: `unplanned:${session.sessionId ?? index}:${session.date}`,
    date: session.date,
    status: 'unplanned',
    label: materialTitle ?? 'Unplanned session',
    materialTitle,
    materialId: session.materialId,
    minutes: session.minutes,
    sessionIds: session.sessionId ? [session.sessionId] : [],
    sessionId: session.sessionId,
  }
}

export function bindCells(
  grid: MonthGrid,
  derivedSlots: DerivedSlot[],
  unplanned: UnplannedSession[],
  materialsById: Map<string, string>,
): BoundMonthGrid {
  const bubblesByDate = new Map<string, CalendarBubble[]>()

  for (const derived of derivedSlots) {
    const bubbles = bubblesByDate.get(derived.slot.date) ?? []
    bubbles.push(bubbleForSlot(derived, materialsById))
    bubblesByDate.set(derived.slot.date, bubbles)
  }

  unplanned.forEach((session, index) => {
    const bubbles = bubblesByDate.get(session.date) ?? []
    bubbles.push(bubbleForUnplanned(session, materialsById, index))
    bubblesByDate.set(session.date, bubbles)
  })

  return {
    monthLabel: grid.monthLabel,
    monthKey: grid.monthKey,
    weeks: grid.weeks.map((week) =>
      week.map((day) => ({
        ...day,
        bubbles: bubblesByDate.get(day.date) ?? [],
      })),
    ),
  }
}
