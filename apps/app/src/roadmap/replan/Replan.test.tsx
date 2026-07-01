import { beforeEach, describe, expect, it, vi } from 'vitest'
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import type { Event } from '../../events/EventStore'
import type { RoadmapCreatedPayload } from '../../sync/types'
import { Replan } from '../../pages/Replan'

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockState = vi.hoisted(() => ({
  events: [] as Event[],
  logEvent: vi.fn(),
  navigate: vi.fn(),
  commitReplan: vi.fn(),
}))

vi.mock('../../events/useEventStore', () => ({
  useEventStore: () => ({
    getAll: vi.fn().mockResolvedValue(mockState.events),
  }),
}))

vi.mock('../../sync/useSync', () => ({
  useSync: () => ({
    logEvent: mockState.logEvent,
    syncState: { status: 'idle', lastSyncedAt: null, pendingCount: 0, lastError: null },
    forceSyncNow: vi.fn(),
  }),
}))

vi.mock('dexie-react-hooks', () => ({
  useLiveQuery: () => mockState.events,
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockState.navigate,
  }
})

// Mock commitReplan so we can inspect the arguments passed from the UI
vi.mock('./commitReplan', () => ({
  commitReplan: (opts: unknown) => mockState.commitReplan(opts),
}))

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function event(kind: string, payload: unknown, createdAt: string): Event {
  return { kind, payload: payload as Record<string, unknown>, createdAt }
}

const ROADMAP_CREATED_AT = '2026-07-01T10:00:00.000Z'
const DEADLINE = '2026-08-01'

function roadmapPayload(overrides: Partial<RoadmapCreatedPayload> = {}): RoadmapCreatedPayload {
  return {
    startDate: '2026-07-01',
    deadline: DEADLINE,
    weeks: 4,
    purpose: 'Systems',
    selectedStudyDays: ['Mon', 'Wed'],
    weekdayHours: 1,
    weekendHours: 0,
    weeklyHours: 2,
    materialIds: ['mat-1', 'mat-2'],
    slots: undefined,
    ...overrides,
  }
}

function baseEvents(): Event[] {
  return [
    event('MaterialAdded', {
      materialId: 'mat-1', title: 'Algo Book', estimatedDuration: 120,
      kind: 'manual', role: 'anchor',
    }, '2026-06-30T09:00:00.000Z'),
    event('MaterialAdded', {
      materialId: 'mat-2', title: 'Practice Set', estimatedDuration: 60,
      kind: 'manual', role: 'practice',
    }, '2026-06-30T09:01:00.000Z'),
    event('RoadmapCreated', roadmapPayload(), ROADMAP_CREATED_AT),
  ]
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('Replan', () => {
  beforeEach(() => {
    mockState.events = baseEvents()
    mockState.logEvent.mockResolvedValue(1)
    mockState.navigate.mockReset()
    mockState.commitReplan.mockReset()
    mockState.commitReplan.mockResolvedValue(undefined)
  })

  function renderReplan(search = '') {
    return render(
      <MemoryRouter initialEntries={[`/replan${search}`]}>
        <Replan />
      </MemoryRouter>,
    )
  }

  it('renders the levers layout — no SchedulePreview', () => {
    renderReplan()
    expect(screen.getByText('Adjust your plan')).toBeInTheDocument()
    expect(screen.getByText('Extend the deadline')).toBeInTheDocument()
    expect(screen.getByText('Study more each week')).toBeInTheDocument()
    expect(screen.getByText('Drop or shorten materials')).toBeInTheDocument()
    expect(screen.queryByTestId('schedule-preview')).not.toBeInTheDocument()
  })

  it('shows the live outcome panel', () => {
    renderReplan()
    expect(screen.getByText('estimate')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Apply changes' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Keep current' })).toBeInTheDocument()
  })

  it('intent=extend pre-selects +1 week preset', () => {
    renderReplan('?intent=extend')
    const plusOneWeek = screen.getByRole('button', { name: '+1 week' })
    expect(plusOneWeek).toHaveAttribute('aria-pressed', 'true')
  })

  it('Keep current navigates without committing', () => {
    renderReplan()
    fireEvent.click(screen.getByRole('button', { name: 'Keep current' }))
    expect(mockState.navigate).toHaveBeenCalledWith('/roadmap')
    expect(mockState.commitReplan).not.toHaveBeenCalled()
  })

  it('Apply changes calls commitReplan and navigates to roadmap', async () => {
    renderReplan()
    fireEvent.click(screen.getByRole('button', { name: 'Apply changes' }))
    await waitFor(() => expect(mockState.navigate).toHaveBeenCalledWith('/roadmap'))
    expect(mockState.commitReplan).toHaveBeenCalledWith(expect.objectContaining({
      roadmapCreatedAt: ROADMAP_CREATED_AT,
    }))
  })

  it('dropping a material removes it from commitReplan materialIds', async () => {
    renderReplan()

    await screen.findByText('Practice Set')

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Drop Practice Set' }))
    })

    expect(screen.getByRole('button', { name: 'Restore Practice Set' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Apply changes' }))
    await waitFor(() => expect(mockState.commitReplan).toHaveBeenCalled())

    const opts = mockState.commitReplan.mock.calls[0][0]
    expect((opts.materialIds as string[]).includes('mat-2')).toBe(false)
    expect((opts.materialIds as string[]).includes('mat-1')).toBe(true)
  })

  it('shortening a material writes materialDurationOverrides to commitReplan', async () => {
    renderReplan()

    await screen.findByText('Algo Book')

    // Shorten mat-1 (120m) by 3 × 15m = 75m remaining
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Shorten Algo Book' }))
    })
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Shorten Algo Book' }))
    })
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Shorten Algo Book' }))
    })

    fireEvent.click(screen.getByRole('button', { name: 'Apply changes' }))
    await waitFor(() => expect(mockState.commitReplan).toHaveBeenCalled())

    const opts = mockState.commitReplan.mock.calls[0][0]
    expect(opts.materialDurationOverrides).toBeDefined()
    expect((opts.materialDurationOverrides as Record<string, number>)['mat-1']).toBe(75)
  })
})
