"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Film, LayoutDashboard, FolderOpen, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/projects", label: "Projects", icon: FolderOpen },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    localStorage.removeItem("access_token");
    router.push("/login");
  }

  return (
    <div className="flex h-screen bg-film-dark">
      {/* Sidebar */}
      <aside className="w-60 flex flex-col bg-film-panel border-r border-white/5">
        <div className="flex items-center gap-3 px-6 py-5 border-b border-white/5">
          <Film className="text-brand-500" size={24} />
          <span className="font-bold tracking-tight">SceneMind AI</span>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
                pathname === href || pathname.startsWith(href + "/")
                  ? "bg-brand-600/20 text-brand-400"
                  : "text-white/60 hover:bg-white/5 hover:text-white"
              )}
            >
              <Icon size={18} />
              {label}
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-white/5">
          <button onClick={logout} className="flex items-center gap-3 text-sm text-white/40 hover:text-white w-full px-3 py-2">
            <LogOut size={16} />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto p-8">{children}</main>
    </div>
  );
}
