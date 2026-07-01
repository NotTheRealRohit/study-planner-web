import { useEffect, useMemo, useState } from 'react';
import { ROLE_TO_LABEL } from '@study-tracker/roadmap-engine';
import type { SessionSlotData } from './types';
import type { SessionMaterialOption } from './sessionPlanning';
import { withSelectedMaterial } from './sessionPlanning';

interface PreSessionSetupProps {
  initialSlotData?: SessionSlotData;
  materials: SessionMaterialOption[];
  onStart: (slotData: SessionSlotData) => void | Promise<void>;
  onCancel: () => void;
}

function formatMinutes(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest === 0 ? `${hours} hr` : `${hours} hr ${rest} min`;
}

function iconFor(kind: SessionMaterialOption['kind']): string {
  if (kind === 'youtube') return 'YT';
  if (kind === 'article') return 'AR';
  return 'NB';
}

export function PreSessionSetup({
  initialSlotData,
  materials,
  onStart,
  onCancel,
}: PreSessionSetupProps) {
  const [selectedMaterialId, setSelectedMaterialId] = useState(
    initialSlotData?.materialId ?? materials[0]?.materialId ?? '',
  );
  const [plannedMinutes, setPlannedMinutes] = useState(initialSlotData?.plannedMinutes ?? 50);
  const [pickerOpen, setPickerOpen] = useState(false);

  useEffect(() => {
    if (initialSlotData?.materialId) setSelectedMaterialId(initialSlotData.materialId);
    if (initialSlotData?.plannedMinutes) setPlannedMinutes(initialSlotData.plannedMinutes);
  }, [initialSlotData]);

  const selectedMaterial = useMemo(
    () => materials.find((material) => material.materialId === selectedMaterialId) ?? materials[0],
    [materials, selectedMaterialId],
  );

  const maxMinutes = Math.max(30, Math.ceil(Math.max(plannedMinutes, initialSlotData?.plannedMinutes ?? 50) / 15) * 15, 180);
  const startDisabled = !initialSlotData || !selectedMaterial;

  const handleStart = async () => {
    if (!initialSlotData || !selectedMaterial) return;
    await onStart({
      ...withSelectedMaterial(initialSlotData, selectedMaterial),
      plannedMinutes,
      plannedSessionMinutes: plannedMinutes,
    });
  };

  if (!initialSlotData || !selectedMaterial) {
    return (
      <div className="session-layout session-layout-centered">
        <div className="session-frame">
          <div className="session-eyebrow-row eyebrow-faint">Ready to start</div>
          <div className="session-title">Pick something to study</div>
          <div className="session-subtitle">Your material directory is empty for this roadmap.</div>
          <div className="session-actions">
            <button className="btn btn-secondary" onClick={onCancel}>Back home</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="session-layout session-layout-centered">
      <div className="session-frame">
        <div className="session-eyebrow-row eyebrow-clay">
          <span className="session-pulse-dot paused" />
          Ready to start
        </div>
        <div className="session-title">{selectedMaterial.title}</div>
        <div className="session-subtitle">
          Suggested material · {ROLE_TO_LABEL[selectedMaterial.role]} · est ~{formatMinutes(selectedMaterial.remainingEstimatedMinutes || selectedMaterial.estimatedMinutes)}
        </div>

        <div className="material-strip session-setup-strip">
          <div className="material-strip-icon">{iconFor(selectedMaterial.kind)}</div>
          <div className="material-strip-body">
            <div className="material-strip-title">{selectedMaterial.title}</div>
            <div className="material-strip-meta">
              {selectedMaterial.kind.toUpperCase()} · {selectedMaterial.started ? 'in progress' : 'not started'}
            </div>
          </div>
          <button className="btn btn-secondary btn-sm session-setup-change" onClick={() => setPickerOpen(true)}>
            Change
          </button>
        </div>

        <div className="session-dial-wrap">
          <div className="session-dial-face" aria-live="polite">
            <div className="session-dial-value">{formatMinutes(plannedMinutes)}</div>
            <div className="session-dial-label">planned length</div>
          </div>
          <input
            className="session-dial-range"
            aria-label="Planned session length"
            type="range"
            min={5}
            max={maxMinutes}
            step={5}
            value={plannedMinutes}
            onChange={(event) => setPlannedMinutes(Number(event.target.value))}
          />
          <div className="session-dial-meta">
            Recommended {formatMinutes(initialSlotData.plannedMinutes)}
          </div>
        </div>

        <div className="session-actions">
          <button className="btn btn-accent" onClick={() => void handleStart()} disabled={startDisabled}>
            Start session
          </button>
          <button className="btn btn-secondary" onClick={() => setPickerOpen(true)}>
            Pick a different material
          </button>
        </div>
      </div>

      {pickerOpen && (
        <div className="modal-overlay" role="dialog" aria-modal="true" aria-label="Choose material" onClick={() => setPickerOpen(false)}>
          <div className="modal-card session-material-picker" onClick={(event) => event.stopPropagation()}>
            <div className="modal-eyebrow">Choose material</div>
            <div className="modal-title">What do you want to study?</div>
            <div className="chooser">
              {materials.map((material) => (
                <button
                  key={material.materialId}
                  className={`chooser-row${material.materialId === selectedMaterial.materialId ? ' sel' : ''}`}
                  onClick={() => setSelectedMaterialId(material.materialId)}
                >
                  <span className="chooser-radio" />
                  <span className="material-strip-icon chooser-icon">{iconFor(material.kind)}</span>
                  <span className="material-strip-body">
                    <span className="material-strip-title">{material.title}</span>
                    <span className="material-strip-meta">
                      {ROLE_TO_LABEL[material.role]} · {material.done ? 'done' : material.started ? 'in progress' : 'not started'}
                    </span>
                  </span>
                </button>
              ))}
            </div>
            <div className="session-picker-actions">
              <button className="btn btn-secondary btn-sm" onClick={() => setPickerOpen(false)}>Cancel</button>
              <button className="btn btn-primary btn-sm" onClick={() => setPickerOpen(false)}>Use this material</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
