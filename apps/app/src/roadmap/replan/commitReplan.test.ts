import { describe, expect, it, vi } from 'vitest'
import type { RoadmapOutput } from '@study-tracker/roadmap-engine'
import type { Event } from '../../events/EventStore'
import type { RoadmapCreatedPayload } from '../../sync/types'
import { deriveRoadmapLifecycle } from '../roadmapLifecycle'
import { commitReplan } from './commitReplan'

function event(kind: string, payload: unknown, createdAt: string): Event {
  return { kind, payload: payload as Record<string, unknown>, createdAt }
}

function originalPayload(): RoadmapCreatedPayload {
  return {
    startDate: '2026-06-01',
    deadline: '2026-06-30',
    weeks: 4,
    purpose: 'Systems exam',
    selectedStudyDays: ['Mon'],
    weekdayHours: 1,
    weekendHours: 0,
    weeklyHours: 1,
    slots: [
      {
        weekIndex: 0,
        dayOfWeek: 'Mon',
        date: '2026-06-01',
        capacityMinutes: 60,
        role: 'anchor',
        candidateMaterialIds: ['mat-1'],
        plannedMinutes: 60,
        sessionTitle: 'Read chapter',
      },
    ],
  }
}

function regeneratedOutput(): RoadmapOutput {
  return {
    weeks: [
      {
        weekIndex: 0,
        startDate: '2026-06-01',
        slots: [
          {
            weekIndex: 0,
            dayOfWeek: 'Mon',
            date: '2026-06-01',
            capacityMinutes: 60,
            role: 'anchor',
            candidateMaterialIds: ['mat-1'],
            plannedMinutes: 45,
            sessionTitle: 'Read chapter, shorter',
          },
        ],
      },
    ],
    warnings: [],
    capacityCheck: {
      totalCapacityMinutes: 60,
      totalMaterialMinutes: 45,
      status: 'fits',
    },
  }
}

describe('commitReplan', () => {
  it('emits one in-place RoadmapReplanned event and lifecycle keeps one active entry', async () => {
    const originalCreatedAt = '2026-05-31T10:00:00.000Z'
    const events = [
      event('RoadmapCreated', originalPayload(), originalCreatedAt),
    ]
    const logEvent = vi.fn().mockResolvedValue(1)
    const output = regeneratedOutput()

    await commitReplan({
      roadmap: output,
      events,
      roadmapCreatedAt: originalCreatedAt,
      logEvent,
    })

    expect(logEvent).toHaveBeenCalledTimes(1)
    expect(logEvent).toHaveBeenCalledWith('RoadmapReplanned', expect.objectContaining({
      roadmapCreatedAt: originalCreatedAt,
      weeks: 1,
      slots: output.weeks[0].slots,
    }))

    const payload = logEvent.mock.calls[0][1]
    const groups = deriveRoadmapLifecycle([
      ...events,
      event('RoadmapReplanned', payload, '2026-06-10T00:00:00.000Z'),
    ])

    expect(groups.active).toHaveLength(1)
    expect(groups.active[0].roadmapCreatedAt).toBe(originalCreatedAt)
    expect(groups.active[0].payload.slots).toEqual(output.weeks[0].slots)
  })
})
