"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { FolderOpen, Plus, Film } from "lucide-react";
import { api } from "@/lib/api";
import type { Project } from "@/types";
import { format } from "date-fns";

export default function DashboardPage() {
  const { data: projects, isLoading } = useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: () => api.get("/projects/").then((r) => r.data),
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-white/50 text-sm mt-1">Your productions at a glance</p>
        </div>
        <Link href="/projects/new" className="btn-primary">
          <Plus size={16} />
          New project
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: "Total projects", value: projects?.length ?? 0 },
          {
            label: "In production",
            value: projects?.filter((p) => p.status === "shooting").length ?? 0,
          },
          {
            label: "Pre-production",
            value:
              projects?.filter((p) => p.status === "pre_production").length ?? 0,
          },
        ].map((stat) => (
          <div key={stat.label} className="card">
            <p className="text-white/50 text-xs uppercase tracking-wider mb-2">{stat.label}</p>
            <p className="text-3xl font-bold text-brand-500">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Recent projects */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Recent projects</h2>
        {isLoading ? (
          <div className="text-white/40 text-sm">Loading…</div>
        ) : projects?.length === 0 ? (
          <div className="card text-center py-16 text-white/40">
            <Film size={40} className="mx-auto mb-4 opacity-30" />
            <p>No projects yet.</p>
            <Link href="/projects/new" className="btn-primary mt-4 inline-flex">
              <Plus size={16} /> Create your first project
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects?.slice(0, 6).map((project) => (
              <Link key={project.id} href={`/projects/${project.id}`} className="card hover:border-white/10 transition-colors block">
                <div className="flex items-start justify-between mb-3">
                  <FolderOpen size={20} className="text-brand-500" />
                  <span className="text-xs text-white/30">{format(new Date(project.created_at), "MMM d, yyyy")}</span>
                </div>
                <h3 className="font-semibold mb-1">{project.name}</h3>
                <p className="text-white/40 text-xs">{project.description?.slice(0, 80) ?? "No description"}</p>
                <div className="mt-3">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-brand-600/20 text-brand-400 capitalize">
                    {project.status.replace("_", " ")}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
