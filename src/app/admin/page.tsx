"use client";

import {
  Bot,
  BriefcaseBusiness,
  Check,
  ChevronRight,
  Circle,
  FileText,
  Inbox,
  LayoutDashboard,
  LogIn,
  LogOut,
  MessageCircle,
  MessageSquareText,
  Plus,
  RefreshCcw,
  Search,
  Send,
  ShieldCheck,
  Trash2,
  UploadCloud,
  UserRoundCheck,
  X
} from "lucide-react";
import type { FormEvent, ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";

type EmployeeStatus = "Enabled" | "Disabled";
type EmployeeApiStatus = "active" | "inactive" | "needs_setup";
type DocumentStatus = "Uploaded" | "Processing" | "Ready" | "Error";
type ConversationStatus = "AI" | "Human" | "Closed" | "Needs human";
type EmployeeTab = "Overview" | "Knowledge" | "Telegram" | "Conversations" | "Settings";
type Screen = "login" | "workspace" | "hire" | "employee" | "accounts";

type KnowledgeDocument = {
  id: number;
  name: string;
  size: string;
  uploadedAt: string;
  status: DocumentStatus;
};

type KnowledgeFileResponse = {
  id: number;
  original_filename: string;
  size_bytes: number;
  status: "uploaded" | "processing" | "ready" | "error";
  created_at: string;
};

type EmployeeResponse = {
  id: number;
  name: string;
  role: string;
  business_description: string | null;
  language: string;
  tone: string;
  instruction: string;
  fallback_message: string;
  telegram_admin_chat_id: string | null;
  status: EmployeeApiStatus;
  created_at: string;
  updated_at: string | null;
};

type TelegramChannelResponse = {
  id: number;
  employee_id: number;
  external_username: string | null;
  status: "connected" | "disconnected" | "error";
  created_at: string;
  connected_at: string | null;
};

type TelegramConnectionResponse = {
  connected: boolean;
  bot_name: string | null;
  bot_username: string | null;
  status: "connected" | "disconnected" | "error";
};

type DialogApiStatus = "active" | "resolved" | "needs_human";
type SenderType = "client" | "employee" | "human";

type MessageResponse = {
  id: number;
  dialog_id: number;
  sender_type: SenderType;
  text: string;
  external_message_id: string | null;
  created_at: string;
};

type DialogResponse = {
  id: number;
  employee_id: number;
  channel_id: number | null;
  client_external_id: string;
  client_name: string | null;
  client_username: string | null;
  status: DialogApiStatus;
  is_human_takeover: boolean;
  created_at: string;
  updated_at: string | null;
  messages: MessageResponse[];
};

type ChatMessage = {
  id: number;
  author: "You" | "AI" | "Customer";
  text: string;
  time: string;
};

type Conversation = {
  id: number;
  customer: string;
  lastMessage: string;
  time: string;
  status: ConversationStatus;
  messages: ChatMessage[];
};

type Employee = {
  id: number;
  name: string;
  role: string;
  businessDescription: string;
  language: string;
  tone: string;
  workInstruction: string;
  fallbackMessage: string;
  telegramAdminChatId: string;
  status: EmployeeStatus;
  telegramConnected: boolean;
  telegramBotUsername?: string;
  telegramConnectedAt?: string;
  activeDialogs: number;
  humanPending: number;
  documents: KnowledgeDocument[];
  conversations: Conversation[];
};

type EmployeeForm = {
  name: string;
  role: string;
  businessDescription: string;
  language: string;
  tone: string;
  workInstruction: string;
  fallbackMessage: string;
  telegramAdminChatId: string;
};

const tabs: EmployeeTab[] = ["Overview", "Knowledge", "Telegram", "Conversations", "Settings"];

const tabLabels: Record<EmployeeTab, string> = {
  Overview: "Обзор",
  Knowledge: "База знаний",
  Telegram: "Telegram",
  Conversations: "Диалоги",
  Settings: "Настройки"
};

const statusLabels: Record<string, string> = {
  Enabled: "Включен",
  Disabled: "Отключен",
  Uploaded: "Загружен",
  Processing: "Обработка",
  Ready: "Готов",
  Error: "Ошибка",
  AI: "AI",
  Human: "Оператор",
  Closed: "Закрыт",
  "Needs human": "Нужен человек"
};

const authorLabels: Record<ChatMessage["author"], string> = {
  You: "Вы",
  AI: "AI",
  Customer: "Клиент"
};

const emptyForm: EmployeeForm = {
  name: "",
  role: "",
  businessDescription: "",
  language: "Русский",
  tone: "Дружелюбный",
  workInstruction: "",
  fallbackMessage: "Я пока не уверен в ответе. Передам вопрос человеку из команды.",
  telegramAdminChatId: ""
};

const initialEmployees: Employee[] = [];

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.sentra.fun";
let accessToken = "";

function fetch(input: RequestInfo | URL, init: RequestInit = {}) {
  return globalThis.fetch(input, { ...init, credentials: "include" });
}

function authHeaders(): Record<string, string> {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

function nowTime() {
  return new Intl.DateTimeFormat("ru-RU", { hour: "2-digit", minute: "2-digit" }).format(new Date());
}

function formatBytes(size: number) {
  if (size < 1024 * 1024) return `${Math.max(1, Math.round(size / 1024))} КБ`;
  return `${(size / 1024 / 1024).toFixed(1)} МБ`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "long", year: "numeric" }).format(new Date(value));
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("ru-RU", { hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function formatTelegramUsername(username?: string | null) {
  if (!username) return undefined;
  return username.startsWith("@") ? username : `@${username}`;
}

async function readApiError(response: Response, fallback: string) {
  try {
    const data = (await response.json()) as { detail?: string };
    return data.detail ?? fallback;
  } catch {
    return fallback;
  }
}

function mapDocumentStatus(status: KnowledgeFileResponse["status"]): DocumentStatus {
  const map: Record<KnowledgeFileResponse["status"], DocumentStatus> = {
    uploaded: "Uploaded",
    processing: "Processing",
    ready: "Ready",
    error: "Error"
  };
  return map[status];
}

function mapKnowledgeFile(file: KnowledgeFileResponse): KnowledgeDocument {
  return {
    id: file.id,
    name: file.original_filename,
    size: formatBytes(file.size_bytes),
    uploadedAt: formatDate(file.created_at),
    status: mapDocumentStatus(file.status)
  };
}

function mapEmployeeStatus(status: EmployeeApiStatus): EmployeeStatus {
  return status === "active" ? "Enabled" : "Disabled";
}

function mapEmployeeStatusForApi(status: EmployeeStatus): EmployeeApiStatus {
  return status === "Enabled" ? "active" : "inactive";
}

function mapConversationStatus(dialog: DialogResponse): ConversationStatus {
  if (dialog.status === "resolved") return "Closed";
  if (dialog.is_human_takeover) return "Human";
  if (dialog.status === "needs_human") return "Needs human";
  return "AI";
}

function mapMessageAuthor(senderType: SenderType): ChatMessage["author"] {
  if (senderType === "client") return "Customer";
  if (senderType === "human") return "You";
  return "AI";
}

function mapConversation(dialog: DialogResponse): Conversation {
  const messages = dialog.messages.map((message) => ({
    id: message.id,
    author: mapMessageAuthor(message.sender_type),
    text: message.text,
    time: formatTime(message.created_at)
  }));
  const lastMessage = dialog.messages.at(-1);
  const customer = dialog.client_name || dialog.client_username || `Клиент ${dialog.client_external_id}`;

  return {
    id: dialog.id,
    customer,
    lastMessage: lastMessage?.text ?? "Сообщений пока нет",
    time: formatTime(lastMessage?.created_at ?? dialog.updated_at ?? dialog.created_at),
    status: mapConversationStatus(dialog),
    messages
  };
}

function mapEmployee(employee: EmployeeResponse): Employee {
  return {
    id: employee.id,
    name: employee.name,
    role: employee.role,
    businessDescription: employee.business_description ?? "",
    language: employee.language,
    tone: employee.tone,
    workInstruction: employee.instruction,
    fallbackMessage: employee.fallback_message,
    telegramAdminChatId: employee.telegram_admin_chat_id ?? "",
    status: mapEmployeeStatus(employee.status),
    telegramConnected: false,
    activeDialogs: 0,
    humanPending: 0,
    documents: [],
    conversations: [],
  };
}

function mergeEmployeeResponse(current: Employee, employee: EmployeeResponse): Employee {
  return {
    ...current,
    name: employee.name,
    role: employee.role,
    businessDescription: employee.business_description ?? "",
    language: employee.language,
    tone: employee.tone,
    workInstruction: employee.instruction,
    fallbackMessage: employee.fallback_message,
    telegramAdminChatId: employee.telegram_admin_chat_id ?? current.telegramAdminChatId,
    status: mapEmployeeStatus(employee.status)
  };
}

function statusClass(status: string) {
  const map: Record<string, string> = {
    Enabled: "border-emerald-200 bg-emerald-50 text-emerald-700",
    Disabled: "border-slate-200 bg-slate-50 text-slate-600",
    Uploaded: "border-blue-200 bg-blue-50 text-blue-700",
    Processing: "border-amber-200 bg-amber-50 text-amber-700",
    Ready: "border-emerald-200 bg-emerald-50 text-emerald-700",
    Error: "border-rose-200 bg-rose-50 text-rose-700",
    AI: "border-indigo-200 bg-indigo-50 text-indigo-700",
    Human: "border-cyan-200 bg-cyan-50 text-cyan-700",
    Closed: "border-slate-200 bg-slate-50 text-slate-600",
    "Needs human": "border-rose-200 bg-rose-50 text-rose-700"
  };
  return map[status] ?? "border-slate-200 bg-slate-50 text-slate-600";
}

export default function AdminPage() {
  const [screen, setScreen] = useState<Screen>("login");
  const [employees, setEmployees] = useState<Employee[]>(initialEmployees);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState(initialEmployees[0]?.id ?? 0);
  const [activeTab, setActiveTab] = useState<EmployeeTab>("Overview");
  const [toast, setToast] = useState("Рабочее пространство готово");
  const [canRegisterUsers, setCanRegisterUsers] = useState(false);

  const selectedEmployee = employees.find((employee) => employee.id === selectedEmployeeId) ?? employees[0];

  useEffect(() => {
    localStorage.removeItem("access_token");
    fetch(`${API_BASE_URL}/auth/me`)
      .then(async (response) => {
        if (response.ok) {
          const session = (await response.json()) as { can_register_users: boolean };
          setCanRegisterUsers(session.can_register_users);
          setScreen("workspace");
          void loadEmployees();
        }
      })
      .catch(() => undefined);
  }, []);

  function updateEmployee(id: number, updater: (employee: Employee) => Employee) {
    setEmployees((current) => current.map((employee) => (employee.id === id ? updater(employee) : employee)));
  }

  async function logout() {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: "POST",
        headers: authHeaders()
      });
    } finally {
      accessToken = "";
      setEmployees([]);
      setSelectedEmployeeId(0);
      setCanRegisterUsers(false);
      setScreen("login");
    }
  }

  async function loadEmployees() {
    try {
      const response = await fetch(`${API_BASE_URL}/employees/`, {
        headers: authHeaders()
      });

      if (!response.ok) {
        throw new Error("Не удалось загрузить сотрудников");
      }

      const loadedEmployees = ((await response.json()) as EmployeeResponse[]).map(mapEmployee);

      setEmployees(loadedEmployees);
      setSelectedEmployeeId(loadedEmployees[0]?.id ?? 0);
      setToast("Сотрудники загружены");
    } catch (err) {
      setToast("Не удалось загрузить сотрудников");
    }
  }

  function openEmployee(employeeId: number) {
    setSelectedEmployeeId(employeeId);
    setActiveTab("Overview");
    setScreen("employee");
  }

  function createEmployee(form: EmployeeForm, employeeId = Date.now()) {
    const employee: Employee = {
      id: employeeId,
      name: form.name || "Новый сотрудник",
      role: form.role || "Сотрудник поддержки",
      businessDescription: form.businessDescription,
      language: form.language,
      tone: form.tone,
      workInstruction: form.workInstruction,
      fallbackMessage: form.fallbackMessage,
      telegramAdminChatId: form.telegramAdminChatId,
      status: "Enabled",
      telegramConnected: false,
      activeDialogs: 0,
      humanPending: 0,
      documents: [],
      conversations: [],
    };
    setEmployees((current) => [employee, ...current]);
    setSelectedEmployeeId(employee.id);
    setActiveTab("Overview");
    setScreen("employee");
    setToast(`${employee.name} нанят`);
  }

  async function deleteEmployee(id: number) {
    if (!window.confirm("Удалить сотрудника? Это действие нельзя отменить.")) return;

    try {
      const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
        method: "DELETE",
        headers: authHeaders()
      });

      if (!response.ok) {
        throw new Error(await readApiError(response, "Не удалось удалить сотрудника"));
      }

      const nextEmployees = employees.filter((employee) => employee.id !== id);
      setEmployees(nextEmployees);
      setSelectedEmployeeId(nextEmployees[0]?.id ?? 0);
      setScreen("workspace");
      setToast("Сотрудник удален");
    } catch (err) {
      setToast(err instanceof Error ? err.message : "Не удалось удалить сотрудника");
    }
  }

  return (
    <div className="min-h-screen bg-[#f7f8fb] text-slate-950">
      {screen === "login" ? (
        <LoginScreen
          onLogin={(canRegisterUsers) => {
            setCanRegisterUsers(canRegisterUsers);
            setScreen("workspace");
            loadEmployees();
          }}
        />
      ) : (
        <div className="flex min-h-screen">
          <Sidebar screen={screen} onNavigate={setScreen} canRegisterUsers={canRegisterUsers} onLogout={logout} />
          <div className="min-w-0 flex-1">
            <Topbar
              title={screen === "accounts" ? "Регистрация клиентов" : screen === "hire" ? "Найм сотрудника" : screen === "employee" ? selectedEmployee?.name ?? "Сотрудник" : "Рабочее пространство"}
              subtitle="Управляйте цифровыми сотрудниками поддержки."
              onHire={() => setScreen("hire")}
            />
            <main className="mx-auto w-full max-w-7xl px-6 py-6">
              {screen === "workspace" && (
                <Workspace employees={employees} onHire={() => setScreen("hire")} onOpen={openEmployee} />
              )}
              {screen === "hire" && <HireEmployee onCreate={createEmployee} onCancel={() => setScreen("workspace")} />}
              {screen === "accounts" && canRegisterUsers && <AccountRegistration setToast={setToast} />}
              {screen === "employee" && selectedEmployee && (
                <EmployeeWorkspace
                  employee={selectedEmployee}
                  activeTab={activeTab}
                  onTabChange={setActiveTab}
                  onUpdate={(updater) => updateEmployee(selectedEmployee.id, updater)}
                  onDelete={() => deleteEmployee(selectedEmployee.id)}
                  setToast={setToast}
                />
              )}
              {screen === "employee" && !selectedEmployee && <EmptyState title="У вас пока нет AI-сотрудников." action="Наймите первого сотрудника." />}
            </main>
          </div>
          <Toast message={toast} />
        </div>
      )}
    </div>
  );
}

function LoginScreen({ onLogin }: { onLogin: (canRegisterUsers: boolean) => void }) {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          password,
        }),
      });

      if (!response.ok) {
        setError("Неверная почта или пароль");
        setIsLoading(false);
        return;
      }

      const data = (await response.json()) as { access_token: string };
      accessToken = data.access_token;

      const sessionResponse = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: authHeaders()
      });
      const session = sessionResponse.ok
        ? (await sessionResponse.json()) as { can_register_users: boolean }
        : { can_register_users: false };

      onLogin(session.can_register_users);
    } catch (err) {
      setError("Не удалось подключиться к серверу");
    } finally {
      setIsLoading(false);
    }
  }
  return (
    <main className="grid min-h-screen place-items-center px-6">
      <section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mb-8 flex items-center gap-3">
          <div className="grid size-9 place-items-center rounded-lg bg-slate-950 text-sm font-bold text-white">
            S
          </div>
          <div>
            <p className="text-lg font-semibold">Админ-панель Sentra</p>
            <p className="text-sm text-slate-500">Рабочее пространство AI-сотрудников</p>
          </div>
        </div>
        <form
          className="space-y-4"
          onSubmit={handleSubmit}
        >
          <Field label="Имя пользователя">
            <input className="input" type="text" value={name} onChange={(event) => setName(event.target.value)} />
          </Field>
          <Field label="Пароль">
            <input className="input" type="password" value={password} onChange={(event => setPassword(event.target.value))}/>
          </Field>
          {error && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
              {error}
            </p>
          )}
          <button className="btn-primary w-full" type="submit" disabled={isLoading}>
            <LogIn size={17} />
            {isLoading ? "Входим..." : "Войти в рабочее пространство"}
          </button>
        </form>
      </section>
    </main>
  );
}

function AccountRegistration({ setToast }: { setToast: (message: string) => void }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ name, email, password })
      });
      if (!response.ok) throw new Error(await readApiError(response, "Не удалось создать аккаунт"));

      setName("");
      setEmail("");
      setPassword("");
      setToast(`Аккаунт ${name} создан`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Не удалось создать аккаунт");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="max-w-2xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold">Новый клиентский аккаунт</h2>
      <p className="mt-1 text-sm text-slate-500">Создайте доступ после получения заявки. Самостоятельная регистрация отключена.</p>
      <form className="mt-6 space-y-4" onSubmit={submit}>
        <Field label="Имя пользователя">
          <input className="input" minLength={3} pattern="[A-Za-z0-9_.-]+" required value={name} onChange={(event) => setName(event.target.value)} />
        </Field>
        <Field label="Email">
          <input className="input" required type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        </Field>
        <Field label="Временный пароль (минимум 12 символов)">
          <input className="input" minLength={12} required type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </Field>
        {error ? <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600" role="alert">{error}</p> : null}
        <button className="btn-primary" disabled={isSubmitting} type="submit">
          <UserRoundCheck size={17} />
          {isSubmitting ? "Создаём..." : "Создать аккаунт"}
        </button>
      </form>
    </section>
  );
}

function Sidebar({ screen, onNavigate, canRegisterUsers, onLogout }: { screen: Screen; onNavigate: (screen: Screen) => void; canRegisterUsers: boolean; onLogout: () => void }) {
  const items = [
    { label: "Рабочее пространство", icon: LayoutDashboard, screen: "workspace" as Screen },
    ...(canRegisterUsers ? [{ label: "Аккаунты клиентов", icon: UserRoundCheck, screen: "accounts" as Screen }] : [])
  ];

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white px-4 py-5 lg:flex">
      <div className="mb-8 flex items-center gap-3 px-2">
        <div className="grid size-9 place-items-center rounded-lg bg-slate-950 text-sm font-bold text-white">
          S
        </div>
        <div>
          <p className="font-semibold">Sentra</p>
          <p className="text-xs text-slate-500">Админка</p>
        </div>
      </div>
      <nav className="space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const active = screen === item.screen || (item.label === "Сотрудники" && screen === "employee");
          return (
            <button
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                active ? "bg-slate-950 text-white" : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
              }`}
              key={item.label}
              onClick={() => onNavigate(item.screen)}
              type="button"
            >
              <Icon size={17} />
              {item.label}
            </button>
          );
        })}
      </nav>
      <button
        className="mt-auto flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-500 transition hover:bg-red-50 hover:text-red-700"
        onClick={onLogout}
        type="button"
      >
        <LogOut size={17} />
        Выйти
      </button>
    </aside>
  );
}

function Topbar({ title, subtitle, onHire }: { title: string; subtitle: string; onHire: () => void }) {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/85 px-6 py-4 backdrop-blur">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
          <p className="text-sm text-slate-500">{subtitle}</p>
        </div>
        <button className="btn-primary" onClick={onHire} type="button">
          <Plus size={17} />
          Нанять сотрудника
        </button>
      </div>
    </header>
  );
}

function Workspace({ employees, onHire, onOpen }: { employees: Employee[]; onHire: () => void; onOpen: (id: number) => void }) {
  const totalDialogs = employees.reduce((sum, employee) => sum + employee.activeDialogs, 0);
  const connected = employees.filter((employee) => employee.telegramConnected).length;

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-3">
        <MetricCard icon={<UserRoundCheck size={20} />} label="AI-сотрудники" value={String(employees.length)} />
        <MetricCard icon={<MessageCircle size={20} />} label="Активные диалоги" value={String(totalDialogs)} />
        <MetricCard icon={<Bot size={20} />} label="Telegram подключен" value={String(connected)} />
      </section>
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold">Добрый день</h2>
            <p className="text-sm text-slate-500">Ваша цифровая команда поддержки готова к работе.</p>
          </div>
          <button className="btn-secondary" onClick={onHire} type="button">
            <Plus size={16} />
            Нанять сотрудника
          </button>
        </div>
        {employees.length === 0 ? (
          <EmptyState title="У вас пока нет AI-сотрудников." action="Наймите первого сотрудника." />
        ) : (
          <div className="grid gap-4 xl:grid-cols-2">
            {employees.map((employee) => (
              <EmployeeCard employee={employee} key={employee.id} onOpen={() => onOpen(employee.id)} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function EmployeeCard({ employee, onOpen }: { employee: Employee; onOpen: () => void }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-slate-100 text-slate-700">
            <BriefcaseBusiness size={21} />
          </div>
          <div>
            <h3 className="font-semibold">{employee.name}</h3>
            <p className="text-sm text-slate-500">{employee.role}</p>
          </div>
        </div>
        <Badge label={employee.status} />
      </div>
      <div className="grid gap-3 text-sm sm:grid-cols-3">
        <SmallStat label="Telegram" value={employee.telegramConnected ? "Подключен" : "Не подключен"} />
        <SmallStat label="Активные диалоги" value={String(employee.activeDialogs)} />
        <SmallStat label="Ждут человека" value={String(employee.humanPending)} />
      </div>
      <button className="btn-secondary mt-5 w-full justify-between" onClick={onOpen} type="button">
        Открыть рабочее пространство
        <ChevronRight size={17} />
      </button>
    </article>
  );
}

function HireEmployee({ onCreate, onCancel }: { onCreate: (form: EmployeeForm, employeeId?: number) => void; onCancel: () => void }) {
  const [form, setForm] = useState<EmployeeForm>(emptyForm);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  function setField<K extends keyof EmployeeForm>(key: K, value: EmployeeForm[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }
  async function createEmployee(form: EmployeeForm) {
    const response = await fetch(`${API_BASE_URL}/employees/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify({
        name: form.name,
        role: form.role,
        language: form.language,
        tone: form.tone,
        business_description: form.businessDescription,
        instruction: form.workInstruction,
        fallback_message: form.fallbackMessage,
        telegram_admin_chat_id: form.telegramAdminChatId.trim() || null,
      }),
  });

  if (!response.ok) {
    throw new Error("Не удалось создать сотрудника");
  }

  return await response.json();
}
  
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <FormHeader title="Найм сотрудника" subtitle="Создайте цифрового сотрудника и задайте стиль его общения." />
      <form
        className="grid gap-5 lg:grid-cols-2"
        onSubmit={async (event) => {
          event.preventDefault();
          try{
              setIsLoading(true);
              setError("");

              const employee = await createEmployee(form);
              onCreate(form, employee.id);
          }
            catch (err) {
            setError("Ошибка при создании сотрудника");
            } finally {
            setIsLoading(false);
            }
        }}
      >
        <Field label="Имя сотрудника">
          <input className="input" onChange={(event) => setField("name", event.target.value)} required value={form.name} />
        </Field>
        <Field label="Должность">
          <input className="input" onChange={(event) => setField("role", event.target.value)} required value={form.role} />
        </Field>
        <Field label="Язык">
          <select className="input" onChange={(event) => setField("language", event.target.value)} value={form.language}>
            <option>Русский</option>
            <option>Английский</option>
            <option>Испанский</option>
          </select>
        </Field>
        <Field label="Тон общения">
          <select className="input" onChange={(event) => setField("tone", event.target.value)} value={form.tone}>
            <option>Дружелюбный</option>
            <option>Спокойный и точный</option>
            <option>Формальный</option>
            <option>Уверенный</option>
          </select>
        </Field>
        <Field className="lg:col-span-2" label="Описание бизнеса">
          <textarea className="textarea" onChange={(event) => setField("businessDescription", event.target.value)} value={form.businessDescription} />
        </Field>
        <Field className="lg:col-span-2" label="Рабочая инструкция">
          <textarea className="textarea" onChange={(event) => setField("workInstruction", event.target.value)} value={form.workInstruction} />
        </Field>
        <Field className="lg:col-span-2" label="Сообщение при отсутствии ответа">
          <textarea className="textarea" onChange={(event) => setField("fallbackMessage", event.target.value)} value={form.fallbackMessage} />
        </Field>
        <Field className="lg:col-span-2" label="Telegram chat ID админа">
          <input
            className="input"
            onChange={(event) => setField("telegramAdminChatId", event.target.value)}
            placeholder="Например: 123456789"
            value={form.telegramAdminChatId}
          />
        </Field>
        <div className="flex flex-wrap gap-3 lg:col-span-2">
          {error && (
            <p className="text-sm text-red-600 lg:col-span-2">
              {error}
            </p>
          )}
          <button className="btn-primary" type="submit" disabled={isLoading}>
            <Check size={17} />
            {isLoading ? "Создаем..." : "Нанять сотрудника"}
          </button>
          <button className="btn-secondary" onClick={onCancel} type="button">
            <X size={17} />
            Отмена
          </button>
        </div>
      </form>
    </section>
  );
}

function EmployeeWorkspace({
  employee,
  activeTab,
  onTabChange,
  onUpdate,
  onDelete,
  setToast
}: {
  employee: Employee;
  activeTab: EmployeeTab;
  onTabChange: (tab: EmployeeTab) => void;
  onUpdate: (updater: (employee: Employee) => Employee) => void;
  onDelete: () => void;
  setToast: (message: string) => void;
}) {
  return (
    <section className="space-y-5">
      <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white p-2 shadow-sm">
        <div className="flex min-w-max gap-1">
          {tabs.map((tab) => (
            <button
              className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
                activeTab === tab ? "bg-slate-950 text-white" : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
              }`}
              key={tab}
              onClick={() => onTabChange(tab)}
              type="button"
            >
              {tabLabels[tab]}
            </button>
          ))}
        </div>
      </div>
      {activeTab === "Overview" && <Overview employee={employee} onUpdate={onUpdate} setToast={setToast} />}
      {activeTab === "Knowledge" && <Knowledge employee={employee} onUpdate={onUpdate} setToast={setToast} />}
      {activeTab === "Telegram" && <Telegram employee={employee} onUpdate={onUpdate} setToast={setToast} />}
      {activeTab === "Conversations" && <Conversations employee={employee} onUpdate={onUpdate} setToast={setToast} />}
      {activeTab === "Settings" && <EmployeeSettings employee={employee} onUpdate={onUpdate} onDelete={onDelete} setToast={setToast} />}
    </section>
  );
}

function Overview({
  employee,
  onUpdate,
  setToast
}: {
  employee: Employee;
  onUpdate: (updater: (employee: Employee) => Employee) => void;
  setToast: (message: string) => void;
}) {
  const [action, setAction] = useState<EmployeeStatus | null>(null);
  const [error, setError] = useState("");

  async function changeStatus(status: EmployeeStatus) {
    try {
      setError("");
      setAction(status);

      const response = await fetch(`${API_BASE_URL}/employees/${employee.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders()
        },
        body: JSON.stringify({
          status: mapEmployeeStatusForApi(status)
        })
      });

      if (!response.ok) {
        throw new Error(await readApiError(response, "Не удалось изменить статус сотрудника"));
      }

      const updatedEmployee = (await response.json()) as EmployeeResponse;
      onUpdate((current) => mergeEmployeeResponse(current, updatedEmployee));
      setToast(status === "Enabled" ? "Сотрудник включен" : "Сотрудник отключен");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось изменить статус сотрудника");
    } finally {
      setAction(null);
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold">{employee.name}</h2>
            <p className="text-sm text-slate-500">{employee.role}</p>
          </div>
          <Badge label={employee.status} />
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <SmallStat label="Telegram" value={employee.telegramConnected ? "Подключен" : "Не подключен"} />
          <SmallStat label="Документы" value={String(employee.documents.length)} />
          <SmallStat label="Диалоги" value={String(employee.conversations.length)} />
          <SmallStat label="Ждут человека" value={String(employee.humanPending)} />
        </div>
        <div className="mt-6 flex gap-3">
          <button
            className="btn-primary"
            disabled={action !== null || employee.status === "Enabled"}
            onClick={() => changeStatus("Enabled")}
            type="button"
          >
            <Check size={17} />
            {action === "Enabled" ? "Включаем..." : "Включить сотрудника"}
          </button>
          <button
            className="btn-secondary"
            disabled={action !== null || employee.status === "Disabled"}
            onClick={() => changeStatus("Disabled")}
            type="button"
          >
            <Circle size={17} />
            {action === "Disabled" ? "Отключаем..." : "Отключить сотрудника"}
          </button>
        </div>
        {error && <p className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600">{error}</p>}
      </section>
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <FormHeader title="Рабочий профиль" subtitle="Сотрудник ведет себя как цифровой член команды, а не как обычный чат-бот." />
        <div className="space-y-4 text-sm">
          <InfoRow label="Язык" value={employee.language} />
          <InfoRow label="Тон" value={employee.tone} />
          <InfoRow label="Telegram chat ID админа" value={employee.telegramAdminChatId || "-"} />
          <InfoRow label="Резервное сообщение" value={employee.fallbackMessage} />
        </div>
      </section>
    </div>
  );
}

function Knowledge({
  employee,
  onUpdate,
  setToast
}: {
  employee: Employee;
  onUpdate: (updater: (employee: Employee) => Employee) => void;
  setToast: (message: string) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  async function loadDocuments() {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/employees/${employee.id}/knowledge/`, {
        headers: authHeaders()
      });

      if (!response.ok) {
        throw new Error("Не удалось загрузить список документов");
      }

      const files = (await response.json()) as KnowledgeFileResponse[];

      onUpdate((current) => ({
        ...current,
        documents: files.map(mapKnowledgeFile)
      }));
    } catch (err) {
      setError("Не удалось получить документы с сервера");
    } finally {
      setIsLoading(false);
    }
  }

  async function addFiles(files: FileList | null) {
    if (!files?.length) return;
    setIsUploading(true);
    setError("");

    try {
      const uploadedDocuments = await Promise.all(
        Array.from(files).map(async (file) => {
          const formData = new FormData();
          formData.append("file", file);

          const response = await fetch(`${API_BASE_URL}/employees/${employee.id}/knowledge/upload`, {
            method: "POST",
            headers: authHeaders(),
            body: formData
          });

          if (!response.ok) {
            throw new Error(`Не удалось загрузить ${file.name}`);
          }

          return mapKnowledgeFile((await response.json()) as KnowledgeFileResponse);
        })
      );

      onUpdate((current) => ({ ...current, documents: [...uploadedDocuments, ...current.documents] }));
      setToast(uploadedDocuments.length === 1 ? "Документ загружен" : "Документы загружены");
    } catch (err) {
      setError("Не удалось загрузить документы. Проверьте формат файла и доступ к серверу.");
      setToast("Ошибка загрузки документов");
    } finally {
      setIsUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  async function reindexDocument(documentId: number) {
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/employees/${employee.id}/knowledge/${documentId}/reindex`, {
        method: "POST",
        headers: authHeaders()
      });

      if (!response.ok) {
        throw new Error("Не удалось запустить обработку");
      }

      const updatedDocument = mapKnowledgeFile((await response.json()) as KnowledgeFileResponse);

      onUpdate((current) => ({
        ...current,
        documents: current.documents.map((item) => (item.id === documentId ? updatedDocument : item))
      }));
      setToast("Документ отправлен на обработку");
    } catch (err) {
      setError("Не удалось отправить документ на повторную обработку");
    }
  }

  async function deleteDocument(documentId: number) {
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/employees/${employee.id}/knowledge/${documentId}`, {
        method: "DELETE",
        headers: authHeaders()
      });

      if (!response.ok) {
        throw new Error("Не удалось удалить документ");
      }

      onUpdate((current) => ({ ...current, documents: current.documents.filter((item) => item.id !== documentId) }));
      setToast("Документ удален");
    } catch (err) {
      setError("Не удалось удалить документ");
    }
  }

  useEffect(() => {
    loadDocuments();
  }, [employee.id]);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <FormHeader title="База знаний" subtitle="Загрузите PDF, DOCX или TXT, чтобы обучить сотрудника." />
      <button
        className="mb-5 flex w-full flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center transition hover:border-slate-500 hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
        disabled={isUploading}
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          addFiles(event.dataTransfer.files);
        }}
        type="button"
      >
        <UploadCloud className="mb-3 text-slate-500" size={30} />
        <span className="font-medium">{isUploading ? "Загружаем документы..." : "Загрузите первый документ."}</span>
        <span className="mt-1 text-sm text-slate-500">Перетащите файлы сюда или выберите их на устройстве.</span>
        <input
          accept=".pdf,.docx,.txt"
          className="hidden"
          multiple
          onChange={(event) => addFiles(event.target.files)}
          ref={inputRef}
          type="file"
        />
      </button>
      {error && <p className="mb-5 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600">{error}</p>}
      {isLoading ? (
        <EmptyState title="Загружаем документы..." action="Получаем актуальный список с сервера." />
      ) : employee.documents.length === 0 ? (
        <EmptyState title="Загрузите документы, чтобы обучить сотрудника." action="Поддерживаются PDF, DOCX и TXT." />
      ) : (
        <div className="divide-y divide-slate-100 rounded-2xl border border-slate-200">
          {employee.documents.map((document) => (
            <div className="flex flex-wrap items-center justify-between gap-3 p-4" key={document.id}>
              <div className="flex items-center gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-slate-100 text-slate-600">
                  <FileText size={18} />
                </div>
                <div>
                  <p className="font-medium">{document.name}</p>
                  <p className="text-sm text-slate-500">
                    {document.size} / {document.uploadedAt}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge label={document.status} />
                <button
                  className="icon-btn"
                  onClick={() => reindexDocument(document.id)}
                  title="Обработать документ повторно"
                  type="button"
                >
                  <RefreshCcw size={16} />
                </button>
                <button
                  className="icon-btn text-rose-600"
                  onClick={() => deleteDocument(document.id)}
                  title="Удалить документ"
                  type="button"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function Telegram({
  employee,
  onUpdate,
  setToast
}: {
  employee: Employee;
  onUpdate: (updater: (employee: Employee) => Employee) => void;
  setToast: (message: string) => void;

}) {
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [action, setAction] = useState<"connect" | "check" | "disconnect" | null>(null);

  useEffect(() => {
    void checkTelegram(true);
  }, [employee.id]);

  async function connectTelegram() {
    if (!token.trim()) {
      setError("Введите токен Telegram-бота");
      return;
    }

    try {
      setError("");
      setAction("connect");

      const response = await fetch(`${API_BASE_URL}/employees/${employee.id}/telegram/connect`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders()
        },
        body: JSON.stringify({
          type: "telegram",
          token: token.trim()
        })
      });

      if (!response.ok) {
        throw new Error(await readApiError(response, "Не удалось подключить Telegram"));
      }

      const channel = (await response.json()) as TelegramChannelResponse;

      onUpdate((current) => ({
        ...current,
        telegramConnected: channel.status === "connected",
        telegramBotUsername: formatTelegramUsername(channel.external_username),
        telegramConnectedAt: channel.connected_at ? formatDateTime(channel.connected_at) : formatDateTime(channel.created_at)
      }));

      setToast("Telegram подключен");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось подключить Telegram");
    } finally {
      setAction(null);
    }
  }

  async function checkTelegram(silent = false) {
    try {
      setError("");
      setAction("check");

      const response = await fetch(`${API_BASE_URL}/employees/${employee.id}/telegram/check`, {
        headers: authHeaders()
      });

      if (!response.ok) {
        throw new Error(await readApiError(response, "Не удалось проверить Telegram"));
      }

      const connection = (await response.json()) as TelegramConnectionResponse;

      onUpdate((current) => ({
        ...current,
        telegramConnected: connection.connected,
        telegramBotUsername: formatTelegramUsername(connection.bot_username),
        telegramConnectedAt: connection.connected ? current.telegramConnectedAt ?? "Проверено только что" : undefined
      }));

      if (!silent) {
        setToast(connection.connected ? "Telegram подключен" : "Telegram не подключен");
      }
    } catch (err) {
      if (!silent) {
        setError(err instanceof Error ? err.message : "Не удалось проверить Telegram");
      }
    } finally {
      setAction(null);
    }
  }

  async function disconnectTelegram() {
    try {
      setError("");
      setAction("disconnect");

      const response = await fetch(`${API_BASE_URL}/employees/${employee.id}/telegram/disconnect`, {
        method: "DELETE",
        headers: authHeaders()
      });

      if (!response.ok) {
        throw new Error(await readApiError(response, "Не удалось отключить Telegram"));
      }

      onUpdate((current) => ({
        ...current,
        telegramConnected: false,
        telegramBotUsername: undefined,
        telegramConnectedAt: undefined
      }));

      setToast("Telegram отключен");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось отключить Telegram");
    } finally {
      setAction(null);
    }
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <FormHeader title="Telegram" subtitle="Подключите Telegram, чтобы принимать сообщения клиентов." />
      <div className="grid gap-5 lg:grid-cols-[1fr_0.8fr]">
        <div className="space-y-4">
          <Field label="Токен Telegram-бота">
            <input className="input" onChange={(event) => setToken(event.target.value)} type="password" value={token} />
          </Field>
          {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600">{error}</p>}
          <div className="flex flex-wrap gap-3">
            <button
              className="btn-primary"
              disabled={action !== null}
              onClick={connectTelegram}
              type="button"
            >
              <Bot size={17} />
              {action === "connect" ? "Подключаем..." : "Подключить"}
            </button>
            <button className="btn-secondary" disabled={action !== null} onClick={() => checkTelegram()} type="button">
              <ShieldCheck size={17} />
              {action === "check" ? "Проверяем..." : "Проверить подключение"}
            </button>
            <button
              className="btn-secondary"
              disabled={action !== null || !employee.telegramConnected}
              onClick={disconnectTelegram}
              type="button"
            >
              <X size={17} />
              {action === "disconnect" ? "Отключаем..." : "Отключить"}
            </button>
          </div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
          <InfoRow label="Имя бота" value={employee.telegramBotUsername ?? "Не подключен"} />
          <InfoRow label="Статус" value={employee.telegramConnected ? "Подключен" : "Отключен"} />
          <InfoRow label="Подключен" value={employee.telegramConnectedAt ?? "-"} />
        </div>
      </div>
    </section>
  );
}


function Conversations({
  employee,
  onUpdate,
  setToast
}: {
  employee: Employee;
  onUpdate: (updater: (employee: Employee) => Employee) => void;
  setToast: (message: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<"All" | ConversationStatus>("All");
  const [selectedId, setSelectedId] = useState(employee.conversations[0]?.id ?? 0);
  const [isLoading, setIsLoading] = useState(false);
  const [action, setAction] = useState<"takeover" | "return" | "resolve" | "send" | null>(null);
  const [error, setError] = useState("");

  const filtered = useMemo(
    () =>
      employee.conversations.filter((conversation) => {
        const matchesQuery = conversation.customer.toLowerCase().includes(query.toLowerCase());
        const matchesStatus = status === "All" || conversation.status === status;
        return matchesQuery && matchesStatus;
      }),
    [employee.conversations, query, status]
  );
  const selected = employee.conversations.find((conversation) => conversation.id === selectedId) ?? filtered[0];

  function setConversations(conversations: Conversation[]) {
    onUpdate((current) => ({
      ...current,
      activeDialogs: conversations.filter((conversation) => conversation.status !== "Closed").length,
      humanPending: conversations.filter((conversation) => conversation.status === "Human" || conversation.status === "Needs human").length,
      conversations
    }));
  }

  function updateConversation(id: number, updater: (conversation: Conversation) => Conversation) {
    onUpdate((current) => {
      const conversations = current.conversations.map((conversation) => (conversation.id === id ? updater(conversation) : conversation));

      return {
        ...current,
        activeDialogs: conversations.filter((conversation) => conversation.status !== "Closed").length,
        humanPending: conversations.filter((conversation) => conversation.status === "Human" || conversation.status === "Needs human").length,
        conversations
      };
    });
  }

  async function loadConversations() {
    try {
      setError("");
      setIsLoading(true);

      const response = await fetch(`${API_BASE_URL}/dialog/?employee_id=${employee.id}`, {
        headers: authHeaders()
      });

      if (!response.ok) {
        throw new Error(await readApiError(response, "Не удалось загрузить диалоги"));
      }

      const conversations = ((await response.json()) as DialogResponse[]).map(mapConversation);
      setConversations(conversations);
      setSelectedId((current) => (conversations.some((conversation) => conversation.id === current) ? current : conversations[0]?.id ?? 0));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить диалоги");
    } finally {
      setIsLoading(false);
    }
  }

  async function runDialogAction(nextAction: "takeover" | "return" | "resolve", dialogId: number) {
    const endpoint = nextAction === "takeover" ? "takeover" : nextAction === "return" ? "return" : "resolve";

    try {
      setError("");
      setAction(nextAction);

      const response = await fetch(`${API_BASE_URL}/dialog/${dialogId}/${endpoint}`, {
        method: "POST",
        headers: authHeaders()
      });

      if (!response.ok) {
        throw new Error(await readApiError(response, "Не удалось обновить диалог"));
      }

      const updatedConversation = mapConversation((await response.json()) as DialogResponse);
      updateConversation(dialogId, () => updatedConversation);
      setToast("Диалог обновлен");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось обновить диалог");
    } finally {
      setAction(null);
    }
  }

  async function sendMessage(dialogId: number, text: string) {
    try {
      setError("");
      setAction("send");

      const response = await fetch(`${API_BASE_URL}/dialog/${dialogId}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders()
        },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        throw new Error(await readApiError(response, "Не удалось отправить сообщение"));
      }

      const message = (await response.json()) as MessageResponse;
      const chatMessage: ChatMessage = {
        id: message.id,
        author: mapMessageAuthor(message.sender_type),
        text: message.text,
        time: formatTime(message.created_at)
      };

      updateConversation(dialogId, (conversation) => ({
        ...conversation,
        lastMessage: chatMessage.text,
        time: chatMessage.time,
        status: "Human",
        messages: [...conversation.messages, chatMessage]
      }));
      setToast("Сообщение отправлено");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось отправить сообщение");
    } finally {
      setAction(null);
    }
  }

  useEffect(() => {
    void loadConversations();
  }, [employee.id]);

  return (
    <section className="grid min-w-0 gap-5 xl:grid-cols-[minmax(0,0.75fr)_minmax(0,1.25fr)]">
      <div className="flex h-[620px] min-w-0 flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex flex-wrap gap-3">
          <label className="relative min-w-0 flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input className="input pl-9" onChange={(event) => setQuery(event.target.value)} placeholder="Поиск" value={query} />
          </label>
          <select className="input w-40" onChange={(event) => setStatus(event.target.value as "All" | ConversationStatus)} value={status}>
            <option value="All">Все</option>
            <option value="AI">AI</option>
            <option value="Human">Оператор</option>
            <option value="Needs human">Нужен человек</option>
            <option value="Closed">Закрыт</option>
          </select>
          <button className="btn-secondary" disabled={isLoading} onClick={loadConversations} type="button">
            <RefreshCcw size={16} />
            {isLoading ? "Обновляем..." : "Обновить"}
          </button>
        </div>
        {error && <p className="mb-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600">{error}</p>}
        {isLoading ? (
          <EmptyState title="Загружаем диалоги..." action="Получаем обращения клиентов с сервера." />
        ) : filtered.length === 0 ? (
          <EmptyState title="Диалогов пока нет." action="Здесь появятся обращения клиентов." />
        ) : (
          <div className="min-h-0 flex-1 space-y-2 overflow-y-auto pr-1">
            {filtered.map((conversation) => (
              <button
                className={`h-[118px] w-full overflow-hidden rounded-2xl border p-4 text-left transition ${
                  selected?.id === conversation.id ? "border-slate-950 bg-slate-50" : "border-slate-200 hover:bg-slate-50"
                }`}
                key={conversation.id}
                onClick={() => setSelectedId(conversation.id)}
                type="button"
              >
                <div className="flex min-w-0 items-center justify-between gap-3">
                  <p className="min-w-0 truncate font-medium">{conversation.customer}</p>
                  <span className="shrink-0 text-xs text-slate-500">{conversation.time}</span>
                </div>
                <p className="mt-1 truncate text-sm text-slate-500">{conversation.lastMessage}</p>
                <div className="mt-3">
                  <Badge label={conversation.status} />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
      {selected ? (
        <ChatPanel
          actions={
            <>
              <button className="btn-secondary" disabled={action !== null} onClick={() => runDialogAction("takeover", selected.id)} type="button">
                {action === "takeover" ? "Берем..." : "Взять на себя"}
              </button>
              <button className="btn-secondary" disabled={action !== null} onClick={() => runDialogAction("return", selected.id)} type="button">
                {action === "return" ? "Возвращаем..." : "Вернуть AI"}
              </button>
              <button className="btn-secondary" disabled={action !== null} onClick={() => runDialogAction("resolve", selected.id)} type="button">
                {action === "resolve" ? "Закрываем..." : "Закрыть"}
              </button>
            </>
          }
          emptyTitle="В этом диалоге пока нет сообщений."
          messages={selected.messages}
          onSend={(text) => sendMessage(selected.id, text)}
          title={selected.customer}
        />
      ) : (
        <div className="h-[620px] min-w-0">
          <EmptyState title="Диалогов пока нет." action="Откройте диалог, чтобы ответить вручную." />
        </div>
      )}
    </section>
  );
}

function EmployeeSettings({
  employee,
  onUpdate,
  onDelete,
  setToast
}: {
  employee: Employee;
  onUpdate: (updater: (employee: Employee) => Employee) => void;
  onDelete: () => void;
  setToast: (message: string) => void;
}) {
  const [form, setForm] = useState<EmployeeForm>({
    name: employee.name,
    role: employee.role,
    businessDescription: employee.businessDescription,
    language: employee.language,
    tone: employee.tone,
    workInstruction: employee.workInstruction,
    fallbackMessage: employee.fallbackMessage,
    telegramAdminChatId: employee.telegramAdminChatId
  });
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  function setField<K extends keyof EmployeeForm>(key: K, value: EmployeeForm[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function saveSettings() {
    try {
      setError("");
      setIsSaving(true);

      const response = await fetch(`${API_BASE_URL}/employees/${employee.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders()
        },
        body: JSON.stringify({
          name: form.name,
          role: form.role,
          business_description: form.businessDescription,
          language: form.language,
          tone: form.tone,
          instruction: form.workInstruction,
          fallback_message: form.fallbackMessage,
          telegram_admin_chat_id: form.telegramAdminChatId.trim() || null
        })
      });

      if (!response.ok) {
        throw new Error(await readApiError(response, "Не удалось сохранить изменения"));
      }

      const updatedEmployee = (await response.json()) as EmployeeResponse;
      onUpdate((current) => mergeEmployeeResponse(current, updatedEmployee));
      setToast("Изменения сохранены");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось сохранить изменения");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <FormHeader title="Настройки" subtitle="Измените поведение сотрудника, язык, тон и резервное сообщение." />
      <form
        className="grid gap-5 lg:grid-cols-2"
        onSubmit={(event) => {
          event.preventDefault();
          void saveSettings();
        }}
      >
        <Field label="Имя сотрудника">
          <input className="input" onChange={(event) => setField("name", event.target.value)} value={form.name} />
        </Field>
        <Field label="Должность">
          <input className="input" onChange={(event) => setField("role", event.target.value)} value={form.role} />
        </Field>
        <Field label="Язык">
          <input className="input" onChange={(event) => setField("language", event.target.value)} value={form.language} />
        </Field>
        <Field label="Тон">
          <input className="input" onChange={(event) => setField("tone", event.target.value)} value={form.tone} />
        </Field>
        <Field className="lg:col-span-2" label="Описание бизнеса">
          <textarea className="textarea" onChange={(event) => setField("businessDescription", event.target.value)} value={form.businessDescription} />
        </Field>
        <Field className="lg:col-span-2" label="Рабочая инструкция">
          <textarea className="textarea" onChange={(event) => setField("workInstruction", event.target.value)} value={form.workInstruction} />
        </Field>
        <Field className="lg:col-span-2" label="Сообщение при отсутствии ответа">
          <textarea className="textarea" onChange={(event) => setField("fallbackMessage", event.target.value)} value={form.fallbackMessage} />
        </Field>
        <Field className="lg:col-span-2" label="Telegram chat ID админа">
          <input
            className="input"
            onChange={(event) => setField("telegramAdminChatId", event.target.value)}
            placeholder="Например: 123456789"
            value={form.telegramAdminChatId}
          />
        </Field>
        {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600 lg:col-span-2">{error}</p>}
        <div className="flex flex-wrap justify-between gap-3 lg:col-span-2">
          <button className="btn-primary" disabled={isSaving} type="submit">
            <Check size={17} />
            {isSaving ? "Сохраняем..." : "Сохранить изменения"}
          </button>
          <button className="btn-danger" onClick={onDelete} type="button">
            <Trash2 size={17} />
            Удалить сотрудника
          </button>
        </div>
      </form>
    </section>
  );
}

function ChatPanel({
  title,
  messages,
  emptyTitle,
  actions,
  onSend,
  onClear
}: {
  title: string;
  messages: ChatMessage[];
  emptyTitle: string;
  actions?: ReactNode;
  onSend: (message: string) => void;
  onClear?: () => void;
}) {
  const [message, setMessage] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!message.trim()) return;
    onSend(message.trim());
    setMessage("");
  }

  return (
    <section className="flex h-[620px] min-w-0 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex min-h-[98px] items-center justify-between gap-3 border-b border-slate-200 p-5">
        <div className="min-w-0 flex-1">
          <h2 className="truncate font-semibold">{title}</h2>
          <p className="text-sm text-slate-500">История сообщений и ручные ответы.</p>
        </div>
        <div className="flex shrink-0 flex-wrap justify-end gap-2">
          {actions}
          {onClear && (
            <button className="btn-secondary" onClick={onClear} type="button">
              Очистить историю
            </button>
          )}
        </div>
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto bg-slate-50 p-5">
        {messages.length === 0 ? (
          <EmptyState title={emptyTitle} action="Отправьте сообщение, чтобы начать." />
        ) : (
          messages.map((item) => <MessageBubble key={item.id} message={item} />)
        )}
      </div>
      <form className="flex gap-3 border-t border-slate-200 p-4" onSubmit={submit}>
        <input className="input min-w-0" onChange={(event) => setMessage(event.target.value)} placeholder="Введите сообщение" value={message} />
        <button className="btn-primary shrink-0" type="submit">
          <Send size={17} />
          Отправить
        </button>
      </form>
    </section>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const own = message.author === "You";
  return (
    <div className={`flex ${own ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[78%] overflow-hidden rounded-2xl px-4 py-3 shadow-sm ${own ? "bg-slate-950 text-white" : "bg-white text-slate-800"}`}>
        <div className="mb-1 flex items-center gap-2 text-xs opacity-70">
          <span>{authorLabels[message.author]}</span>
          <span>{message.time}</span>
        </div>
        <p className="break-words text-sm leading-6 [overflow-wrap:anywhere]">{message.text}</p>
      </div>
    </div>
  );
}

function MetricCard({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 grid h-10 w-10 place-items-center rounded-xl bg-slate-100 text-slate-600">{icon}</div>
      <p className="text-2xl font-semibold">{value}</p>
      <p className="text-sm text-slate-500">{label}</p>
    </article>
  );
}

function SmallStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <p className="text-xs font-medium uppercase tracking-[0.12em] text-slate-400">{label}</p>
      <p className="mt-1 text-sm font-semibold text-slate-800">{value}</p>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-b border-slate-200 py-3 last:border-b-0">
      <p className="text-xs font-medium uppercase tracking-[0.12em] text-slate-400">{label}</p>
      <p className="mt-1 text-sm text-slate-800">{value}</p>
    </div>
  );
}

function Field({ label, children, className = "" }: { label: string; children: ReactNode; className?: string }) {
  return (
    <label className={`block space-y-2 ${className}`}>
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

function Badge({ label }: { label: string }) {
  return <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${statusClass(label)}`}>{statusLabels[label] ?? label}</span>;
}

function EmptyState({ title, action }: { title: string; action: string }) {
  return (
    <div className="grid place-items-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center">
      <Inbox className="mb-3 text-slate-400" size={28} />
      <p className="font-medium text-slate-800">{title}</p>
      <p className="mt-1 text-sm text-slate-500">{action}</p>
    </div>
  );
}

function FormHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="mb-6">
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="text-sm text-slate-500">{subtitle}</p>
    </div>
  );
}

function Toast({ message }: { message: string }) {
  return (
    <div className="fixed bottom-5 right-5 hidden items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-lg xl:flex">
      <MessageSquareText size={16} />
      {message}
    </div>
  );
}
