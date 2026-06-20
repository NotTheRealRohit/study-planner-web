import { renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { CalibrationState } from '@study-tracker/progress'
import { useCalibrationState } from './useCalibration'

const mocks = vi.hoisted(() => ({
  getAll: vi.fn(),
  postCalibration: vi.fn(),
}))

vi.mock('../events/useEventStore', () => ({
  useEventStore: () => ({
    getAll: mocks.getAll,
  }),
}))

vi.mock('../lib/intelligenceClient', () => ({
  postCalibration: mocks.postCalibration,
}))

const calibrationState: CalibrationState = {
  globalMultiplier: 1.05,
  globalPosterior: {
    mean: 1.05,
    variance: 0.01,
    sessionCount: 1,
  },
  roleMultipliers: {},
  trend: {
    phases: [],
    currentPhase: null,
    projectionSlope: 0,
    projectionUncertainty: 1,
  },
  promptNeeded: false,
  insightsByContext: [],
  nextSessionForecast: 1.08,
}

const roadmapEvent = {
  id: 1,
  kind: 'RoadmapCreated',
  createdAt: '2026-01-01T00:00:00Z',
  payload: {
    startDate: '2099-01-01',
    deadline: '2099-02-01',
    weeks: 4,
    selectedStudyDays: ['Mon', 'Wed'],
    weekdayHours: 4,
    weekendHours: 0,
    weeklyHours: 4,
    slots: [
      {
        weekIndex: 0,
        dayOfWeek: 'Mon',
        date: '2099-01-01',
        capacityMinutes: 120,
        role: 'anchor',
        candidateMaterialIds: ['m-1'],
        plannedMinutes: 60,
        sessionTitle: 'Foundations',
      },
      {
        weekIndex: 0,
        dayOfWeek: 'Wed',
        date: '2099-01-03',
        capacityMinutes: 120,
        role: 'practice',
        candidateMaterialIds: ['m-2'],
        plannedMinutes: 45,
        sessionTitle: 'Practice',
      },
    ],
  },
}

const sessionEvent = {
  id: 2,
  kind: 'SessionLogged',
  createdAt: '2026-01-02T00:00:00Z',
  payload: {
    date: '2026-01-02',
    source: 'active',
    plannedMinutes: 60,
    activeMinutes: 45,
    duration: 45,
    role: 'anchor',
    startedAt: '2026-01-02T18:00:00Z',
    sessionId: 's-1',
  },
}

describe('useCalibrationState', () => {
  beforeEach(() => {
    mocks.getAll.mockReset()
    mocks.postCalibration.mockReset()
  })

  it('posts mapped events with planned horizon and returns calibration state', async () => {
    mocks.getAll.mockResolvedValue([roadmapEvent, sessionEvent])
    mocks.postCalibration.mockResolvedValue(calibrationState)

    const { result } = renderHook(() => useCalibrationState())

    await waitFor(() => expect(mocks.postCalibration).toHaveBeenCalledTimes(1))
    const body = mocks.postCalibration.mock.calls[0][0]

    expect(body.sessions).toHaveLength(1)
    expect(body.sessions[0].sessionId).toBe('s-1')
    expect(body.nextContext).toMatchObject({
      date: '2099-01-01',
      startedAt: '2099-01-01',
      materialRole: 'anchor',
      session_index: 0,
      planned_horizon: {
        deadline: '2099-02-01',
        planned_total_sessions: 2,
      },
    })
    await waitFor(() => expect(result.current).toEqual(calibrationState))
  })

  it('returns null when the service rejects', async () => {
    mocks.getAll.mockResolvedValue([sessionEvent])
    mocks.postCalibration.mockRejectedValue(new Error('offline'))

    const { result } = renderHook(() => useCalibrationState())

    await waitFor(() => expect(mocks.postCalibration).toHaveBeenCalledTimes(1))
    expect(result.current).toBeNull()
  })
})
