import { stats } from "@/lib/data";
import { Card } from "@/components/ui/Card";
import { FadeIn } from "@/components/ui/FadeIn";
import { Section } from "@/components/ui/Section";

export function Stats() {
  return (
    <Section id="stats">
      <div className="grid gap-8 lg:grid-cols-[0.75fr_1fr] lg:items-end">
        <FadeIn>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary">Цифры</p>
            <h2 className="mt-4 text-3xl font-semibold text-text sm:text-5xl">Скорость, которую клиент замечает</h2>
            <p className="mt-5 leading-8 text-muted">
              Sentra не делает поддержку громче. Она убирает ожидание из типовых вопросов и освобождает рабочее время команды.
            </p>
          </div>
        </FadeIn>
        <div className="grid gap-4 sm:grid-cols-3">
          {stats.map((stat, index) => (
            <FadeIn key={stat.key} delay={index * 0.06}>
              <Card>
                <stat.icon aria-hidden="true" className="text-primary" size={25} />
                <p className="mt-6 text-3xl font-semibold text-text">{stat.value}</p>
                <p className="mt-2 text-sm leading-6 text-muted">{stat.label}</p>
              </Card>
            </FadeIn>
          ))}
        </div>
      </div>
    </Section>
  );
}
