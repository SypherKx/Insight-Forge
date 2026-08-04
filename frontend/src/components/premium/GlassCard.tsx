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
    canvas: "bg-white border border-slate-200 text-slate-900 rounded-xl p-6 shadow-sm",
    soft: "bg-slate-50 border border-slate-200 text-slate-900 rounded-xl p-6",
    dark: "bg-slate-900 text-white border border-slate-800 rounded-xl p-8 shadow-xl",
    coral: "bg-rose-900 text-white rounded-xl p-8 shadow-lg",
    forest: "bg-emerald-950 text-white rounded-xl p-8 shadow-lg",
    cream: "bg-amber-50 text-slate-900 border border-amber-200 rounded-xl p-6",
    peach: "bg-orange-100 text-slate-900 border border-orange-200 rounded-xl p-6",
    mint: "bg-emerald-100 text-slate-900 border border-emerald-200 rounded-xl p-6",
    yellow: "bg-amber-100 text-slate-900 border border-amber-200 rounded-xl p-6",
    violet: "bg-purple-900 text-white rounded-xl p-8 shadow-lg",
    cyan: "bg-sky-900 text-white rounded-xl p-8 shadow-lg",
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
