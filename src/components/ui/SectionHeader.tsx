export function SectionHeader({
  label,
  title,
  description
}: {
  label: string;
  title: string;
  description: string;
}) {
  return (
    <div className="mx-auto max-w-3xl text-center">
      <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary">{label}</p>
      <h2 className="mt-4 text-3xl font-semibold tracking-normal text-text sm:text-5xl">{title}</h2>
      <p className="mt-5 text-base leading-8 text-muted sm:text-lg">{description}</p>
    </div>
  );
}
