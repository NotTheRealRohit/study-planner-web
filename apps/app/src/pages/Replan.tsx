import { useEffect, useMemo, useState } from 'react'
import { addDays, format, parseISO } from 'date-fns'
import { useLiveQuery } from 'dexie-react-hooks'
import { useLocation, useNavigate } from 'react-router-dom'
import type { RoadmapOutput } from '@study-tracker/roadmap-engine'
import { SchedulePreview, formatMinutes } from '../onboarding/components/SchedulePreview'
import { useEventStore } from '../events/useEventStore'
import { useSync } from '../sync/useSync'
import { deriveRoadmapLifecycle } from '../roadmap/roadmapLifecycle'
import {
  mapToRegenerateRequest,
  type RoadmapRegenerateRequest,
} from '../roadmap/replan/mapToRegenerateRequest'
import { replanRoadmap } from '../roadmap/replan/replanRoadmap'
import { commitReplan } from '../roadmap/replan/commitReplan'
import '../roadmap/roadmap.css'

function todayISO(): string {
  return new Date().toISOString().slice(0, 10)
}

function extendDeadline(deadline: string): string {
  return format(addDays(parseISO(deadline), 7), 'yyyy-MM-dd')
}

function withExtendedWeeks(
  request: RoadmapRegenerateRequest,
  extendWeeks: number,
): RoadmapRegenerateRequest {
  if (extendWeeks <= 0) return request

  return {
    ...request,
    input: {
      ...request.input,
      weeks: request.input.weeks + extendWeeks,
    },
  }
}

function slotCount(roadmap: RoadmapOutput | null): number {
  return roadmap?.weeks.reduce((total, week) => total + week.slots.length, 0) ?? 0
}

export function Replan() {
  const eventStore = useEventStore()
  const { logEvent } = useSync()
  const location = useLocation()
  const navigate = useNavigate()
  const [today] = useState(todayISO)
  const [roadmap, setRoadmap] = useState<RoadmapOutput | null>(null)
  const [loading, setLoading] = useState(false)
  const [applying, setApplying] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const events = useLiveQuery(() => eventStore.getAll(), [eventStore])
  const loadedEvents = useMemo(() => events ?? [], [events])
  const intent = new URLSearchParams(location.search).get('intent')
  const extendWeeks = intent === 'extend' ? 1 : 0

  const lifecycle = useMemo(() => deriveRoadmapLifecycle(loadedEvents), [loadedEvents])
  const activeEntry = lifecycle.active[0] ?? null
  const requestState = useMemo(() => {
    if (!events) return null
    try {
      return {
        request: withExtendedWeeks(
          mapToRegenerateRequest(loadedEvents, today),
          extendWeeks,
        ),
        error: null,
      }
    } catch (err) {
      return {
        request: null,
        error: err instanceof Error ? err.message : 'Could not build replan request',
      }
    }
  }, [events, loadedEvents, today, extendWeeks])

  useEffect(() => {
    if (!events || !requestState?.request) return

    let cancelled = false
    setLoading(true)
    setError(null)

    replanRoadmap(loadedEvents, {
      today,
      offlineFallback: true,
      extendWeeks,
    })
      .then((nextRoadmap) => {
        if (!cancelled) setRoadmap(nextRoadmap)
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Could not regenerate roadmap')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [events, loadedEvents, requestState, today, extendWeeks])

  const handleApply = async () => {
    if (!roadmap || !activeEntry) return
    setApplying(true)
    setError(null)
    try {
      await commitReplan({
        roadmap,
        events: loadedEvents,
        roadmapCreatedAt: activeEntry.roadmapCreatedAt,
        logEvent,
        option: intent === 'extend' ? 'extend-deadline' : 'edit',
        deadline: intent === 'extend' ? extendDeadline(activeEntry.deadline) : undefined,
      })
      navigate('/roadmap')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not apply replan')
    } finally {
      setApplying(false)
    }
  }

  if (!events) {
    return (
      <main className="replan-page">
        <p className="t-body" role="status">Loading replan...</p>
      </main>
    )
  }

  if (requestState?.error || !activeEntry) {
    return (
      <main className="replan-page">
        <div className="mono-caps">Replan</div>
        <h1 className="t-display-2">No active roadmap</h1>
        <p className="t-body">{requestState?.error ?? 'There is no active roadmap to replan.'}</p>
        <button className="btn btn-secondary" type="button" onClick={() => navigate('/roadmaps')}>
          Back to roadmaps
        </button>
      </main>
    )
  }

  const lockedCount = requestState?.request?.pins.length ?? 0
  const totalSlots = slotCount(roadmap)
  const replannedCount = Math.max(0, totalSlots - lockedCount)
  const materials = requestState?.request?.input.materials.map((material) => ({
    id: material.id,
    title: material.title,
  })) ?? []

  return (
    <main className="replan-page">
      <header className="replan-header">
        <div>
          <div className="mono-caps">Replan</div>
          <h1 className="t-display-2">
            {intent === 'extend' ? 'Extend this roadmap' : 'Preview the replan'}
          </h1>
          <p className="t-body">
            {lockedCount} locked, {replannedCount} will be re-planned
          </p>
        </div>
      </header>

      {intent === 'extend' && (
        <div className="replan-intent" role="note">
          Deadline preview: {activeEntry.deadline} to {extendDeadline(activeEntry.deadline)}
        </div>
      )}

      {loading && <p className="t-body" role="status">Regenerating preview...</p>}
      {error && <p className="field-error" role="alert">{error}</p>}

      {roadmap && (
        <>
          <div className="replan-summary" aria-label="Replan summary">
            <span><strong>{roadmap.weeks.length}</strong> week{roadmap.weeks.length !== 1 ? 's' : ''}</span>
            <span><strong>{formatMinutes(roadmap.capacityCheck.totalMaterialMinutes)}</strong> planned</span>
            <span><strong>{roadmap.warnings.length}</strong> warning{roadmap.warnings.length !== 1 ? 's' : ''}</span>
          </div>
          <SchedulePreview
            roadmap={roadmap}
            materials={materials}
            onResolveTie={() => {}}
            onRename={() => {}}
            readOnly
          />
        </>
      )}

      <div className="replan-actions">
        <button
          className="btn btn-primary"
          type="button"
          disabled={!roadmap || applying}
          onClick={() => void handleApply()}
        >
          {applying ? 'Applying...' : 'Apply'}
        </button>
        <button
          className="btn btn-secondary"
          type="button"
          onClick={() => navigate('/roadmap')}
        >
          Keep current
        </button>
      </div>
    </main>
  )
}
