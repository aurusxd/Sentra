"use client";

import { Send } from "lucide-react";
import { useState, type FormEvent } from "react";

export function LeadForm({ id = "lead" }: { id?: string }) {
  const [sent, setSent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function submitLead(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setSent(false);
    setError("");

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      const response = await fetch("/backend-api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.get("name"),
          phone: formData.get("phone"),
          telegram: formData.get("telegram"),
          website: formData.get("website")
        })
      });
      const result = (await response.json()) as { error?: string };

      if (!response.ok) throw new Error(result.error || "Не удалось отправить заявку");

      form.reset();
      setSent(true);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Не удалось отправить заявку");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form id={id} onSubmit={submitLead} className="rounded-lg border border-line bg-panel/80 p-5 shadow-[0_26px_90px_rgb(0_0_0/0.26)]">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-text">Заявка на запуск</p>
          <p className="mt-1 text-sm text-muted">Ответим и уточним детали проекта.</p>
        </div>
        <span className="grid size-10 place-items-center rounded-lg bg-primary/12 text-primary">
          <Send aria-hidden="true" size={18} />
        </span>
      </div>
      <div className="grid gap-3">
        <input className="hidden" name="website" tabIndex={-1} autoComplete="off" aria-hidden="true" />
        <input className="focus-ring h-12 rounded-md border border-line bg-bg/70 px-4 text-text placeholder:text-muted" name="name" placeholder="Имя" required />
        <input className="focus-ring h-12 rounded-md border border-line bg-bg/70 px-4 text-text placeholder:text-muted" name="phone" placeholder="Телефон" required />
        <input className="focus-ring h-12 rounded-md border border-line bg-bg/70 px-4 text-text placeholder:text-muted" name="telegram" placeholder="Telegram" required />
        <button className="focus-ring mt-2 inline-flex h-12 items-center justify-center rounded-full bg-primary px-5 text-sm font-semibold text-bg transition hover:bg-accent hover:text-text disabled:cursor-not-allowed disabled:opacity-60" type="submit" disabled={submitting}>
          {submitting ? "Отправляем..." : "Оставить заявку"}
        </button>
      </div>
      {sent ? <p className="mt-4 text-sm text-primary">Заявка отправлена. Скоро свяжемся с вами.</p> : null}
      {error ? <p className="mt-4 text-sm text-red-400" role="alert">{error}</p> : null}
    </form>
  );
}
