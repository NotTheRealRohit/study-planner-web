import type { Event } from '../events/EventStore'
import type { RoadmapLifecycleEntry } from './roadmapLifecycle'

export interface RoadmapProgressSummary {
  sessionsCount: number
  loggedMinutes: number
  totalPlannedMinutes: number
  toGoMinutes: number
  completedSlots: number
  totalSlots: number
  percentComplete: number
}

function sessionDate(event: Event): string | null {
  const value = event.payload.date
  return typeof value === 'string' ? value : null
}

function sessionMaterialId(event: Event): string | null {
  const value = event.payload.materialId
  return typeof value === 'string' ? value : null
}

function sessionDuration(event: Event): number {
  const value = event.payload.duration
  return typeof value === 'number' ? value : 0
}

export function summarizeRoadmapProgress(
  entry: RoadmapLifecycleEntry,
  events: Event[],
): RoadmapProgressSummary {
  const sessions = events.filter((event) => event.kind === 'SessionLogged')
  const usedSessionIndexes = new Set<number>()
  let completedSlots = 0
  let loggedMinutes = 0

  for (const slot of entry.payload.slots) {
    const matchIndex = sessions.findIndex((session, index) => {
      const materialId = sessionMaterialId(session)
      return (
        !usedSessionIndexes.has(index) &&
        sessionDate(session) === slot.date &&
        materialId !== null &&
        slot.candidateMaterialIds.includes(materialId)
      )
    })

    if (matchIndex === -1) continue

    usedSessionIndexes.add(matchIndex)
    completedSlots += 1
    loggedMinutes += sessionDuration(sessions[matchIndex])
  }

  const totalSlots = entry.payload.slots.length
  const totalPlannedMinutes = entry.payload.slots.reduce(
    (total, slot) => total + slot.plannedMinutes,
    0,
  )
  const percentComplete = totalSlots === 0
    ? 0
    : Math.round((completedSlots / totalSlots) * 100)

  return {
    sessionsCount: completedSlots,
    loggedMinutes,
    totalPlannedMinutes,
    toGoMinutes: Math.max(0, totalPlannedMinutes - loggedMinutes),
    completedSlots,
    totalSlots,
    percentComplete,
  }
}
