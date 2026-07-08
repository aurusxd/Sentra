import type { LucideIcon } from "lucide-react";
import { Bot, Clock3, Database, Gauge, MessagesSquare, ShieldCheck, Sparkles, TimerReset } from "lucide-react";

export type BenefitKey = "answers" | "knowledge" | "telegram" | "quality";
export type StatKey = "speed" | "hours" | "coverage";

export const benefits: Array<{
  key: BenefitKey;
  title: string;
  description: string;
  icon: LucideIcon;
}> = [
  {
    key: "answers",
    title: "Отвечает на частые вопросы",
    description: "AI-сотрудник берет на себя типовые обращения: условия, сроки, статусы, инструкции и первые консультации.",
    icon: MessagesSquare
  },
  {
    key: "knowledge",
    title: "Знает вашу компанию",
    description: "Вы загружаете базу знаний, а Sentra превращает ее в понятные ответы без ручного поиска по документам.",
    icon: Database
  },
  {
    key: "telegram",
    title: "Работает в Telegram",
    description: "Клиенты пишут в привычный мессенджер, а бизнес получает стабильный канал поддержки без лишней нагрузки.",
    icon: Bot
  },
  {
    key: "quality",
    title: "Держит единый стандарт",
    description: "Ответы остаются спокойными, точными и одинаково полезными даже в часы пик.",
    icon: ShieldCheck
  }
];

export const processSteps = [
  {
    title: "Создаем AI-сотрудника",
    description: "Формируем роль, тон общения и сценарии для популярных запросов клиентов."
  },
  {
    title: "Загружаем базу знаний",
    description: "Добавляем ответы, регламенты, документы и информацию о продуктах компании."
  },
  {
    title: "Подключаем Telegram-бота",
    description: "Связываем AI-сотрудника с каналом, где клиенты уже привыкли задавать вопросы."
  },
  {
    title: "Запускаем поддержку",
    description: "Бот отвечает на обращения, а владелец видит заявки и качество работы в админке."
  }
] as const;

export const testimonials = [
  {
    quote: "Мы убрали большую часть повторяющихся вопросов из личных сообщений. Менеджеры теперь подключаются только там, где реально нужен человек.",
    name: "Анна Орлова",
    role: "Владелец онлайн-школы"
  },
  {
    quote: "Sentra помогла быстро навести порядок в поддержке: база знаний стала рабочим инструментом, а не папкой, которую никто не открывает.",
    name: "Илья Мартынов",
    role: "Основатель сервисной компании"
  },
  {
    quote: "Клиенты получают ответ сразу, даже вечером. Для малого бизнеса это ощущается как отдельный сотрудник без найма и обучения.",
    name: "Мария Белова",
    role: "Руководитель e-commerce проекта"
  }
] as const;

export const stats: Array<{
  key: StatKey;
  value: string;
  label: string;
  icon: LucideIcon;
}> = [
  { key: "speed", value: "< 3 сек", label: "среднее время первого ответа", icon: Gauge },
  { key: "hours", value: "до 12 ч", label: "экономии команды каждую неделю", icon: TimerReset },
  { key: "coverage", value: "24/7", label: "поддержка без выходных и пауз", icon: Clock3 }
];

export const faqItems = [
  {
    question: "Что нужно, чтобы запустить Sentra?",
    answer: "Достаточно описать частые вопросы клиентов и передать материалы: инструкции, условия, ответы менеджеров или базу знаний."
  },
  {
    question: "AI-сотрудник будет отвечать как наша компания?",
    answer: "Да. Перед запуском задается тон общения, ограничения и источники знаний, на которые бот должен опираться."
  },
  {
    question: "Что будет, если вопрос сложный?",
    answer: "Бот может попросить уточнение или собрать заявку для менеджера, чтобы человек подключился к нестандартной ситуации."
  },
  {
    question: "Можно ли обновлять базу знаний?",
    answer: "Да. Когда меняются условия, продукты или ответы, база обновляется, и AI-сотрудник начинает использовать новые данные."
  },
  {
    question: "Sentra заменяет всю поддержку?",
    answer: "Sentra закрывает повторяющиеся вопросы и первичную коммуникацию. Команда остается для сложных диалогов и продаж."
  }
] as const;

export const adminSignals = [
  { label: "Новые заявки", value: "18", icon: Sparkles },
  { label: "Автоответы сегодня", value: "247", icon: MessagesSquare },
  { label: "Средняя скорость", value: "2.4 c", icon: Gauge }
] as const;
