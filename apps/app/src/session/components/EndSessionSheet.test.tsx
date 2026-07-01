import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { EndSessionSheet } from './EndSessionSheet';
import type { ActiveSessionRecord } from '../types';

function makeRecord(overrides?: Partial<ActiveSessionRecord>): ActiveSessionRecord {
  return {
    id: 1,
    sessionId: 'session-1',
    materialId: 'mat-1',
    sessionTitle: 'Linear Algebra Lecture 4',
    slotDate: '2026-07-01',
    weekIndex: 0,
    plannedMinutes: 50,
    startedAt: '2026-07-01T09:00:00.000Z',
    status: 'active',
    pauseIntervals: [],
    pomodoroConfig: { workMinutes: 50, breakMinutes: 10 },
    materialEstimatedMinutes: 120,
    ...overrides,
  };
}

describe('EndSessionSheet', () => {
  it('logs complete with done position when Done is selected', () => {
    const onComplete = vi.fn();
    const onInterrupt = vi.fn();

    render(
      <EndSessionSheet
        record={makeRecord()}
        unusual={false}
        onUnusualChange={vi.fn()}
        onComplete={onComplete}
        onInterrupt={onInterrupt}
        onCancel={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Done' }));
    fireEvent.click(screen.getByRole('button', { name: 'Log session' }));

    expect(onComplete).toHaveBeenCalledWith({ kind: 'percent', value: 100, ofTotal: 100 });
    expect(onInterrupt).not.toHaveBeenCalled();
  });

  it('logs interrupted when position is not finished', () => {
    const onComplete = vi.fn();
    const onInterrupt = vi.fn();

    render(
      <EndSessionSheet
        record={makeRecord()}
        unusual={false}
        onUnusualChange={vi.fn()}
        onComplete={onComplete}
        onInterrupt={onInterrupt}
        onCancel={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: '75%' }));
    fireEvent.click(screen.getByRole('button', { name: 'Log session' }));

    expect(onInterrupt).toHaveBeenCalledWith({ kind: 'percent', value: 75, ofTotal: 100 });
    expect(onComplete).not.toHaveBeenCalled();
  });
});
