import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section className="panel p-6">
      <div className="muted-label">Navigation</div>
      <h2 className="mt-2 text-2xl font-semibold text-white">Page not found</h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
        The requested route is not part of the local OCC demonstrator. Return to the dashboard to continue the
        presentation flow.
      </p>
      <Link
        to="/"
        className="mt-5 inline-flex rounded-2xl border border-signal.cyan/40 bg-signal.cyan/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-signal.cyan/20"
      >
        Return to dashboard
      </Link>
    </section>
  );
}
