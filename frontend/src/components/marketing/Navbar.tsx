import { Link, useRouterState } from "@tanstack/react-router";
import { ArrowRight, Sun, Moon, Sparkles, LayoutDashboard } from "lucide-react";
import { PremiumButton } from "@/components/premium/PremiumButton";
import { BrandLogo } from "@/components/brand/BrandLogo";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";

const links = [
  { to: "/", label: "Overview" },
  { to: "/features", label: "Capabilities" },
  { to: "/about", label: "Architecture" },
  { to: "/app/dashboard", label: "Workspace" },
] as const;

export function Navbar() {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    const isDark = savedTheme !== "light";
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
    <header className="sticky top-0 z-50 h-20 w-full border-b border-[var(--hairline)] bg-[var(--canvas)]/90 backdrop-blur-md transition-colors duration-300">
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-8">
        {/* Brand Logo (Navigates to /) */}
        <BrandLogo size="md" />

        {/* Primary Navigation Menu */}
        <nav className="hidden items-center gap-10 md:flex">
          {links.map((l) => {
            const active = path === l.to;
            return (
              <Link
                key={l.to}
                to={l.to}
                className={cn(
                  "text-sm font-medium transition-colors tracking-wide",
                  active ? "text-[var(--ink)] font-semibold" : "text-[var(--muted)] hover:text-[var(--ink)]"
                )}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>

        {/* Project Action Buttons & Sun/Moon Theme Toggle */}
        <div className="flex items-center gap-4">
          <button
            onClick={toggleDarkMode}
            className="flex h-10 w-10 items-center justify-center rounded-full border border-[var(--hairline)] bg-[var(--surface-soft)] text-[var(--ink)] hover:bg-[var(--surface-card)] transition cursor-pointer"
            title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {darkMode ? <Sun className="h-4 w-4 text-[#c1fbd4]" /> : <Moon className="h-4 w-4 text-[var(--ink)]" />}
          </button>

          <Link to="/app/query">
            <PremiumButton variant="outlineOnDark" size="sm">
              <Sparkles className="h-3.5 w-3.5 mr-1 text-[#c1fbd4]" /> RAG Search
            </PremiumButton>
          </Link>
          <Link to="/app/dashboard">
            <PremiumButton variant="primaryPill" size="sm">
              <LayoutDashboard className="h-3.5 w-3.5 mr-1" /> Launch Workspace <ArrowRight className="h-4 w-4 ml-1" />
            </PremiumButton>
          </Link>
        </div>
      </div>
    </header>
  );
}