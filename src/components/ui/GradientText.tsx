import type { ReactNode } from "react";

export function GradientText({ children }: { children: ReactNode }) {
  return (
    <span className="bg-gradient-to-r from-primary via-text to-accent bg-clip-text text-transparent">
      {children}
    </span>
  );
}
