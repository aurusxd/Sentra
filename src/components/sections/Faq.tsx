"use client";

import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { faqItems } from "@/lib/data";
import { Section } from "@/components/ui/Section";
import { SectionHeader } from "@/components/ui/SectionHeader";

export function Faq() {
  const [open, setOpen] = useState(0);

  return (
    <Section id="faq" className="bg-white/[0.02]">
      <SectionHeader
        label="FAQ"
        title="Вопросы перед запуском"
        description="Короткие ответы на то, что обычно волнует владельца бизнеса перед внедрением AI-поддержки."
      />
      <div className="mx-auto mt-12 max-w-3xl divide-y divide-line overflow-hidden rounded-lg border border-line bg-panel/64">
        {faqItems.map((item, index) => {
          const active = open === index;
          const panelId = `faq-panel-${index}`;
          return (
            <div key={item.question}>
              <button
                type="button"
                aria-expanded={active}
                aria-controls={panelId}
                onClick={() => setOpen(active ? -1 : index)}
                className="focus-ring flex w-full items-center justify-between gap-4 px-5 py-5 text-left text-base font-semibold text-text"
              >
                {item.question}
                <ChevronDown aria-hidden="true" className={`shrink-0 text-primary transition ${active ? "rotate-180" : ""}`} size={20} />
              </button>
              {active ? (
                <div id={panelId} role="region" className="px-5 pb-5 leading-7 text-muted">
                  {item.answer}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </Section>
  );
}
