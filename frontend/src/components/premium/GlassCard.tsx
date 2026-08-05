import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  variant?: "canvas" | "soft" | "dark" | "coral" | "forest" | "cream" | "peach" | "mint" | "yellow" | "violet" | "cyan";
  hover?: boolean;
}

export function GlassCard({
  children,
  className,
  variant = "canvas",
  hover = false,
}: GlassCardProps) {
  const variantStyles = {
    canvas: "bg-[var(--surface-card)] border border-[var(--hairline)] text-[var(--ink)] rounded-xl p-6 shadow-sm",
    soft: "bg-[var(--surface-soft)] border border-[var(--hairline)] text-[var(--ink)] rounded-xl p-6",
    dark: "bg-[var(--surface-dark)] text-[var(--on-dark)] border border-[var(--hairline)] rounded-xl p-8 shadow-xl",
    coral: "bg-[var(--primary)] text-white rounded-xl p-8 shadow-lg",
    forest: "bg-emerald-950 text-white rounded-xl p-8 shadow-lg",
    cream: "bg-[var(--surface-card)] text-[var(--ink)] border border-[var(--hairline)] rounded-xl p-6",
    peach: "bg-[var(--surface-soft)] text-[var(--ink)] border border-[var(--hairline)] rounded-xl p-6",
    mint: "bg-emerald-950/40 text-[var(--ink)] border border-emerald-800/40 rounded-xl p-6",
    yellow: "bg-amber-950/40 text-[var(--ink)] border border-amber-800/40 rounded-xl p-6",
    violet: "bg-purple-950/40 text-white rounded-xl p-8 shadow-lg",
    cyan: "bg-sky-950/40 text-white rounded-xl p-8 shadow-lg",
  };

  return (
    <div
      className={cn(
        variantStyles[variant],
        "transition-all duration-200",
        hover && "hover:border-slate-400 hover:shadow-md",
        className
      )}
    >
      {children}
    </div>
  );
}
