import type { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-lg border border-line/70 bg-panel/62 p-6 shadow-[0_24px_80px_rgb(0_0_0/0.22)] ${className}`}>
      {children}
    </div>
  );
}
