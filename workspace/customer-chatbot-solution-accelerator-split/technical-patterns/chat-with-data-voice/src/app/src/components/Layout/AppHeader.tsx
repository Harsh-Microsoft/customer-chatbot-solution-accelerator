import { useHostConfig } from '@/lib/hostConfig';

export function AppHeader() {
  const host = useHostConfig();

  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          {host.iconPath ? <img src={host.iconPath} alt={host.appTitle} className="h-8 w-8 rounded-lg" /> : null}
          <div>
            <div className="text-base font-semibold text-slate-950">{host.appTitle}</div>
            <div className="text-sm text-slate-500">{host.widgetTheme}</div>
          </div>
        </div>
        {host.assistantIconPath ? <img src={host.assistantIconPath} alt="Assistant" className="h-8 w-8 rounded-full" /> : null}
      </div>
    </header>
  );
}
