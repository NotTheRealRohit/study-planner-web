import type { Event } from '../events/EventStore'
import type {
  RoadmapCreatedPayload,
  RoadmapMarkedAbandonedPayload,
  RoadmapMarkedCompletePayload,
} from '../sync/types'

export type RoadmapLifecycleStatus = 'active' | 'completed' | 'abandoned' | 'superseded'

export interface RoadmapLifecycleEntry {
  roadmapCreatedAt: string
  eventKind: 'RoadmapCreated' | 'RoadmapReplanned'
  status: RoadmapLifecycleStatus
  payload: RoadmapCreatedPayload
  title: string
  startDate: string
  deadline: string
  weeks: number
  totalSlots: number
  completedSlots: number
  percentComplete: number
  resolvedAt?: string
  reason?: string
}

export interface RoadmapLifecycleGroups {
  active: RoadmapLifecycleEntry[]
  completed: RoadmapLifecycleEntry[]
  abandoned: RoadmapLifecycleEntry[]
  superseded: RoadmapLifecycleEntry[]
  all: RoadmapLifecycleEntry[]
}

interface TerminalEvent {
  kind: 'RoadmapMarkedComplete' | 'RoadmapMarkedAbandoned'
  createdAt: string
  payload: RoadmapMarkedCompletePayload | RoadmapMarkedAbandonedPayload
}

function isRoadmapEvent(event: Event): boolean {
  return event.kind === 'RoadmapCreated' || event.kind === 'RoadmapReplanned'
}

function isTerminalEvent(event: Event): event is Event & TerminalEvent {
  return event.kind === 'RoadmapMarkedComplete' || event.kind === 'RoadmapMarkedAbandoned'
}

function eventTime(event: { createdAt: string }): number {
  return new Date(event.createdAt).getTime()
}

function terminalTime(event: TerminalEvent): number {
  return new Date(event.payload.resolvedAt || event.createdAt).getTime()
}

function latestTerminalFor(
  roadmapCreatedAt: string,
  roadmapEventCreatedAt: string,
  terminals: TerminalEvent[],
): TerminalEvent | null {
  const roadmapTime = new Date(roadmapEventCreatedAt).getTime()

  return terminals
    .filter((event) =>
      event.payload.roadmapCreatedAt === roadmapCreatedAt &&
      eventTime(event) >= roadmapTime,
    )
    .sort((a, b) => terminalTime(b) - terminalTime(a))[0] ?? null
}

function completedSlotCount(events: Event[], roadmap: RoadmapCreatedPayload): number {
  const usedSessionIndexes = new Set<number>()
  const sessions = events
    .filter((event) => event.kind === 'SessionLogged')
    .map((event, index) => ({
      index,
      date: event.payload.date as string | undefined,
      materialId: event.payload.materialId as string | undefined,
    }))

  let completed = 0
  for (const slot of roadmap.slots) {
    const match = sessions.find((session) =>
      !usedSessionIndexes.has(session.index) &&
      session.date === slot.date &&
      session.materialId !== undefined &&
      slot.candidateMaterialIds.includes(session.materialId)
    )

    if (match) {
      usedSessionIndexes.add(match.index)
      completed += 1
    }
  }

  return completed
}

function entryTitle(payload: RoadmapCreatedPayload): string {
  return payload.purpose?.trim() || 'Roadmap'
}

export function deriveRoadmapLifecycle(events: Event[]): RoadmapLifecycleGroups {
  const roadmapEvents = events
    .filter(isRoadmapEvent)
    .sort((a, b) => eventTime(a) - eventTime(b))
  const terminals = events
    .filter(isTerminalEvent)
    .sort((a, b) => eventTime(a) - eventTime(b))
  const latestRoadmap = roadmapEvents[roadmapEvents.length - 1] ?? null

  const all = roadmapEvents.map((event) => {
    const payload = event.payload as unknown as RoadmapCreatedPayload
    const terminal = latestTerminalFor(event.createdAt, event.createdAt, terminals)
    const totalSlots = payload.slots.length
    const completedSlots = completedSlotCount(events, payload)
    const percentComplete = totalSlots === 0
      ? 0
      : Math.round((completedSlots / totalSlots) * 100)

    let status: RoadmapLifecycleStatus = 'active'
    if (terminal?.kind === 'RoadmapMarkedComplete') {
      status = 'completed'
    } else if (terminal?.kind === 'RoadmapMarkedAbandoned') {
      status = 'abandoned'
    } else if (latestRoadmap && event.createdAt !== latestRoadmap.createdAt) {
      status = 'superseded'
    }

    return {
      roadmapCreatedAt: event.createdAt,
      eventKind: event.kind as 'RoadmapCreated' | 'RoadmapReplanned',
      status,
      payload,
      title: entryTitle(payload),
      startDate: payload.startDate,
      deadline: payload.deadline,
      weeks: payload.weeks,
      totalSlots,
      completedSlots,
      percentComplete,
      resolvedAt: terminal?.payload.resolvedAt,
      reason: terminal?.payload.reason,
    }
  }).sort((a, b) =>
    new Date(b.roadmapCreatedAt).getTime() - new Date(a.roadmapCreatedAt).getTime()
  )

  return {
    active: all.filter((entry) => entry.status === 'active'),
    completed: all.filter((entry) => entry.status === 'completed'),
    abandoned: all.filter((entry) => entry.status === 'abandoned'),
    superseded: all.filter((entry) => entry.status === 'superseded'),
    all,
  }
}
