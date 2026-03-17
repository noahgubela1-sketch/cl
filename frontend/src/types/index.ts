/**
 * Shared TypeScript types mirroring the backend domain model.
 */

export type ProjectStatus =
  | "pre_production"
  | "shooting"
  | "post_production"
  | "completed";

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  shooting_start: string | null;
  shooting_end: string | null;
  budget_cents: number | null;
  created_at: string;
  updated_at: string;
}

export type DayNight = "day" | "night" | "dusk" | "dawn";
export type IntExt = "interior" | "exterior";

export interface Scene {
  id: string;
  project_id: string;
  scene_number: string;
  heading: string | null;
  description: string | null;
  day_night: DayNight | null;
  int_ext: IntExt | null;
  estimated_minutes: number | null;
  page_count: number | null;
  priority: number;
  location_id: string | null;
  notes: string | null;
}

export interface ShootingDay {
  id: string;
  date: string;
  call_time: string | null;
  wrap_time_planned: string | null;
  primary_location_id: string | null;
}

export type TrackingEventType =
  | "scene_start"
  | "scene_end"
  | "setup_start"
  | "setup_end"
  | "break_start"
  | "break_end"
  | "technical_delay"
  | "weather_delay"
  | "day_wrap";

export interface TrackingEvent {
  id: string;
  event_type: TrackingEventType;
  scene_id: string | null;
  timestamp: string;
  delta_minutes: number | null;
  notes: string | null;
}

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
}
