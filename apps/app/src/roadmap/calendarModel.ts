import {
  addDays,
  addMonths,
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

export interface MonthBounds {
  startMonth: string
  endMonth: string
}

export type CalendarBubbleStatus = SlotStatus | 'unplanned'

export interface CalendarMaterial {
  title: string
  url?: string
}

export interface CalendarBubble {
  id: string
  date: string
  status: CalendarBubbleStatus
  label: string
  materialTitle?: string
  materialUrl?: string
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

export function monthKeyForDate(monthDate: string | Date): string {
  return format(startOfMonth(toDate(monthDate)), 'yyyy-MM')
}

export function monthKeyToDate(monthKey: string): Date {
  return parseISO(`${monthKey}-01`)
}

export function calendarMonthBounds(startDate: string, deadline: string): MonthBounds {
  const startMonth = monthKeyForDate(startDate)
  const endMonth = monthKeyForDate(deadline)

  if (startMonth > endMonth) {
    return { startMonth: endMonth, endMonth: startMonth }
  }

  return { startMonth, endMonth }
}

export function clampMonth(monthDate: string | Date, bounds: MonthBounds): string {
  const monthKey = monthKeyForDate(monthDate)
  if (monthKey < bounds.startMonth) return bounds.startMonth
  if (monthKey > bounds.endMonth) return bounds.endMonth
  return monthKey
}

export function shiftMonth(monthKey: string, offset: number, bounds: MonthBounds): string {
  return clampMonth(addMonths(monthKeyToDate(monthKey), offset), bounds)
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

function materialInfoById(
  materialId: string | undefined,
  materialsById: Map<string, string | CalendarMaterial>,
): CalendarMaterial | undefined {
  if (!materialId) return undefined
  const material = materialsById.get(materialId)
  if (!material) return undefined
  if (typeof material === 'string') return { title: material }
  return material
}

function firstMaterialTitle(
  slot: RoadmapSlot,
  materialsById: Map<string, string | CalendarMaterial>,
): string | undefined {
  const materialId = slot.candidateMaterialIds[0]
  return materialInfoById(materialId, materialsById)?.title
}

function bubbleForSlot(
  derived: DerivedSlot,
  materialsById: Map<string, string | CalendarMaterial>,
): CalendarBubble {
  const materialId = derived.slot.candidateMaterialIds[0]
  const materialInfo = materialInfoById(materialId, materialsById)
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
    materialUrl: materialInfo?.url,
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
  materialsById: Map<string, string | CalendarMaterial>,
  index: number,
): CalendarBubble {
  const materialInfo = materialInfoById(session.materialId, materialsById)
  const materialTitle = materialInfo?.title

  return {
    id: `unplanned:${session.sessionId ?? index}:${session.date}`,
    date: session.date,
    status: 'unplanned',
    label: materialTitle ?? 'Unplanned session',
    materialTitle,
    materialUrl: materialInfo?.url,
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
  materialsById: Map<string, string | CalendarMaterial>,
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
