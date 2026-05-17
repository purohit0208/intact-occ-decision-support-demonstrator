interface ExplanationCardProps {
  title: string;
  body: string;
  footnote?: string;
}

export function ExplanationCard({ title, body, footnote }: ExplanationCardProps) {
  return (
    <div className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
      <div className="text-sm font-semibold text-white">{title}</div>
      <p className="mt-2 text-sm leading-6 text-slate-300">{body}</p>
      {footnote ? <p className="mt-3 text-xs leading-5 text-slate-400">{footnote}</p> : null}
    </div>
  );
}
