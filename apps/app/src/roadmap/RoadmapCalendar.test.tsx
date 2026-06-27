import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import type { Event } from '../events/EventStore'
import type { RoadmapCreatedPayload } from '../sync/types'
import { RoadmapCalendar } from './RoadmapCalendar'

const mockState = vi.hoisted(() => ({
  events: [] as Event[],
  logEvent: vi.fn(),
}))

vi.mock('../events/useEventStore', () => ({
  useEventStore: () => ({
    getAll: vi.fn().mockResolvedValue(mockState.events),
  }),
}))

vi.mock('../sync/useSync', () => ({
  useSync: () => ({
    logEvent: mockState.logEvent,
    syncState: { status: 'idle', lastSyncedAt: null, pendingCount: 0, lastError: null },
    forceSyncNow: vi.fn(),
  }),
}))

vi.mock('dexie-react-hooks', () => ({
  useLiveQuery: () => mockState.events,
}))

vi.mock('../progress', () => ({
  useCalibrationState: () => ({ calibration: null, status: 'ready' }),
  useProgressSnapshot: () => null,
}))

vi.mock('../lib/useMatchMedia', () => ({
  useMatchMedia: () => false,
}))

function roadmapPayload(overrides: Partial<RoadmapCreatedPayload> = {}): RoadmapCreatedPayload {
  return {
    startDate: '2099-06-01',
    deadline: '2099-06-30',
    weeks: 4,
    purpose: 'Systems',
    selectedStudyDays: ['Mon', 'Wed'],
    weekdayHours: 1,
    weekendHours: 0,
    weeklyHours: 2,
    slots: [
      {
        date: '2099-06-03',
        dayOfWeek: 'Wed',
        weekIndex: 0,
        plannedMinutes: 60,
        capacityMinutes: 60,
        candidateMaterialIds: ['mat-1'],
        role: 'anchor',
        sessionTitle: 'Read chapter',
      },
    ],
    ...overrides,
  }
}

function event(kind: string, payload: unknown, createdAt: string): Event {
  return { kind, payload: payload as Record<string, unknown>, createdAt }
}

function baseEvents(): Event[] {
  return [
    event(
      'MaterialAdded',
      {
        materialId: 'mat-1',
        title: 'Distributed Systems',
        estimatedDuration: 120,
        kind: 'article',
        role: 'anchor',
      },
      '2026-05-01T08:00:00.000Z',
    ),
    event('RoadmapCreated', roadmapPayload(), '2026-05-01T09:00:00.000Z'),
  ]
}

function renderCalendar(readOnly = false) {
  return render(
    <MemoryRouter>
      <RoadmapCalendar readOnly={readOnly} />
    </MemoryRouter>,
  )
}

function openPlannedBubble() {
  fireEvent.click(screen.getByRole('button', { name: /Planned: Read chapter, 1h/ }))
}

describe('RoadmapCalendar quick actions', () => {
  beforeEach(() => {
    mockState.events = baseEvents()
    mockState.logEvent.mockReset()
    mockState.logEvent.mockResolvedValue(1)
  })

  it('logs a session with the tapped slot date and material', async () => {
    renderCalendar()
    openPlannedBubble()

    fireEvent.click(screen.getByRole('button', { name: 'Log session' }))

    await waitFor(() => {
      expect(mockState.logEvent).toHaveBeenCalledWith('SessionLogged', expect.objectContaining({
        source: 'manual',
        date: '2099-06-03',
        materialId: 'mat-1',
        duration: 60,
      }))
    })
  })

  it('renames a future slot by emitting RoadmapEdited', async () => {
    renderCalendar()
    openPlannedBubble()

    fireEvent.change(screen.getByLabelText('Session title'), {
      target: { value: 'Read chapter revised' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Save title' }))

    await waitFor(() => {
      expect(mockState.logEvent).toHaveBeenCalledWith('RoadmapEdited', {
        roadmapCreatedAt: '2026-05-01T09:00:00.000Z',
        weekIndex: 0,
        dayOfWeek: 'Wed',
        materialId: 'mat-1',
        sessionTitle: 'Read chapter revised',
        plannedMinutes: 60,
      })
    })
  })

  it('hides quick actions in read-only history mode', () => {
    renderCalendar(true)
    openPlannedBubble()

    expect(screen.queryByRole('button', { name: 'Log session' })).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Session title')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Start session' })).toBeDisabled()
  })
})
