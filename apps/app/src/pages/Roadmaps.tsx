import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useLiveQuery } from 'dexie-react-hooks'
import { format, parseISO } from 'date-fns'
import { useEventStore } from '../events/useEventStore'
import { RoadmapCalendar } from '../roadmap/RoadmapCalendar'
import {
  deriveRoadmapLifecycle,
  type RoadmapLifecycleEntry,
} from '../roadmap/roadmapLifecycle'
import '../roadmap/roadmap.css'

function formatRange(entry: RoadmapLifecycleEntry): string {
  return `${format(parseISO(entry.startDate), 'MMM d')} to ${format(parseISO(entry.deadline), 'MMM d, yyyy')}`
}

function RoadmapGroup({
  title,
  entries,
  selectedCreatedAt,
  onSelect,
}: {
  title: string
  entries: RoadmapLifecycleEntry[]
  selectedCreatedAt: string | null
  onSelect: (entry: RoadmapLifecycleEntry) => void
}) {
  return (
    <section className="roadmaps-group" aria-label={`${title} roadmaps`}>
      <div className="roadmaps-group-head">
        <h2>{title}</h2>
        <span className="roadmaps-count">{entries.length}</span>
      </div>
      {entries.length === 0 ? (
        <p className="roadmaps-muted">Nothing here yet.</p>
      ) : (
        <div className="roadmaps-list">
          {entries.map((entry) => (
            <button
              key={entry.roadmapCreatedAt}
              type="button"
              className="roadmaps-row"
              data-selected={entry.roadmapCreatedAt === selectedCreatedAt ? 'true' : undefined}
              onClick={() => onSelect(entry)}
            >
              <span className="roadmaps-row-main">
                <span className="roadmaps-row-title">{entry.title}</span>
                <span className="roadmaps-row-meta">
                  {formatRange(entry)} · {entry.weeks} weeks
                </span>
              </span>
              <span className="roadmaps-row-progress">
                {entry.percentComplete}%
              </span>
            </button>
          ))}
        </div>
      )}
    </section>
  )
}

export function Roadmaps() {
  const eventStore = useEventStore()
  const events = useLiveQuery(() => eventStore.getAll(), [eventStore])
  const [selectedCreatedAt, setSelectedCreatedAt] = useState<string | null>(null)
  const loadedEvents = events ?? []
  const lifecycle = useMemo(
    () => deriveRoadmapLifecycle(loadedEvents),
    [loadedEvents],
  )
  const hasRoadmaps = lifecycle.all.length > 0
  const selectedEntry = selectedCreatedAt
    ? lifecycle.all.find((entry) => entry.roadmapCreatedAt === selectedCreatedAt) ?? null
    : null

  if (!events) {
    return (
      <div className="roadmaps-page">
        <p className="t-body" role="status" style={{ color: 'var(--text-secondary)' }}>
          Loading roadmaps...
        </p>
      </div>
    )
  }

  return (
    <div className="roadmaps-page">
      <header className="roadmaps-header">
        <div>
          <div className="mono-caps">Roadmap history</div>
          <h1 className="roadmaps-title">Past Roadmaps</h1>
          <p className="roadmaps-subtitle">
            Active plans, completed arcs, and abandoned attempts stay visible here.
          </p>
        </div>
        <Link className="btn btn-accent" to="/onboarding">
          Start a new roadmap
        </Link>
      </header>

      {!hasRoadmaps ? (
        <section className="roadmaps-empty" data-testid="roadmaps-empty">
          <p>Nothing here yet.</p>
          <Link className="btn btn-accent" to="/onboarding">
            Start a new roadmap
          </Link>
        </section>
      ) : (
        <div className="roadmaps-layout">
          <div className="roadmaps-groups">
            <RoadmapGroup
              title="Active"
              entries={lifecycle.active}
              selectedCreatedAt={selectedCreatedAt}
              onSelect={(entry) => setSelectedCreatedAt(entry.roadmapCreatedAt)}
            />
            <RoadmapGroup
              title="Completed"
              entries={lifecycle.completed}
              selectedCreatedAt={selectedCreatedAt}
              onSelect={(entry) => setSelectedCreatedAt(entry.roadmapCreatedAt)}
            />
            <RoadmapGroup
              title="Abandoned"
              entries={lifecycle.abandoned}
              selectedCreatedAt={selectedCreatedAt}
              onSelect={(entry) => setSelectedCreatedAt(entry.roadmapCreatedAt)}
            />
          </div>

          {selectedEntry && (
            <section className="roadmaps-readonly" data-testid="roadmaps-readonly-detail">
              <RoadmapCalendar
                roadmapCreatedAt={selectedEntry.roadmapCreatedAt}
                readOnly
              />
            </section>
          )}
        </div>
      )}
    </div>
  )
}
