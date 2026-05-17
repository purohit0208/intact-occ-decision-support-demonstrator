import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";

type Props = {
  children: ReactNode;
};

type State = {
  hasError: boolean;
};

export class AppErrorBoundary extends Component<Props, State> {
  override state: State = {
    hasError: false,
  };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Frontend runtime error", error, errorInfo);
  }

  private readonly handleReload = () => {
    window.location.assign("/");
  };

  override render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(84,209,219,0.12),_transparent_32%),linear-gradient(180deg,_#07111d_0%,_#09131f_48%,_#0c1520_100%)] px-4 py-8 text-slate-100">
          <div className="mx-auto max-w-3xl rounded-3xl border border-panelEdge/80 bg-panel/90 p-6 shadow-panel">
            <div className="flex items-center gap-3 text-signal.amber">
              <AlertTriangle className="h-5 w-5" />
              <div className="text-sm font-semibold uppercase tracking-[0.2em]">Application status</div>
            </div>
            <h1 className="mt-4 text-2xl font-semibold text-white">The OCC demonstrator encountered a frontend error.</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
              Reload the dashboard to restore the local session. If the issue persists, restart the backend and frontend
              with the provided launcher and try again.
            </p>
            <button
              type="button"
              onClick={this.handleReload}
              className="mt-5 inline-flex items-center gap-2 rounded-2xl border border-signal.cyan/40 bg-signal.cyan/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-signal.cyan/20"
            >
              <RotateCcw className="h-4 w-4" />
              Reload dashboard
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
