import { useEffect, useMemo, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { useEventStore } from '../events/useEventStore'
import type { CalibrationState } from '@study-tracker/progress'
import { getUpNextSlot } from '../events/ProgressEngine'
import { postCalibration } from '../lib/intelligenceClient'
import { mapSessions, mapExceptionalTags, mapResolutions, findRoadmap } from './mapEvents'

export function useCalibrationState(): CalibrationState | null {
  const eventStore = useEventStore()
  const request = useLiveQuery(async () => {
    const events = await eventStore.getAll()
    const sessions = mapSessions(events)
    const roadmap = findRoadmap(events)
    const today = new Date().toISOString().split('T')[0]
    const upNext = roadmap ? getUpNextSlot(roadmap, today) : null
    const sessionIndex = roadmap && upNext ? roadmap.slots.indexOf(upNext) : -1

    return {
      sessions,
      exceptionalTags: mapExceptionalTags(events),
      resolutions: mapResolutions(events),
      nextContext:
        roadmap && upNext
          ? {
              date: upNext.date,
              startedAt: upNext.date,
              materialRole: upNext.role,
              session_index: sessionIndex >= 0 ? sessionIndex : undefined,
              planned_horizon: {
                deadline: roadmap.deadline,
                planned_total_sessions: roadmap.slots.length,
              },
            }
          : null,
    }
  }, [eventStore])
  const requestKey = useMemo(() => JSON.stringify(request ?? null), [request])
  const [state, setState] = useState<CalibrationState | null>(null)

  useEffect(() => {
    if (!request) {
      setState(null)
      return
    }
    let cancelled = false
    setState(null)
    postCalibration(request)
      .then((result) => {
        if (!cancelled) setState(result as CalibrationState)
      })
      .catch(() => {
        if (!cancelled) setState(null)
      })
    return () => {
      cancelled = true
    }
  }, [requestKey])

  return state
}
