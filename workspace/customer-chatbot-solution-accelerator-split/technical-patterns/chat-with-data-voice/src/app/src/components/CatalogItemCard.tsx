import type { CatalogCardVariant, CatalogItem, CatalogPresentation } from '@/types';
import { resolveItemPresentation } from '@/lib/resolveItemPresentation';

interface CatalogItemCardProps {
  item: CatalogItem;
  presentation: CatalogPresentation;
  variant: CatalogCardVariant;
}

export function CatalogItemCard({ item, presentation, variant }: CatalogItemCardProps) {
  const resolved = resolveItemPresentation(item, presentation);
  const compact = variant === 'list';

  return (
    <article className={`rounded-2xl border border-slate-200 bg-white shadow-sm ${compact ? 'p-4' : 'p-5'}`}>
      <div className={compact ? 'flex items-start gap-4' : 'space-y-4'}>
        <img
          src={resolved.image}
          alt={resolved.title}
          className={compact ? 'h-20 w-20 rounded-xl object-cover' : 'h-48 w-full rounded-xl object-cover'}
          loading="lazy"
        />
        <div className="space-y-3">
          <div>
            <h3 className="text-lg font-semibold text-slate-950">{resolved.title}</h3>
            <p className="text-sm text-slate-600">{item.category}</p>
          </div>
          <ul className="space-y-1 text-sm text-slate-700">
            {resolved.highlights.map((highlight) => (
              <li key={highlight}>• {highlight}</li>
            ))}
          </ul>
          {typeof item.price === 'number' ? (
            <div className="text-sm font-medium text-slate-900">{item.price.toFixed(2)}</div>
          ) : null}
        </div>
      </div>
    </article>
  );
}
