import type { CatalogItem, CatalogPresentation } from '@/types';

export interface ItemPresentation {
  title: string;
  image: string;
  highlights: string[];
}

function resolveImage(image: string | undefined, defaultImage: string): string {
  const candidate = (image ?? '').trim();
  if (!candidate) {
    return defaultImage;
  }
  if (/^https?:\/\//i.test(candidate)) {
    return candidate;
  }
  return `/api/scenario/assets/${candidate.replace(/^\/+/, '')}`;
}

export function resolveItemPresentation(
  item: CatalogItem,
  presentation: CatalogPresentation,
): ItemPresentation {
  const itemKey = (item.id || '').trim();
  const alias = presentation.titleAliases[item.title?.trim() ?? ''] ?? itemKey;
  const record = presentation.items[itemKey] ?? presentation.items[alias];
  const highlights = record?.highlights?.length ? record.highlights : item.highlights ?? [];

  return {
    title: item.title,
    image: resolveImage(item.image, presentation.defaultImage),
    highlights: highlights.length > 0 ? highlights : [item.category],
  };
}
