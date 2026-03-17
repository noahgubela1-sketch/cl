"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { Project, Scene, ShootingDay } from "@/types";
import { formatMinutes } from "@/lib/utils";
import { Zap, FileText, Download, Calendar } from "lucide-react";
import { useState } from "react";

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"scenes" | "schedule">("scenes");

  const { data: project } = useQuery<Project>({
    queryKey: ["project", id],
    queryFn: () => api.get(`/projects/${id}`).then((r) => r.data),
  });

  const { data: scenes } = useQuery<Scene[]>({
    queryKey: ["scenes", id],
    queryFn: () => api.get(`/schedules/${id}/scenes`).then((r) => r.data),
  });

  const { data: days } = useQuery<ShootingDay[]>({
    queryKey: ["shooting_days", id],
    queryFn: () => api.get(`/schedules/${id}/shooting-days`).then((r) => r.data),
    enabled: activeTab === "schedule",
  });

  const generateMutation = useMutation({
    mutationFn: () => api.post(`/schedules/${id}/generate`),
    onSuccess: () => {
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["shooting_days", id] });
      }, 5000); // Poll after 5s – background task
    },
  });

  const [uploading, setUploading] = useState(false);

  async function handleScriptUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    await api.post(`/scripts/${id}/upload`, form);
    setTimeout(() => {
      queryClient.invalidateQueries({ queryKey: ["scenes", id] });
      setUploading(false);
    }, 8000);
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">{project?.name ?? "Loading…"}</h1>
          <p className="text-white/40 text-sm mt-1">{project?.description}</p>
        </div>
        <div className="flex gap-3">
          <label className="btn-ghost cursor-pointer border border-white/10">
            <FileText size={16} />
            {uploading ? "Parsing…" : "Upload script"}
            <input
              type="file"
              accept=".pdf,.fdx,.fountain,.celtx"
              className="hidden"
              onChange={handleScriptUpload}
            />
          </label>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="btn-primary"
          >
            <Zap size={16} />
            {generateMutation.isPending ? "Generating…" : "Generate schedule"}
          </button>
          <a href={`${process.env.NEXT_PUBLIC_API_URL}/export/${id}/pdf`} target="_blank" rel="noreferrer" className="btn-ghost border border-white/10">
            <Download size={16} />
            Export PDF
          </a>
        </div>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: "Scenes", value: scenes?.length ?? 0 },
          {
            label: "Total minutes",
            value: formatMinutes(scenes?.reduce((a, s) => a + (s.estimated_minutes ?? 0), 0) ?? 0),
          },
          { label: "Shooting days", value: days?.length ?? "–" },
          { label: "Status", value: project?.status?.replace("_", " ") ?? "–" },
        ].map((s) => (
          <div key={s.label} className="card">
            <p className="text-white/40 text-xs uppercase tracking-wider mb-1">{s.label}</p>
            <p className="text-xl font-semibold capitalize">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-white/10">
        {(["scenes", "schedule"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
              activeTab === tab
                ? "border-brand-500 text-white"
                : "border-transparent text-white/40 hover:text-white"
            }`}
          >
            {tab === "schedule" ? (
              <span className="flex items-center gap-1.5"><Calendar size={14} />{tab}</span>
            ) : (
              <span className="flex items-center gap-1.5"><FileText size={14} />{tab}</span>
            )}
          </button>
        ))}
      </div>

      {/* Scenes */}
      {activeTab === "scenes" && (
        <div className="overflow-x-auto rounded-xl border border-white/5">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5 text-white/40 text-xs uppercase tracking-wider">
                {["#", "Heading", "I/E", "D/N", "Location", "Est."].map((h) => (
                  <th key={h} className="text-left px-4 py-3 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {scenes?.map((scene) => (
                <tr key={scene.id} className="border-b border-white/5 hover:bg-white/2">
                  <td className="px-4 py-3 font-mono text-brand-400">{scene.scene_number}</td>
                  <td className="px-4 py-3 text-white/80 max-w-xs truncate">{scene.heading}</td>
                  <td className="px-4 py-3">
                    {scene.int_ext && (
                      <span className={scene.int_ext === "interior" ? "badge-int" : "badge-ext"}>
                        {scene.int_ext === "interior" ? "INT" : "EXT"}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {scene.day_night && (
                      <span className={scene.day_night === "day" ? "badge-day" : "badge-night"}>
                        {scene.day_night.toUpperCase()}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-white/50">{scene.location_id ?? "–"}</td>
                  <td className="px-4 py-3 text-white/50">
                    {scene.estimated_minutes ? formatMinutes(scene.estimated_minutes) : "–"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Schedule */}
      {activeTab === "schedule" && (
        <div className="space-y-4">
          {!days?.length ? (
            <div className="card text-center py-16 text-white/40">
              <Zap size={40} className="mx-auto mb-4 opacity-30" />
              <p>No schedule yet. Upload a script and click &quot;Generate schedule&quot;.</p>
            </div>
          ) : (
            days.map((day, i) => (
              <div key={day.id} className="card">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold">
                    Day {i + 1} – {new Date(day.date).toLocaleDateString("en-GB", { weekday: "long", day: "2-digit", month: "long", year: "numeric" })}
                  </h3>
                  {day.call_time && (
                    <span className="text-xs text-white/40">
                      Call: {new Date(day.call_time).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
