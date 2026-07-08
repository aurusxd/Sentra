import { LeadForm } from "@/components/sections/LeadForm";
import { FadeIn } from "@/components/ui/FadeIn";
import { GradientText } from "@/components/ui/GradientText";
import { Section } from "@/components/ui/Section";

export function FinalCta() {
  return (
    <Section id="final-cta">
      <div className="grid gap-10 rounded-lg border border-line bg-panel/72 p-6 shadow-[0_30px_120px_rgb(0_0_0/0.28)] lg:grid-cols-[1fr_420px] lg:p-10">
        <FadeIn>
          <div className="flex h-full flex-col justify-center">
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary">Запуск</p>
            <h2 className="mt-4 max-w-3xl text-3xl font-semibold text-text sm:text-5xl">
              Дайте клиентам ответ сейчас, <GradientText>а команде верните время</GradientText>
            </h2>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-muted">
              Оставьте заявку, и мы покажем, как Sentra может выглядеть для вашей компании, базы знаний и Telegram-бота.
            </p>
          </div>
        </FadeIn>
        <FadeIn delay={0.08}>
          <LeadForm id="final-lead" />
        </FadeIn>
      </div>
    </Section>
  );
}
