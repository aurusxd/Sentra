import { CheckCircle2, MessageSquareText, Search, UploadCloud } from "lucide-react";
import { adminSignals } from "@/lib/data";
import { FadeIn } from "@/components/ui/FadeIn";
import { Section } from "@/components/ui/Section";
import { SectionHeader } from "@/components/ui/SectionHeader";

const knowledgeItems = ["Доставка и сроки", "Гарантии", "Оплата", "Возврат", "Запись на услугу"];

export function Gallery() {
  return (
    <Section id="demo" className="overflow-hidden bg-white/[0.02]">
      <SectionHeader
        label="Админка"
        title="Контроль без перегруза"
        description="Владелец видит, какие вопросы закрывает AI-сотрудник, что загружено в базу знаний и где нужна помощь менеджера."
      />
      <FadeIn>
        <div className="mx-auto mt-14 max-w-6xl rounded-lg border border-line bg-panel/76 p-4 shadow-[0_30px_120px_rgb(0_0_0/0.34)]">
          <div className="grid gap-4 lg:grid-cols-[0.72fr_1fr]">
            <aside className="rounded-lg border border-line/70 bg-bg/66 p-5">
              <div className="flex items-center justify-between">
                <p className="font-semibold text-text">Sentra Console</p>
                <span className="rounded-full bg-primary/12 px-3 py-1 text-xs text-primary">online</span>
              </div>
              <div className="mt-6 grid gap-3">
                {adminSignals.map((signal) => (
                  <div key={signal.label} className="flex items-center justify-between rounded-md border border-line/65 bg-white/[0.03] p-4">
                    <div className="flex items-center gap-3">
                      <signal.icon aria-hidden="true" className="text-primary" size={19} />
                      <span className="text-sm text-muted">{signal.label}</span>
                    </div>
                    <strong className="text-text">{signal.value}</strong>
                  </div>
                ))}
              </div>
            </aside>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-lg border border-line/70 bg-bg/66 p-5">
                <div className="flex items-center gap-3 text-primary">
                  <UploadCloud aria-hidden="true" size={20} />
                  <p className="text-sm font-semibold uppercase tracking-[0.16em]">База знаний</p>
                </div>
                <div className="mt-5 grid gap-2">
                  {knowledgeItems.map((item) => (
                    <div key={item} className="flex items-center justify-between rounded-md bg-white/[0.04] px-3 py-3">
                      <span className="text-sm text-text">{item}</span>
                      <CheckCircle2 aria-hidden="true" className="text-primary" size={17} />
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-lg border border-line/70 bg-bg/66 p-5">
                <div className="flex items-center gap-3 text-primary">
                  <MessageSquareText aria-hidden="true" size={20} />
                  <p className="text-sm font-semibold uppercase tracking-[0.16em]">Диалог</p>
                </div>
                <div className="mt-5 grid gap-3">
                  <div className="rounded-lg rounded-tl-sm bg-white/[0.06] p-4 text-sm text-muted">Какие сроки доставки по Новосибирску?</div>
                  <div className="ml-8 rounded-lg rounded-tr-sm bg-primary/16 p-4 text-sm text-text">
                    Обычно 1-2 рабочих дня. Если заказ оформлен до 14:00, передаем его в обработку сегодня.
                  </div>
                </div>
                <div className="mt-5 flex items-center gap-2 rounded-md border border-line bg-white/[0.03] px-3 py-3 text-sm text-muted">
                  <Search aria-hidden="true" size={17} />
                  Источник: база знаний / доставка
                </div>
              </div>
            </div>
          </div>
        </div>
      </FadeIn>
    </Section>
  );
}
