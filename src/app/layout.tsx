import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://sentra.ai"),
  title: "Sentra - AI-сотрудник для клиентской поддержки",
  description: "Sentra автоматизирует ответы на частые вопросы клиентов через AI-сотрудника в Telegram.",
  icons: {
    icon: [{ url: "/icon.svg", type: "image/svg+xml" }],
    shortcut: "/icon.svg"
  },
  openGraph: {
    title: "Sentra - AI-сотрудник поддержки",
    description: "Telegram-бот, обученный знаниям компании и готовый отвечать клиентам 24/7.",
    type: "website",
    locale: "ru_RU"
  },
  twitter: {
    card: "summary_large_image",
    title: "Sentra - AI-сотрудник поддержки",
    description: "Автоматизация поддержки для малого и среднего бизнеса."
  },
  robots: {
    index: true,
    follow: true
  }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
