import type { SVGProps } from "react";

export function BrandLogoIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 36 36"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={props.className || "h-7 w-7"}
      {...props}
    >
      <defs>
        <linearGradient id="mintCyanGrad" x1="0" y1="0" x2="36" y2="36" gradientUnits="userSpaceOnUse">
          <stop stopColor="#00f0ff" />
          <stop offset="0.6" stopColor="#c1fbd4" />
          <stop offset="1" stopColor="#a3f7be" />
        </linearGradient>
        <filter id="mintGlow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="1.5" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      {/* Rounded Dark Container */}
      <rect x="1" y="1" width="34" height="34" rx="9" fill="#0a0a0a" stroke="rgba(255,255,255,0.15)" strokeWidth="1.2" />

      {/* Abstract Neural Diamond Crystal */}
      <path
        d="M18 6L25 13L18 20L11 13L18 6Z"
        stroke="url(#mintCyanGrad)"
        strokeWidth="1.8"
        strokeLinejoin="round"
        fill="rgba(193, 251, 212, 0.08)"
        filter="url(#mintGlow)"
      />
      
      {/* Inner Facet Lines */}
      <path d="M11 13H25" stroke="url(#mintCyanGrad)" strokeWidth="1.2" opacity="0.8" />
      <path d="M18 6V20" stroke="url(#mintCyanGrad)" strokeWidth="1.2" opacity="0.8" />

      {/* Neural Node Sparks */}
      <circle cx="18" cy="6" r="1.5" fill="#00f0ff" />
      <circle cx="25" cy="13" r="1.5" fill="#c1fbd4" />
      <circle cx="18" cy="20" r="1.5" fill="#a3f7be" />
      <circle cx="11" cy="13" r="1.5" fill="#c1fbd4" />

      {/* Anvil Base Silhouette */}
      <path
        d="M10 24H26C26 24 25 28 27 28H9C11 28 10 24 10 24Z"
        fill="url(#mintCyanGrad)"
      />
      <rect x="12" y="22" width="12" height="2" rx="1" fill="#c1fbd4" />
    </svg>
  );
}

export function BrandLogo({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const iconSizes = {
    sm: "h-6 w-6",
    md: "h-7.5 w-7.5",
    lg: "h-9 w-9",
  };

  const textSizes = {
    sm: "text-base",
    md: "text-lg",
    lg: "text-2xl",
  };

  return (
    <div className="flex items-center gap-2.5 select-none group cursor-pointer">
      <div className="relative">
        <BrandLogoIcon className={`${iconSizes[size]} shrink-0 transition-transform duration-300 group-hover:scale-105`} />
      </div>
      <span className={`${textSizes[size]} font-display font-semibold tracking-tight text-[var(--ink)] flex items-center gap-1`}>
        InsightForge
        <span className="font-mono text-[10px] font-bold text-[#000000] bg-[#c1fbd4] px-1.5 py-0.5 rounded-full uppercase tracking-wider ml-0.5">
          AI
        </span>
      </span>
    </div>
  );
}
