import { processSteps } from "@/lib/data";
import { FadeIn } from "@/components/ui/FadeIn";
import { Section } from "@/components/ui/Section";
import { SectionHeader } from "@/components/ui/SectionHeader";

export function HowItWorks() {
  return (
    <Section id="process" className="bg-white/[0.02]">
      <SectionHeader
        label="Процесс"
        title="Запуск без лишней сложности"
        description="От первой настройки до рабочего Telegram-бота процесс остается понятным и управляемым."
      />
      <div className="mx-auto mt-14 max-w-4xl">
        {processSteps.map((step, index) => (
          <FadeIn key={step.title} delay={index * 0.05}>
            <div className="grid gap-5 border-l border-line pb-10 pl-6 last:pb-0 sm:grid-cols-[120px_1fr] sm:gap-10">
              <div className="-ml-[37px] flex items-center gap-4 sm:gap-5">
                <span className="grid size-14 shrink-0 place-items-center rounded-lg border border-primary/40 bg-bg text-lg font-semibold text-primary">
                  {index + 1}
                </span>
                <span className="text-sm font-medium uppercase tracking-[0.18em] text-muted">Шаг</span>
              </div>
              <div className="rounded-lg border border-line/70 bg-panel/58 p-6">
                <h3 className="text-2xl font-semibold text-text">{step.title}</h3>
                <p className="mt-3 leading-7 text-muted">{step.description}</p>
              </div>
            </div>
          </FadeIn>
        ))}
      </div>
    </Section>
  );
}
