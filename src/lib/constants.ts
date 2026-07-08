export const navItems = [
  { label: "Преимущества", href: "#benefits" },
  { label: "Процесс", href: "#process" },
  { label: "Админка", href: "#demo" },
  { label: "FAQ", href: "#faq" }
] as const;

export const easing = [0.22, 1, 0.36, 1] as const;

export const fadeIn = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0 }
} as const;
