import type { RoadmapOutput } from '@study-tracker/roadmap-engine'
import type { Event } from '../../events/EventStore'
import type { RoadmapReplannedPayload } from '../../sync/types'
import { deriveRoadmapLifecycle } from '../roadmapLifecycle'

interface CommitReplanOptions {
  roadmap: RoadmapOutput
  events: Event[]
  roadmapCreatedAt: string
  logEvent: (kind: string, payload: Record<string, unknown>) => Promise<unknown>
  option?: RoadmapReplannedPayload['option']
  deadline?: string
}

export async function commitReplan({
  roadmap,
  events,
  roadmapCreatedAt,
  logEvent,
  option = 'edit',
  deadline,
}: CommitReplanOptions): Promise<void> {
  const lifecycle = deriveRoadmapLifecycle(events)
  const entry = lifecycle.active.find((candidate) =>
    candidate.roadmapCreatedAt === roadmapCreatedAt
  ) ?? lifecycle.all.find((candidate) => candidate.roadmapCreatedAt === roadmapCreatedAt)

  if (!entry) {
    throw new Error('No roadmap found for replan commit')
  }

  const payload: RoadmapReplannedPayload = {
    ...entry.payload,
    roadmapCreatedAt,
    option,
    deadline: deadline ?? entry.payload.deadline,
    weeks: roadmap.weeks.length,
    slots: roadmap.weeks.flatMap((week) => week.slots),
  }

  await logEvent('RoadmapReplanned', payload as unknown as Record<string, unknown>)
}
