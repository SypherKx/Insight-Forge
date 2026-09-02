import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { DashboardShell } from "@/components/dashboard/DashboardShell";

export const Route = createFileRoute("/app")({
  beforeLoad: ({ location }) => {
    if (location.pathname === "/app") {
      throw redirect({ to: "/app/query" });
    }
  },
  component: () => (
    <DashboardShell>
      <Outlet />
    </DashboardShell>
  ),
});