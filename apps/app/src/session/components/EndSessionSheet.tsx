import { useEffect, useState } from 'react';
import type { ActiveSessionRecord, MaterialPosition } from '../types';

export interface EndSessionSheetProps {
  record: ActiveSessionRecord;
  unusual: boolean;
  onUnusualChange: (value: boolean) => void;
  onComplete: (position: MaterialPosition) => void | Promise<void>;
  onInterrupt: (position: MaterialPosition) => void | Promise<void>;
  onCancel: () => void;
}

export function EndSessionSheet({
  record,
  unusual,
  onUnusualChange,
  onComplete,
  onInterrupt,
  onCancel,
}: EndSessionSheetProps) {
  const startPercent = record.materialStartPosition?.kind === 'percent'
    ? Math.round(record.materialStartPosition.value)
    : 0;
  const [position, setPosition] = useState(Math.max(0, Math.min(100, startPercent || 50)));
  const [finished, setFinished] = useState(position >= 100);

  useEffect(() => {
    setFinished(position >= 100);
  }, [position]);

  const materialPosition: MaterialPosition = {
    kind: 'percent',
    value: finished ? 100 : position,
    ofTotal: 100,
  };

  const handleLog = async () => {
    if (finished) await onComplete(materialPosition);
    else await onInterrupt(materialPosition);
  };

  return (
    <div className="modal-overlay session-end-overlay" role="dialog" aria-modal="true" aria-label="End session">
      <div className="modal-card session-end-sheet">
        <div className="modal-eyebrow">End session</div>
        <div className="modal-title">{record.sessionTitle}</div>

        <div className="session-position-presets" aria-label="Material position">
          {[25, 50, 75, 100].map((preset) => (
            <button
              key={preset}
              className={`btn btn-sm ${position === preset ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setPosition(preset)}
            >
              {preset === 100 ? 'Done' : `${preset}%`}
            </button>
          ))}
        </div>

        <label className="field-group session-position-slider">
          <span className="field-label">Current position</span>
          <input
            className="session-dial-range"
            type="range"
            min={0}
            max={100}
            step={5}
            value={position}
            onChange={(event) => setPosition(Number(event.target.value))}
          />
          <span className="field-helper">{finished ? 'Finished' : `${position}% complete`}</span>
        </label>

        <div className="session-completion-choice">
          <button
            className={`session-choice${finished ? ' selected' : ''}`}
            onClick={() => setFinished(true)}
          >
            <span className="session-choice-title">Finished</span>
            <span className="session-choice-copy">Mark this material complete.</span>
          </button>
          <button
            className={`session-choice${!finished ? ' selected' : ''}`}
            onClick={() => setFinished(false)}
          >
            <span className="session-choice-title">Keep open</span>
            <span className="session-choice-copy">Log the work and continue later.</span>
          </button>
        </div>

        <button
          className={`checkbox-row${unusual ? ' checked' : ''}`}
          onClick={() => onUnusualChange(!unusual)}
          type="button"
        >
          <span className={`checkbox-box${unusual ? ' checked' : ''}`} />
          <span className="checkbox-body">
            <span className="checkbox-title">This was unusual</span>
          </span>
        </button>

        <div className="session-picker-actions">
          <button className="btn btn-secondary btn-sm" onClick={onCancel}>Cancel</button>
          <button className="btn btn-accent btn-sm" onClick={() => void handleLog()}>Log session</button>
        </div>
      </div>
    </div>
  );
}
