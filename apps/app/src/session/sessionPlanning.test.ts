import { describe, expect, it } from 'vitest';
import type { RoadmapLifecycleEntry } from '../roadmap/roadmapLifecycle';
import type { RoadmapCreatedPayload } from '../sync/types';
import { dailyCapacityForDate, softCapMinutes } from './sessionPlanning';

function entry(payload: Partial<RoadmapCreatedPayload> = {}): RoadmapLifecycleEntry {
  const full: RoadmapCreatedPayload = {
    startDate: '2026-06-01',
    deadline: '2026-07-01',
    weeks: 4,
    selectedStudyDays: ['Mon', 'Wed', 'Sat'],
    weekdayHours: 1,
    weekendHours: 2,
    weeklyHours: 4,
    materialIds: ['mat-1'],
    ...payload,
  };
  return {
    roadmapCreatedAt: '2026-06-01T00:00:00.000Z',
    eventKind: 'RoadmapCreated',
    status: 'active',
    payload: full,
    title: 'Plan',
    startDate: full.startDate,
    deadline: full.deadline,
    weeks: full.weeks,
    totalSlots: 0,
    completedSlots: 0,
    percentComplete: 0,
  };
}

describe('sessionPlanning capacity helpers (D5)', () => {
  it('uses weekday hours on a weekday and weekend hours on a weekend', () => {
    // 2026-06-03 is a Wednesday, 2026-06-06 is a Saturday.
    expect(dailyCapacityForDate(entry(), '2026-06-03')).toBe(60);
    expect(dailyCapacityForDate(entry(), '2026-06-06')).toBe(120);
  });

  it('soft cap subtracts minutes already logged today and floors at zero', () => {
    expect(softCapMinutes(120, 30)).toBe(90);
    expect(softCapMinutes(120, 200)).toBe(0);
    expect(softCapMinutes(0, 0)).toBe(0);
  });

  it('returns zero capacity when there is no active roadmap entry', () => {
    expect(dailyCapacityForDate(undefined, '2026-06-03')).toBe(0);
  });
});
