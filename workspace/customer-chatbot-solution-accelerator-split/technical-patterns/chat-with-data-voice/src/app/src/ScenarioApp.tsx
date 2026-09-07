import { useEffect } from 'react';
import { AppHeader } from '@/components/Layout/AppHeader';
import { useHostConfig } from '@/lib/hostConfig';
import { CatalogApp } from '@/CatalogApp';
import { embedChatWidget } from '@/embedChatWidget';

export function ScenarioApp() {
  const host = useHostConfig();

  useEffect(() => {
    if (host.appTitle) {
      document.title = host.appTitle;
    }
  }, [host.appTitle]);

  // Mounts the shadow-DOM chat widget (chat-app widget.js) once per page load.
  useEffect(() => {
    embedChatWidget();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <AppHeader />
      {host.complianceBanner ? <div className="border-b border-slate-200 bg-amber-50 px-6 py-2 text-center text-xs text-slate-700">{host.complianceBanner}</div> : null}
      <CatalogApp />
    </div>
  );
}
