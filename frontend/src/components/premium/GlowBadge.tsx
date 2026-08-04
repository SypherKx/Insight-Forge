import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface GlowBadgeProps {
  children: ReactNode;
  variant?: "default" | "coral" | "forest" | "cream" | "info";
  className?: string;
}

export function GlowBadge({
  children,
  variant = "default",
  className,
}: GlowBadgeProps) {
  const variantStyles = {
    default: "liquid-glass-tag",
    coral: "bg-[#aa2d00]/10 text-[#aa2d00] border-[#aa2d00]/20 font-semibold rounded-full px-3 py-1 text-xs",
    forest: "bg-[#0a2e0e]/10 text-[#0a2e0e] border-[#0a2e0e]/20 font-semibold rounded-full px-3 py-1 text-xs",
    cream: "bg-[#f5e9d4] text-[#181d26] border-[#dddddd] rounded-full px-3 py-1 text-xs font-medium",
    info: "bg-[#254fad]/10 text-[#254fad] border-[#254fad]/20 rounded-full px-3 py-1 text-xs font-medium",
  };

  return (
    <span className={cn("inline-flex items-center gap-1.5 border", variantStyles[variant], className)}>
      {children}
    </span>
  );
}
