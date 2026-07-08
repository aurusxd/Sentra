import { testimonials } from "@/lib/data";
import { Card } from "@/components/ui/Card";
import { FadeIn } from "@/components/ui/FadeIn";
import { Section } from "@/components/ui/Section";
import { SectionHeader } from "@/components/ui/SectionHeader";

export function Testimonials() {
  return (
    <Section id="testimonials">
      <SectionHeader
        label="Отзывы"
        title="Бизнесу важна тишина в рутине"
        description="Sentra помогает оставить повторяющиеся вопросы системе, а внимание команды вернуть клиентам, где нужен живой диалог."
      />
      <div className="mt-14 grid gap-4 lg:grid-cols-3">
        {testimonials.map((item, index) => (
          <FadeIn key={item.name} delay={index * 0.06}>
            <Card className="h-full">
              <p className="text-lg leading-8 text-text">«{item.quote}»</p>
              <div className="mt-8 border-t border-line pt-5">
                <p className="font-semibold text-text">{item.name}</p>
                <p className="mt-1 text-sm text-muted">{item.role}</p>
              </div>
            </Card>
          </FadeIn>
        ))}
      </div>
    </Section>
  );
}
