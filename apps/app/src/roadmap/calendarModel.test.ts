import { describe, expect, it } from 'vitest'
import type { DerivedSlot, RoadmapSlot, UnplannedSession } from '@study-tracker/progress'
import { bindCells, buildMonthGrid } from './calendarModel'

function makeSlot(overrides: Partial<RoadmapSlot> = {}): RoadmapSlot {
  return {
    date: '2026-03-10',
    dayOfWeek: 'Tuesday',
    weekIndex: 1,
    plannedMinutes: 60,
    candidateMaterialIds: ['mat-1'],
    role: 'anchor',
    sessionTitle: 'Distributed systems · session 1',
    ...overrides,
  }
}

function makeDerivedSlot(
  overrides: Partial<Omit<DerivedSlot, 'slot'>> & { slot?: Partial<RoadmapSlot> } = {},
): DerivedSlot {
  const { slot: slotOverrides, ...derivedOverrides } = overrides
  const slot = makeSlot(slotOverrides)
  return {
    slot,
    status: 'pending',
    loggedMinutes: 0,
    sessionIds: [],
    ...derivedOverrides,
  }
}

describe('calendarModel', () => {
  it('builds a Monday-start grid around a 31-day month that spills into six rows', () => {
    const grid = buildMonthGrid('2026-03-15')

    expect(grid.monthLabel).toBe('March 2026')
    expect(grid.weeks).toHaveLength(6)
    expect(grid.weeks[0][0]).toMatchObject({
      date: '2026-02-23',
      isInMonth: false,
    })
    expect(grid.weeks[0][6].date).toBe('2026-03-01')
    expect(grid.weeks[5][6]).toMatchObject({
      date: '2026-04-05',
      isInMonth: false,
    })
  })

  it('builds February without exceeding the calendar month boundary rows', () => {
    const grid = buildMonthGrid('2026-02-10')
    const dates = grid.weeks.flat().map((day) => day.date)

    expect(grid.monthLabel).toBe('February 2026')
    expect(grid.weeks.length).toBeLessThanOrEqual(6)
    expect(dates).toContain('2026-02-01')
    expect(dates).toContain('2026-02-28')
  })

  it('binds planned slots to their day cells with material titles', () => {
    const grid = buildMonthGrid('2026-03-10')
    const bound = bindCells(
      grid,
      [
        makeDerivedSlot({
          status: 'done',
          loggedMinutes: 52,
          sessionIds: ['session-1'],
        }),
      ],
      [],
      new Map([['mat-1', 'Distributed Systems']]),
    )

    const day = bound.weeks.flat().find((cell) => cell.date === '2026-03-10')

    expect(day?.bubbles).toHaveLength(1)
    expect(day?.bubbles[0]).toMatchObject({
      status: 'done',
      label: 'Distributed systems · session 1',
      materialTitle: 'Distributed Systems',
      minutes: 52,
      plannedMinutes: 60,
      materialId: 'mat-1',
    })
  })

  it('falls back to the material title when a slot has no session title', () => {
    const grid = buildMonthGrid('2026-03-10')
    const bound = bindCells(
      grid,
      [
        makeDerivedSlot({
          slot: {
            sessionTitle: null,
          },
        }),
      ],
      [],
      new Map([['mat-1', 'Operating Systems']]),
    )

    const bubble = bound.weeks.flat().find((cell) => cell.date === '2026-03-10')
      ?.bubbles[0]

    expect(bubble?.label).toBe('Operating Systems')
  })

  it('binds unplanned sessions as their own bubbles', () => {
    const grid = buildMonthGrid('2026-03-10')
    const unplanned: UnplannedSession[] = [
      {
        date: '2026-03-10',
        materialId: 'mat-2',
        minutes: 35,
        sessionId: 'session-unplanned',
      },
    ]
    const bound = bindCells(
      grid,
      [],
      unplanned,
      new Map([['mat-2', 'Office hours']]),
    )

    const bubble = bound.weeks.flat().find((cell) => cell.date === '2026-03-10')
      ?.bubbles[0]

    expect(bubble).toMatchObject({
      status: 'unplanned',
      label: 'Office hours',
      materialTitle: 'Office hours',
      minutes: 35,
      sessionId: 'session-unplanned',
    })
  })
})
