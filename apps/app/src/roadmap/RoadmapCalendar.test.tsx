import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
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
    materialIds: ['mat-1', 'mat-2'],
    slots: undefined,
    ...overrides,
  }
}

function event(kind: string, payload: unknown, createdAt: string): Event {
  return { kind, payload: payload as Record<string, unknown>, createdAt }
}

function baseEvents(): Event[] {
  const roadmapCreatedAt = '2026-05-01T09:00:00.000Z'
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
    event(
      'MaterialAdded',
      {
        materialId: 'mat-2',
        title: 'Operating Systems',
        estimatedDuration: 90,
        kind: 'manual',
        role: 'foundation',
      },
      '2026-05-01T08:05:00.000Z',
    ),
    event('RoadmapCreated', roadmapPayload(), roadmapCreatedAt),
    event(
      'SessionBooked',
      {
        roadmapCreatedAt,
        bookingId: 'booking-1',
        date: '2099-06-03',
        estimatedDuration: 60,
        materialId: 'mat-1',
      },
      '2026-05-01T09:01:00.000Z',
    ),
    event(
      'SessionBooked',
      {
        roadmapCreatedAt,
        bookingId: 'booking-blank',
        date: '2099-06-10',
        estimatedDuration: 45,
      },
      '2026-05-01T09:02:00.000Z',
    ),
  ]
}

function renderCalendar(readOnly = false) {
  return render(
    <MemoryRouter>
      <RoadmapCalendar readOnly={readOnly} />
    </MemoryRouter>,
  )
}

function renderHistoricalCalendar() {
  return render(
    <MemoryRouter>
      <RoadmapCalendar roadmapCreatedAt="2026-05-01T09:00:00.000Z" readOnly />
    </MemoryRouter>,
  )
}

function openBookingEditor(name = /Booked: Distributed Systems, 1h/) {
  fireEvent.click(screen.getByRole('button', { name }))
}

describe('RoadmapCalendar booking interactions', () => {
  beforeEach(() => {
    mockState.events = baseEvents()
    mockState.logEvent.mockReset()
    mockState.logEvent.mockResolvedValue(1)
  })

  it('renders booking statuses instead of slot statuses', () => {
    renderCalendar()

    expect(screen.getByRole('button', { name: /Booked: Distributed Systems, 1h/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Booked: Session · pick at start, 45m/ })).toBeInTheDocument()
    expect(screen.getByLabelText('Projected finish')).toHaveTextContent('estimate')
  })

  it('edits a future booking by emitting BookingEdited', async () => {
    renderCalendar()
    openBookingEditor()

    fireEvent.click(screen.getByRole('button', { name: 'Change material' }))
    fireEvent.click(screen.getByRole('button', { name: /Operating Systems/ }))
    fireEvent.click(screen.getByRole('button', { name: 'Use this material' }))
    fireEvent.click(screen.getByLabelText('Increase booking duration'))
    fireEvent.change(screen.getByLabelText('Booking date'), {
      target: { value: '2099-06-04' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Done' }))

    await waitFor(() => {
      expect(mockState.logEvent).toHaveBeenCalledWith('BookingEdited', {
        roadmapCreatedAt: '2026-05-01T09:00:00.000Z',
        bookingId: 'booking-1',
        date: '2099-06-04',
        estimatedDuration: 75,
        materialId: 'mat-2',
      })
    })
  })

  it('removes a future booking by emitting BookingCleared', async () => {
    renderCalendar()
    openBookingEditor()

    fireEvent.click(screen.getByRole('button', { name: 'Remove booking' }))

    await waitFor(() => {
      expect(mockState.logEvent).toHaveBeenCalledWith('BookingCleared', {
        roadmapCreatedAt: '2026-05-01T09:00:00.000Z',
        bookingId: 'booking-1',
      })
    })
  })

  it('adds a session on an empty day by emitting SessionBooked', async () => {
    renderCalendar()

    fireEvent.click(screen.getAllByRole('button', { name: '+ add session' })[0])
    fireEvent.click(screen.getByRole('button', { name: /Attach/ }))
    fireEvent.click(screen.getByRole('button', { name: /Operating Systems/ }))
    fireEvent.click(screen.getByRole('button', { name: 'Use this material' }))
    fireEvent.click(screen.getByLabelText('Decrease new session duration'))
    fireEvent.click(screen.getByRole('button', { name: 'Add session' }))

    await waitFor(() => {
      expect(mockState.logEvent).toHaveBeenCalledWith('SessionBooked', expect.objectContaining({
        roadmapCreatedAt: '2026-05-01T09:00:00.000Z',
        date: expect.stringMatching(/^2099-06-/),
        estimatedDuration: 45,
        materialId: 'mat-2',
      }))
    })
  })

  it('marks material progress without emitting SessionLogged', async () => {
    renderCalendar()

    const directory = screen.getByLabelText('Materials directory')
    fireEvent.click(within(directory).getAllByRole('button', { name: 'Mark progress' })[0])
    fireEvent.change(screen.getByLabelText('Material progress percent'), {
      target: { value: '50' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Save progress' }))

    await waitFor(() => {
      expect(mockState.logEvent).toHaveBeenCalledWith('MaterialProgressMarked', expect.objectContaining({
        roadmapCreatedAt: '2026-05-01T09:00:00.000Z',
        materialId: 'mat-1',
        materialPosition: { kind: 'percent', value: 50 },
        source: 'directory',
      }))
    })
    expect(mockState.logEvent).not.toHaveBeenCalledWith('SessionLogged', expect.anything())
  })

  it('keeps booking controls out of read-only history mode', () => {
    renderHistoricalCalendar()

    openBookingEditor()

    expect(screen.queryByRole('dialog', { name: 'Edit booking' })).not.toBeInTheDocument()
    expect(screen.getByText('View booking')).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: 'Mark progress' })[0]).toBeDisabled()
    expect(screen.getByRole('link', { name: /Roadmaps/ })).toHaveAttribute('href', '/roadmaps')
  })
})
