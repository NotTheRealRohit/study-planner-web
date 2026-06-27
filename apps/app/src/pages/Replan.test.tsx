import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import type { RoadmapOutput } from '@study-tracker/roadmap-engine'
import type { Event } from '../events/EventStore'
import type { RoadmapCreatedPayload } from '../sync/types'
import { Replan } from './Replan'

const mockState = vi.hoisted(() => ({
  events: [] as Event[],
  logEvent: vi.fn(),
  replanRoadmap: vi.fn(),
  commitReplan: vi.fn(),
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

vi.mock('../roadmap/replan/replanRoadmap', () => ({
  replanRoadmap: mockState.replanRoadmap,
}))

vi.mock('../roadmap/replan/commitReplan', () => ({
  commitReplan: mockState.commitReplan,
}))

function event(kind: string, payload: unknown, createdAt: string): Event {
  return { kind, payload: payload as Record<string, unknown>, createdAt }
}

function roadmapPayload(): RoadmapCreatedPayload {
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
      '2026-05-31T09:00:00.000Z',
    ),
    event('RoadmapCreated', roadmapPayload(), '2026-05-31T10:00:00.000Z'),
  ]
}

function output(): RoadmapOutput {
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
            sessionTitle: 'Read chapter replanned',
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

function renderReplan(initialEntry = '/replan') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/replan" element={<Replan />} />
        <Route path="/roadmap" element={<div>Roadmap reached</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('Replan page', () => {
  beforeEach(() => {
    mockState.events = baseEvents()
    mockState.logEvent.mockReset()
    mockState.replanRoadmap.mockReset()
    mockState.replanRoadmap.mockResolvedValue(output())
    mockState.commitReplan.mockReset()
    mockState.commitReplan.mockResolvedValue(undefined)
  })

  it('renders the preview and pin summary', async () => {
    renderReplan()

    expect(await screen.findByText('Read chapter replanned')).toBeInTheDocument()
    expect(screen.getByText('0 locked, 1 will be re-planned')).toBeInTheDocument()
  })

  it('applies the replan and navigates back to the roadmap', async () => {
    renderReplan()

    fireEvent.click(await screen.findByRole('button', { name: 'Apply' }))

    await waitFor(() => {
      expect(mockState.commitReplan).toHaveBeenCalledWith(expect.objectContaining({
        roadmap: output(),
        events: mockState.events,
        roadmapCreatedAt: '2026-05-31T10:00:00.000Z',
        logEvent: mockState.logEvent,
      }))
    })
    expect(await screen.findByText('Roadmap reached')).toBeInTheDocument()
  })

  it('keeps the current roadmap without committing', async () => {
    renderReplan()

    fireEvent.click(await screen.findByRole('button', { name: 'Keep current' }))

    expect(mockState.commitReplan).not.toHaveBeenCalled()
    expect(await screen.findByText('Roadmap reached')).toBeInTheDocument()
  })

  it('passes extend intent into the regenerate request path', async () => {
    renderReplan('/replan?intent=extend')

    await screen.findByText('Read chapter replanned')

    expect(mockState.replanRoadmap).toHaveBeenCalledWith(
      mockState.events,
      expect.objectContaining({ extendWeeks: 1, offlineFallback: true }),
    )
  })
})
