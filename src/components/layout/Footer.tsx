import { Logo } from "@/components/ui/Logo";

export function Footer() {
  return (
    <footer className="border-t border-line/60 px-4 py-10 sm:px-6">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 text-sm text-muted sm:flex-row sm:items-center sm:justify-between">
        <Logo />
        <p>AI-сотрудник поддержки для малого и среднего бизнеса.</p>
        <p>© 2026 Sentra</p>
      </div>
    </footer>
  );
}
