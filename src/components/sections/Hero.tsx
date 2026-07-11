import { ArrowUpRight, CheckCircle2 } from "lucide-react";
import { LeadForm } from "@/components/sections/LeadForm";
import { Button } from "@/components/ui/Button";
import { FadeIn } from "@/components/ui/FadeIn";
import { GradientText } from "@/components/ui/GradientText";
import { MeshGradient } from "@/components/ui/MeshGradient";

const bullets = ["Ответы клиентам за секунды", "Обучение на базе знаний", "Telegram-бот без найма оператора"];

export function Hero() {
  return (
    <section id="hero" className="relative isolate overflow-hidden px-4 pb-20 pt-32 sm:px-6 lg:min-h-screen lg:pb-24 lg:pt-40">
      <MeshGradient />
      <div className="absolute inset-0 bg-[linear-gradient(180deg,rgb(var(--color-bg)/0.18),rgb(var(--color-bg)/0.92))]" />
      <div className="relative mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.04fr_0.72fr]">
        <FadeIn>
          <div>
            <p className="inline-flex rounded-full border border-primary/30 bg-primary/10 px-4 py-2 text-sm font-medium text-primary">
              AI-поддержка для малого и среднего бизнеса
            </p>
            <h1 className="mt-6 max-w-4xl text-4xl font-semibold tracking-normal text-text sm:text-6xl lg:text-7xl">
              AI-сотрудник, который <GradientText>отвечает клиентам</GradientText> в Telegram
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-muted">
              Sentra обучается знаниям вашей компании и берет на себя популярные вопросы, чтобы команда тратила время на продажи и сложные обращения.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button href="#final-lead">Оставить заявку</Button>
              <Button href="#demo" variant="secondary">
                Посмотреть админку
              </Button>
            </div>
            <div className="mt-8 grid gap-3 text-sm text-muted sm:grid-cols-3">
              {bullets.map((item) => (
                <span key={item} className="flex items-center gap-2">
                  <CheckCircle2 aria-hidden="true" className="shrink-0 text-primary" size={18} />
                  {item}
                </span>
              ))}
            </div>
          </div>
        </FadeIn>
        <FadeIn delay={0.12}>
          <div className="relative">
            <div className="absolute -inset-4 rounded-lg bg-primary/10 blur-3xl" />
            <LeadForm />
            <a href="#process" className="focus-ring mt-4 inline-flex items-center gap-2 rounded-full text-sm text-muted hover:text-text">
              Как это запускается
              <ArrowUpRight aria-hidden="true" size={16} />
            </a>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
