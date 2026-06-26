import {
  regenerateRoadmap,
  type RoadmapOutput,
} from '@study-tracker/roadmap-engine'
import type { Event } from '../../events/EventStore'
import { postRoadmapRegenerate } from '../../lib/intelligenceClient'
import {
  mapToRegenerateRequest,
  type RoadmapRegenerateRequest,
} from './mapToRegenerateRequest'

interface ReplanRoadmapOptions {
  today?: string
  transport?: (body: RoadmapRegenerateRequest) => Promise<unknown>
  offlineFallback?: boolean
}

function todayISO(): string {
  return new Date().toISOString().slice(0, 10)
}

function parseRoadmapOutput(response: unknown): RoadmapOutput {
  return response as RoadmapOutput
}

function offlineReplan(request: RoadmapRegenerateRequest): RoadmapOutput {
  return regenerateRoadmap(request.input, request.pins)
}

export async function replanRoadmap(
  events: Event[],
  opts: ReplanRoadmapOptions = {},
): Promise<RoadmapOutput> {
  const request = mapToRegenerateRequest(events, opts.today ?? todayISO())
  const transport = opts.transport ?? postRoadmapRegenerate

  try {
    return parseRoadmapOutput(await transport(request))
  } catch (err) {
    if (opts.offlineFallback) {
      return offlineReplan(request)
    }
    throw err
  }
}
