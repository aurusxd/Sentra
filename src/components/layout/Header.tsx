import { MobileMenu } from "@/components/layout/MobileMenu";
import { Button } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";
import { navItems } from "@/lib/constants";

export function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-40 border-b border-line/45 bg-bg/74 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Logo />
        <nav aria-label="Основная навигация" className="hidden items-center gap-1 md:flex">
          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="focus-ring rounded-full px-4 py-2 text-sm text-muted transition hover:bg-white/5 hover:text-text"
            >
              {item.label}
            </a>
          ))}
        </nav>
        <div className="hidden md:block">
          <Button variant="secondary" href="/admin" showArrow={false}>Войти</Button>
          <Button href="#lead">Оставить заявку</Button>
        </div>
        
        <MobileMenu />
      </div>
    </header>
  );
}
