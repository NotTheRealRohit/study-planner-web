import { describe, expect, it } from 'vitest'
import type { Event } from '../events/EventStore'
import type { RoadmapCreatedPayload } from '../sync/types'
import { findActiveRoadmap, findRoadmap, mapSessions } from './mapEvents'

function roadmapPayload(overrides: Partial<RoadmapCreatedPayload> = {}): RoadmapCreatedPayload {
  return {
    startDate: '2026-06-01',
    deadline: '2026-07-01',
    weeks: 4,
    purpose: 'Distributed systems',
    selectedStudyDays: ['Mon', 'Wed'],
    weekdayHours: 1,
    weekendHours: 2,
    weeklyHours: 4,
    slots: [
      {
        date: '2026-06-03',
        dayOfWeek: 'Wed',
        weekIndex: 0,
        plannedMinutes: 60,
        capacityMinutes: 60,
        candidateMaterialIds: ['mat-1'],
        role: 'anchor',
        sessionTitle: 'Read chapter 1',
      },
    ],
    ...overrides,
  }
}

function event(kind: string, payload: unknown, createdAt: string): Event {
  return { kind, payload: payload as Record<string, unknown>, createdAt }
}

describe('mapEvents roadmap resolution', () => {
  it('returns null when the latest roadmap is abandoned with no successor', () => {
    const createdAt = '2026-06-01T00:00:00.000Z'
    const events = [
      event('RoadmapCreated', roadmapPayload(), createdAt),
      event(
        'RoadmapMarkedAbandoned',
        {
          roadmapCreatedAt: createdAt,
          resolvedAt: '2026-06-20T00:00:00.000Z',
        },
        '2026-06-20T00:00:00.000Z',
      ),
    ]

    expect(findActiveRoadmap(events)).toBeNull()
  })

  it('returns null when the latest roadmap is completed with no successor', () => {
    const createdAt = '2026-06-01T00:00:00.000Z'
    const events = [
      event('RoadmapCreated', roadmapPayload(), createdAt),
      event(
        'RoadmapMarkedComplete',
        {
          roadmapCreatedAt: createdAt,
          resolvedAt: '2026-06-20T00:00:00.000Z',
        },
        '2026-06-20T00:00:00.000Z',
      ),
    ]

    expect(findActiveRoadmap(events)).toBeNull()
  })

  it('tracks a new active roadmap after abandoning an older one', () => {
    const firstCreatedAt = '2026-06-01T00:00:00.000Z'
    const secondCreatedAt = '2026-07-01T00:00:00.000Z'
    const active = findActiveRoadmap([
      event('RoadmapCreated', roadmapPayload({ purpose: 'Old plan' }), firstCreatedAt),
      event(
        'RoadmapMarkedAbandoned',
        {
          roadmapCreatedAt: firstCreatedAt,
          resolvedAt: '2026-06-20T00:00:00.000Z',
        },
        '2026-06-20T00:00:00.000Z',
      ),
      event(
        'RoadmapCreated',
        roadmapPayload({
          purpose: 'New plan',
          startDate: '2026-07-01',
          deadline: '2026-08-01',
          slots: [
            {
              ...roadmapPayload().slots[0],
              date: '2026-07-03',
              sessionTitle: 'New plan session',
            },
          ],
        }),
        secondCreatedAt,
      ),
    ])

    expect(active?.startDate).toBe('2026-07-01')
    expect(active?.deadline).toBe('2026-08-01')
    expect(active?.slots[0].sessionTitle).toBe('New plan session')
  })

  it('keeps replan parity with the old latest-roadmap resolver while active', () => {
    const createdAt = '2026-06-01T00:00:00.000Z'
    const events = [
      event('RoadmapCreated', roadmapPayload({ purpose: 'Original' }), createdAt),
      event(
        'RoadmapReplanned',
        {
          ...roadmapPayload({
            purpose: 'Replanned',
            deadline: '2026-08-01',
            slots: [
              {
                ...roadmapPayload().slots[0],
                plannedMinutes: 90,
                sessionTitle: 'Replanned session',
              },
            ],
          }),
          roadmapCreatedAt: createdAt,
        },
        '2026-06-10T00:00:00.000Z',
      ),
    ]

    expect(findActiveRoadmap(events)).toEqual(findRoadmap(events))
    expect(findActiveRoadmap(events)?.deadline).toBe('2026-08-01')
    expect(findActiveRoadmap(events)?.slots[0]).toMatchObject({
      plannedMinutes: 90,
      sessionTitle: 'Replanned session',
    })
  })

  it('keeps session mapping global after a roadmap is abandoned', () => {
    const createdAt = '2026-06-01T00:00:00.000Z'
    const events = [
      event('RoadmapCreated', roadmapPayload(), createdAt),
      event(
        'RoadmapMarkedAbandoned',
        {
          roadmapCreatedAt: createdAt,
          resolvedAt: '2026-06-20T00:00:00.000Z',
        },
        '2026-06-20T00:00:00.000Z',
      ),
      event(
        'SessionLogged',
        {
          date: '2026-06-03',
          source: 'active',
          plannedMinutes: 60,
          duration: 45,
          materialId: 'mat-1',
          role: 'anchor',
          sessionId: 's-1',
        },
        '2026-06-03T12:00:00.000Z',
      ),
    ]

    expect(findActiveRoadmap(events)).toBeNull()
    expect(mapSessions(events)).toHaveLength(1)
    expect(mapSessions(events)[0]).toMatchObject({
      sessionId: 's-1',
      duration: 45,
    })
  })
})
