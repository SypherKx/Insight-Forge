import { Link, useRouterState } from "@tanstack/react-router";
import { ArrowRight, Sun, Moon } from "lucide-react";
import { PremiumButton } from "@/components/premium/PremiumButton";
import { BrandLogo } from "@/components/brand/BrandLogo";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";

const links = [
  { to: "/", label: "Product" },
  { to: "/features", label: "Capabilities" },
  { to: "/about", label: "Architecture" },
  { to: "/app/dashboard", label: "Workspace" },
] as const;

export function Navbar() {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    const isDark = savedTheme === "dark" || (!savedTheme && document.documentElement.classList.contains("dark"));
    if (isDark) {
      document.documentElement.classList.add("dark");
      setDarkMode(true);
    } else {
      document.documentElement.classList.remove("dark");
      setDarkMode(false);
    }
  }, []);

  const toggleDarkMode = () => {
    if (darkMode) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
      setDarkMode(false);
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setDarkMode(true);
    }
  };

  return (
    <header className="sticky top-0 z-50 h-16 w-full border-b border-[var(--hairline)] bg-[var(--canvas)]/90 backdrop-blur-md transition-colors duration-300">
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-6">
        {/* Custom Vector Brand Logo */}
        <Link to="/">
          <BrandLogo size="md" />
        </Link>

        {/* Primary Horizontal Menu */}
        <nav className="hidden items-center gap-8 md:flex">
          {links.map((l) => {
            const active = path === l.to;
            return (
              <Link
                key={l.to}
                to={l.to}
                className={cn(
                  "text-sm font-medium transition-colors",
                  active ? "text-[var(--ink)] font-semibold" : "text-[var(--muted)] hover:text-[var(--ink)]"
                )}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>

        {/* Theme Toggle & Primary Action */}
        <div className="flex items-center gap-3">
          <button
            onClick={toggleDarkMode}
            className="flex h-9 w-9 items-center justify-center rounded-md border border-[var(--hairline)] bg-[var(--surface-soft)] text-[var(--ink)] hover:bg-[var(--surface-card)] transition cursor-pointer"
            title="Toggle Light / Dark Mode"
          >
            {darkMode ? <Sun className="h-4 w-4 text-[var(--accent-amber)]" /> : <Moon className="h-4 w-4 text-[var(--muted)]" />}
          </button>

          <Link to="/app/upload">
            <PremiumButton variant="primary" size="sm">
              Try InsightForge <ArrowRight className="ml-1 h-3.5 w-3.5" />
            </PremiumButton>
          </Link>
        </div>
      </div>
    </header>
  );
}