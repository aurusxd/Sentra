"use client";

import { Menu, X } from "lucide-react";
import { useState } from "react";
import { navItems } from "@/lib/constants";
import { Button } from "@/components/ui/Button";

export function MobileMenu() {
  const [open, setOpen] = useState(false);
  const id = "mobile-navigation";

  return (
    <div className="md:hidden">
      <button
        type="button"
        aria-label={open ? "Закрыть меню" : "Открыть меню"}
        aria-expanded={open}
        aria-controls={id}
        onClick={() => setOpen((value) => !value)}
        className="focus-ring grid size-11 place-items-center rounded-full border border-line bg-panel/80 text-text"
      >
        {open ? <X aria-hidden="true" size={20} /> : <Menu aria-hidden="true" size={20} />}
      </button>
      {open ? (
        <div
          id={id}
          className="absolute left-4 right-4 top-20 rounded-lg border border-line bg-panel p-4 shadow-[0_28px_90px_rgb(0_0_0/0.35)]"
        >
          <nav aria-label="Мобильная навигация" className="grid gap-2">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className="focus-ring rounded-md px-3 py-3 text-sm text-muted hover:bg-white/5 hover:text-text"
              >
                {item.label}
              </a>
            ))}
          </nav>
          <Button className="mt-3 w-full" href="#lead">
            Оставить заявку
          </Button>
        </div>
      ) : null}
    </div>
  );
}
