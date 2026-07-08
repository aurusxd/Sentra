import { benefits } from "@/lib/data";
import { Card } from "@/components/ui/Card";
import { FadeIn } from "@/components/ui/FadeIn";
import { Section } from "@/components/ui/Section";
import { SectionHeader } from "@/components/ui/SectionHeader";

export function Benefits() {
  return (
    <Section id="benefits">
      <SectionHeader
        label="Преимущества"
        title="Поддержка отвечает быстрее"
        description="Sentra закрывает повторяющиеся вопросы и помогает владельцу бизнеса не держать команду на рутине."
      />
      <div className="mt-14 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {benefits.map((benefit, index) => (
          <FadeIn key={benefit.key} delay={index * 0.05}>
            <Card className="h-full">
              <benefit.icon aria-hidden="true" className="text-primary" size={28} />
              <h3 className="mt-6 text-xl font-semibold text-text">{benefit.title}</h3>
              <p className="mt-3 leading-7 text-muted">{benefit.description}</p>
            </Card>
          </FadeIn>
        ))}
      </div>
    </Section>
  );
}
