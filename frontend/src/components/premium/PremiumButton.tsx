import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export interface PremiumButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "secondaryOnDark" | "pricingPill" | "tertiary";
  size?: "sm" | "md" | "lg";
  children: ReactNode;
}

export function PremiumButton({
  variant = "primary",
  size = "md",
  children,
  className,
  ...props
}: PremiumButtonProps) {
  const sizeClasses = {
    sm: "px-3.5 py-2 text-xs md:text-sm font-medium",
    md: "px-4 py-2.5 text-sm md:text-base font-semibold",
    lg: "px-6 py-3.5 text-base font-semibold",
  };

  const variantClasses = {
    primary: "button-primary",
    secondary: "button-secondary",
    secondaryOnDark: "bg-white text-slate-900 font-semibold rounded-xl px-5 py-3 hover:bg-slate-100 transition shadow-md",
    pricingPill: "button-pricing-pill",
    tertiary: "bg-transparent text-slate-700 hover:bg-slate-100 border-none font-medium",
  };

  return (
    <button
      className={cn(
        "cursor-pointer transition-all duration-200 inline-flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
