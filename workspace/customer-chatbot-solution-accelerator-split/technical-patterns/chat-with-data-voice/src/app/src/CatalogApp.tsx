import { useEffect, useState } from 'react';
import { useScenarioConfig } from '@/contexts/ScenarioConfigProvider';
import { CatalogItemCard } from '@/components/CatalogItemCard';
import type { CatalogItem } from '@/types';
import { useHostConfig } from '@/lib/hostConfig';

export function CatalogApp() {
  const config = useScenarioConfig();
  const host = useHostConfig();
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    document.title = host.appTitle || document.title;
  }, [host.appTitle]);

  useEffect(() => {
    let cancelled = false;

    async function loadItems() {
      if (!config?.catalog.routePrefix) {
        return;
      }
      try {
        const response = await fetch(`${config.catalog.routePrefix}/`, { credentials: 'include' });
        if (!response.ok) {
          throw new Error(`Catalog request failed with ${response.status}`);
        }
        const data = (await response.json()) as CatalogItem[];
        if (!cancelled) {
          setItems(Array.isArray(data) ? data : []);
          setError('');
        }
      } catch {
        if (!cancelled) {
          setItems([]);
          setError(config?.catalog.copy.loadError ?? 'Unable to load data.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadItems();
    return () => {
      cancelled = true;
    };
  }, [config?.catalog.routePrefix, config?.catalog.copy.loadError]);

  if (!config) {
    return <div className="p-8 text-slate-600">Loading configuration...</div>;
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">
      <section className="mb-8 space-y-3">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">{config.welcome.hint}</p>
        <h1 className="text-3xl font-semibold text-slate-950">{config.welcome.title}</h1>
        <p className="max-w-2xl text-slate-600">{config.welcome.subtitle}</p>
        <p className="max-w-3xl text-base text-slate-700">{config.catalog.copy.intro}</p>
      </section>

      {loading ? <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-slate-600">Loading catalog...</div> : null}
      {error ? <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-rose-800">{error}</div> : null}

      <section className={config.catalog.cardVariant === 'grid' ? 'grid gap-4 md:grid-cols-2 xl:grid-cols-3' : 'space-y-4'}>
        {items.map((item) => (
          <CatalogItemCard key={item.id} item={item} presentation={config.presentation} variant={config.catalog.cardVariant} />
        ))}
      </section>
    </main>
  );
}
