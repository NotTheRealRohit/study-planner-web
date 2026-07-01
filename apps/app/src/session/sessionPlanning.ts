import { buildMaterialLedger, type MaterialLedgerEntry } from '@study-tracker/progress';
import {
  suggestMaterialForBooking,
  type Booking,
  type Material,
} from '@study-tracker/roadmap-engine';
import type { Event } from '../events/EventStore';
import {
  deriveBookingsForRoadmap,
  mapMaterialProgressMarks,
  mapMaterialsForRoadmap,
  mapSessions,
} from '../progress/mapEvents';
import { deriveRoadmapLifecycle, type RoadmapLifecycleEntry } from '../roadmap/roadmapLifecycle';
import type { MaterialAddedPayload } from '../sync/types';
import type { MaterialKind, MaterialPosition, SessionSlotData } from './types';

export interface SessionMaterialOption {
  materialId: string;
  title: string;
  estimatedMinutes: number;
  remainingEstimatedMinutes: number;
  role: 'anchor' | 'foundation' | 'practice';
  kind: MaterialKind;
  url?: string;
  youtubeVideoId?: string;
  videos?: Array<{ youtubeVideoId: string; title: string; durationMinutes: number }>;
  started: boolean;
  done: boolean;
  lastPosition?: MaterialPosition;
}

export interface SessionPlan {
  roadmapEntry?: RoadmapLifecycleEntry;
  roadmapCreatedAt?: string;
  booking?: Booking;
  slotData?: SessionSlotData;
  materials: SessionMaterialOption[];
  suggestedMaterial?: SessionMaterialOption;
}

function dayDiff(start: string, end: string): number {
  const startMs = new Date(`${start}T00:00:00.000Z`).getTime();
  const endMs = new Date(`${end}T00:00:00.000Z`).getTime();
  return Math.max(0, Math.round((endMs - startMs) / 86_400_000));
}

function weekIndexFor(entry: RoadmapLifecycleEntry | undefined, date: string): number {
  if (!entry) return 0;
  return Math.floor(dayDiff(entry.payload.startDate, date) / 7);
}

function toEngineMaterial(payload: MaterialAddedPayload, additionOrder: number): Material {
  return {
    id: payload.materialId,
    title: payload.title,
    totalMinutes: payload.estimatedDuration,
    role: payload.role,
    additionOrder,
  };
}

function materialOptions(
  payloads: MaterialAddedPayload[],
  ledger: MaterialLedgerEntry[],
): SessionMaterialOption[] {
  const ledgerById = new Map(ledger.map((entry) => [entry.materialId, entry]));
  return payloads.map((payload) => {
    const entry = ledgerById.get(payload.materialId);
    return {
      materialId: payload.materialId,
      title: payload.title,
      estimatedMinutes: payload.estimatedDuration,
      remainingEstimatedMinutes: entry?.remainingEstimatedMinutes ?? payload.estimatedDuration,
      role: payload.role,
      kind: payload.kind,
      url: payload.url,
      youtubeVideoId: payload.youtubeVideoId,
      videos: payload.videos,
      started: entry?.started ?? false,
      done: entry?.done ?? false,
      lastPosition: entry?.lastPosition,
    };
  });
}

export function slotDataForBooking(
  booking: Booking | undefined,
  material: SessionMaterialOption,
  entry: RoadmapLifecycleEntry | undefined,
  date: string,
): SessionSlotData {
  const plannedMinutes = booking?.estimatedDuration ?? Math.max(15, Math.min(60, material.remainingEstimatedMinutes || material.estimatedMinutes));
  return {
    bookingId: booking?.id,
    materialId: material.materialId,
    sessionTitle: material.title,
    slotDate: booking?.date ?? date,
    weekIndex: weekIndexFor(entry, booking?.date ?? date),
    plannedMinutes,
    plannedSessionMinutes: plannedMinutes,
    materialEstimatedMinutes: material.estimatedMinutes,
    materialStartPosition: material.lastPosition,
    materialUrl: material.url,
    role: material.role,
    kind: material.kind,
    youtubeVideoId: material.youtubeVideoId,
    videos: material.videos,
  };
}

export function deriveTodaySessionPlan(events: Event[], today: string): SessionPlan {
  const active = deriveRoadmapLifecycle(events).active[0];
  if (!active) return { materials: [] };

  const materialPayloads = mapMaterialsForRoadmap(events, active);
  const sessions = mapSessions(events);
  const marks = mapMaterialProgressMarks(events, active.roadmapCreatedAt);
  const ledger = buildMaterialLedger(
    materialPayloads.map((payload) => ({
      id: payload.materialId,
      title: payload.title,
      estimatedMinutes: payload.estimatedDuration,
    })),
    sessions,
    marks,
  );
  const materials = materialOptions(materialPayloads, ledger);
  const bookings = deriveBookingsForRoadmap(events, active, today);
  const booking = bookings.find((candidate) => candidate.date === today);

  const usedMaterialIds = sessions
    .map((session) => session.materialId)
    .filter((materialId): materialId is string => Boolean(materialId));
  const suggestedId = booking?.materialId ??
    suggestMaterialForBooking(
      materialPayloads.map(toEngineMaterial),
      ledger,
      usedMaterialIds,
    );
  const suggestedMaterial = materials.find((material) => material.materialId === suggestedId) ??
    materials.find((material) => !material.done) ??
    materials[0];

  return {
    roadmapEntry: active,
    roadmapCreatedAt: active.roadmapCreatedAt,
    booking,
    materials,
    suggestedMaterial,
    slotData: suggestedMaterial ? slotDataForBooking(booking, suggestedMaterial, active, today) : undefined,
  };
}

export function withSelectedMaterial(slotData: SessionSlotData, material: SessionMaterialOption): SessionSlotData {
  return {
    ...slotData,
    materialId: material.materialId,
    sessionTitle: material.title,
    materialEstimatedMinutes: material.estimatedMinutes,
    materialStartPosition: material.lastPosition,
    materialUrl: material.url,
    role: material.role,
    kind: material.kind,
    youtubeVideoId: material.youtubeVideoId,
    videos: material.videos,
  };
}
