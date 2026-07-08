"use client";

import { Button } from "@/components/ui/Button";

export default function Error() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-bg px-4 text-center">
      <div className="max-w-md">
        <p className="text-sm uppercase tracking-[0.22em] text-primary">Sentra</p>
        <h1 className="mt-4 text-3xl font-semibold text-text">Что-то пошло не так</h1>
        <p className="mt-3 text-muted">Обновите страницу или оставьте заявку чуть позже.</p>
        <Button className="mt-8" href="/">
          На главную
        </Button>
      </div>
    </main>
  );
}
