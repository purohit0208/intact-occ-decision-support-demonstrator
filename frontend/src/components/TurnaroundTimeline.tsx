const proactiveTimeline = [
  { time: "-25 min", title: "Aircraft-side report received", body: "Structured malfunction, assistance, and inventory signals reach the OCC before landing." },
  { time: "-18 min", title: "OCC dispatches preparatory actions", body: "Maintenance, catering, or PRM teams are pre-briefed while the aircraft is still inbound." },
  { time: "-10 min", title: "Stand resources confirmed", body: "Gate coordination reserves buffer and clarifies stand-side sequencing." },
  { time: "0 min", title: "Arrival with prepared teams", body: "Turnaround starts with higher readiness and fewer avoidable coordination gaps." },
];

const reactiveTimeline = [
  { time: "0 min", title: "Issue recognized on stand", body: "Key maintenance, inventory, or assistance needs are addressed only after arrival." },
  { time: "+6 min", title: "Manual coordination begins", body: "Teams are called after the discrepancy becomes visible at the gate." },
  { time: "+12 min", title: "Resource conflicts emerge", body: "Compressed turnaround margin increases the chance of queueing and handoff delays." },
  { time: "+18 min", title: "Knock-on risk increases", body: "Operational pressure shifts toward reactive delay management rather than proactive coordination." },
];

interface TimelineColumnProps {
  title: string;
  toneClass: string;
  items: typeof proactiveTimeline;
}

function TimelineColumn({ title, toneClass, items }: TimelineColumnProps) {
  return (
    <div className="rounded-3xl border border-panelEdge/80 bg-slate-950/35 p-5">
      <div className={`text-sm font-semibold uppercase tracking-[0.2em] ${toneClass}`}>{title}</div>
      <div className="mt-5 space-y-4">
        {items.map((item) => (
          <div key={`${title}-${item.time}`} className="rounded-2xl border border-panelEdge/70 bg-slate-950/30 p-4">
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{item.time}</div>
            <div className="mt-2 text-sm font-semibold text-white">{item.title}</div>
            <p className="mt-2 text-sm leading-6 text-slate-300">{item.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function TurnaroundTimeline() {
  return (
    <section className="panel p-5">
      <div className="muted-label">Turnaround comparison timeline</div>
      <h3 className="mt-2 panel-title">Proactive versus reactive coordination sequence</h3>
      <div className="mt-5 grid gap-4 xl:grid-cols-2">
        <TimelineColumn title="Proactive coordination" toneClass="text-emerald-300" items={proactiveTimeline} />
        <TimelineColumn title="Reactive coordination" toneClass="text-amber-300" items={reactiveTimeline} />
      </div>
    </section>
  );
}
