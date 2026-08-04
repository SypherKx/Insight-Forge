import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { AmbientBackground } from "@/components/premium/AmbientBackground";

export function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <div className="relative flex min-h-screen text-[var(--ink)] bg-[var(--canvas)] transition-colors duration-300">
      <AmbientBackground />
      <Sidebar />
      <main className="min-w-0 flex-1 scrollbar-thin">
        {children}
      </main>
    </div>
  );
}

export function PageHeader({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col gap-4 border-b border-[var(--hairline)] bg-[var(--canvas)] backdrop-blur-md px-8 py-6 md:flex-row md:items-end md:justify-between transition-colors duration-300">
      <div>
        <h1 className="title-lg text-2xl font-bold tracking-tight text-[var(--ink)] md:text-3xl font-serif">{title}</h1>
        {description && <p className="body-md mt-1 text-sm text-[var(--muted)]">{description}</p>}
      </div>
      {action}
    </div>
  );
}