interface KPIItem {
  label: string;
  value: string;
  note?: string;
}

interface KPIWidgetsProps {
  items: KPIItem[];
}

export function KPIWidgets({ items }: KPIWidgetsProps) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
          <div className="muted-label">{item.label}</div>
          <div className="mt-3 text-2xl font-semibold text-white">{item.value}</div>
          {item.note ? <div className="mt-2 text-sm text-slate-400">{item.note}</div> : null}
        </div>
      ))}
    </div>
  );
}
