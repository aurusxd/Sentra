import type { ReactNode } from "react";

export function Section({ children, id, className = "" }: { children: ReactNode; id: string; className?: string }) {
  return (
    <section id={id} className={`relative px-4 py-20 sm:px-6 lg:py-28 ${className}`}>
      <div className="mx-auto max-w-7xl">{children}</div>
    </section>
  );
}
