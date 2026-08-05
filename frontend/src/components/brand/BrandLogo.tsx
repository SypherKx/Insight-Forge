import type { SVGProps } from "react";

export function BrandLogoIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={props.className || "h-7 w-7"}
      {...props}
    >
      <defs>
        <linearGradient id="insightForgeGrad" x1="2" y1="2" x2="30" y2="30" gradientUnits="userSpaceOnUse">
          <stop stopColor="#cc785c" />
          <stop offset="0.5" stopColor="#e8a55a" />
          <stop offset="1" stopColor="#5db8a6" />
        </linearGradient>
        <linearGradient id="coreGlow" x1="10" y1="10" x2="22" y2="22" gradientUnits="userSpaceOnUse">
          <stop stopColor="#ffffff" stopOpacity="0.95" />
          <stop offset="1" stopColor="#ffe6dc" stopOpacity="0.8" />
        </linearGradient>
      </defs>

      {/* Rounded Diamond Badge Background */}
      <rect x="2" y="2" width="28" height="28" rx="8" fill="url(#insightForgeGrad)" />

      {/* Interlocking RAG Knowledge Layers & Medical Compass Vector */}
      <path
        d="M16 7L23 11.5V20.5L16 25L9 20.5V11.5L16 7Z"
        stroke="white"
        strokeWidth="1.8"
        strokeLinejoin="round"
        fill="none"
        opacity="0.9"
      />
      
      {/* Central Flame / Insight Core */}
      <path
        d="M16 10C16 10 12.5 14 12.5 16.8C12.5 18.8 14.1 20.5 16 20.5C17.9 20.5 19.5 18.8 19.5 16.8C19.5 14 16 10 16 10Z"
        fill="url(#coreGlow)"
      />

      {/* Neural Node Points */}
      <circle cx="16" cy="7" r="1.5" fill="white" />
      <circle cx="23" cy="11.5" r="1.5" fill="white" />
      <circle cx="23" cy="20.5" r="1.5" fill="white" />
      <circle cx="16" cy="25" r="1.5" fill="white" />
      <circle cx="9" cy="20.5" r="1.5" fill="white" />
      <circle cx="9" cy="11.5" r="1.5" fill="white" />
    </svg>
  );
}

export function BrandLogo({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const iconSizes = {
    sm: "h-6 w-6",
    md: "h-7 w-7",
    lg: "h-9 w-9",
  };

  const textSizes = {
    sm: "text-base",
    md: "text-lg",
    lg: "text-2xl",
  };

  return (
    <div className="flex items-center gap-2.5 select-none">
      <BrandLogoIcon className={`${iconSizes[size]} shrink-0 shadow-sm`} />
      <span className={`${textSizes[size]} font-serif font-semibold tracking-tight text-[var(--ink)]`}>
        InsightForge{" "}
        <span className="font-sans text-xs font-bold text-[var(--primary)] uppercase tracking-wider ml-0.5">
          AI
        </span>
      </span>
    </div>
  );
}
