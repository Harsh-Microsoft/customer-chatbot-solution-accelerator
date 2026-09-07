import type { CatalogItem } from '@/types';

// Ported from chat-app/frontend/src/lib/textParsers.ts (plan row 24), de-domained:
// `Product` -> `CatalogItem`, the hardcoded 'Paint Shades' fallback category is
// dropped, and order-text parsing is removed entirely (cart/orders skip, plan
// section 7.1 - there is no order-tracking surface left to parse).

export function stripMarkdown(text: string): string {
  return text
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/[*_`>#-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export function splitParagraphs(text: string): string[] {
  return text.split(/\n{2,}/).map((part) => part.trim()).filter(Boolean);
}

export function detectContentType(text: string): 'catalog' | 'text' {
  const hasCatalogFormat = /\d+\.\s*\*\*[^*]+\*\*.*!\[/s.test(text);
  const hasPriceAndRating = text.includes('**Price:**') && text.includes('**Rating:**');
  const hasPriceAndImage = text.includes('**Price:**') && /!\[[^\]]+\]\([^)]+\)/.test(text);
  const hasNumberedPrice = /\d+\.\s*\*\*[^*]+\*\*[\s\S]*?\*\*Price:\*\*/.test(text);

  const hasImageOrLink = /!\[[^\]]+\]\([^)]+\)/.test(text) || /\[[^\]]+\]\([^)]+\.(jpg|jpeg|png|gif|webp|svg)/i.test(text);
  const hasImageWithDescription =
    hasImageOrLink &&
    (/\w+\s+is\s+(?:described\s+as|a\s+)/i.test(text) || /"[^"]+"\s+is\s+(?:described\s+as|a\s+)/i.test(text));

  if (hasPriceAndRating || hasCatalogFormat || hasImageWithDescription || hasPriceAndImage || hasNumberedPrice) {
    return 'catalog';
  }
  return 'text';
}

export function parseCatalogItemsFromText(text: string): { items: CatalogItem[]; introText: string; outroText: string } {
  const items: CatalogItem[] = [];
  const parts = text.split(/(?=\d+\.\s*\*\*[^*]+\*\*)/);

  let introText = '';
  let outroText = '';

  if (parts.length > 0) {
    introText = parts[0].trim().replace(/^###\s*[^\n]*\n?/gm, '').trim();

    const lastItemIndex = text.lastIndexOf('![');
    if (lastItemIndex !== -1) {
      const afterLastItem = text.substring(lastItemIndex);
      const afterMatch = afterLastItem.match(/!\[[^\]]*\]\([^)]*\)\.?\s*([\s\S]*?)$/);
      if (afterMatch && afterMatch[1].trim()) {
        const afterText = afterMatch[1].trim();
        if (!afterText.match(/^\d+\.\s*\*\*/)) {
          outroText = afterText;
        }
      }
    }
  }

  for (let i = 1; i < parts.length; i++) {
    const item = parseCatalogItemSection(parts[i]);
    if (item) {
      items.push(item);
    }
  }

  const hasImageOrLink = parts.length === 1 && (parts[0].includes('![') || /\[[^\]]+\]\([^)]+\.(jpg|jpeg|png|gif|webp|svg)/i.test(parts[0]));
  if (hasImageOrLink) {
    const item = parseCatalogItemSection(parts[0]);
    if (item) {
      items.push(item);
      const escapedTitle = item.title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const itemPattern = new RegExp(`.*?${escapedTitle}.*?(?:!\\[.*?\\]|\\[.*?\\])\\(.*?\\).*?`, 's');
      introText = introText.replace(itemPattern, '').trim();
    }
  }

  return { items, introText, outroText };
}

function parseCatalogItemSection(section: string): CatalogItem | null {
  try {
    let title = '';
    const nameMatch = section.match(/\d+\.\s*\*\*([^*]+)\*\*/);
    if (nameMatch) {
      title = nameMatch[1].trim().replace(/:$/, '');
    } else {
      const imageAltMatch = section.match(/!\[([^\]]+)\]\([^)]+\)/);
      if (imageAltMatch && imageAltMatch[1]) {
        title = imageAltMatch[1].trim();
      } else {
        const quotedNameMatch = section.match(/^"([^"]+)"|^\*\*([^*]+)\*\*/);
        if (quotedNameMatch) {
          title = (quotedNameMatch[1] || quotedNameMatch[2] || '').trim();
        }
      }
    }

    if (!title) {
      const quotedBeforeDescribed = section.match(/^"([^"]+)"\s+is\s+(?:described\s+as|a\s+)/i);
      if (quotedBeforeDescribed) {
        title = quotedBeforeDescribed[1].trim();
      } else {
        const firstLineMatch = section.match(/^([A-Z][a-zA-Z\s]+?)\s+is\s+(?:described\s+as|a\s+)/i);
        if (firstLineMatch) {
          title = firstLineMatch[1].trim();
        }
      }
    }

    if (!title) {
      return null;
    }

    const priceMatch = section.match(/\*\*Price:\*\*\s*\$([0-9,]+\.?\d*)/);
    const price = priceMatch ? parseFloat(priceMatch[1].replace(',', '')) : undefined;

    const ratingMatch = section.match(/\*\*Rating:\*\*\s*([0-9.]+)/);
    const rating = ratingMatch ? parseFloat(ratingMatch[1]) : undefined;

    let description = '';
    const descMatch = section.match(/\*\*Description:\*\*\s*([^\n]+)/);
    if (descMatch) {
      description = descMatch[1].trim();
    } else {
      const escapedTitle = title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const isAMatch = section.match(new RegExp(`"${escapedTitle}"\\s+is\\s+(?:described\\s+as\\s+|a\\s+)(.+?)(?=If\\s+you're|!\\[|\\[[^\\]]+\\]\\(|$)`, 'is'));
      if (isAMatch) {
        description = isAMatch[1].trim();
      }
    }

    let image = '';
    const imageMatch = section.match(/!\[.*?\]\(([^)]+)\)/);
    if (imageMatch) {
      image = imageMatch[1];
    } else {
      const linkMatch = section.match(/\[[^\]]+\]\(([^)]+)\)/);
      if (linkMatch && /\.(jpg|jpeg|png|gif|webp|svg)(\?|$)/i.test(linkMatch[1])) {
        image = linkMatch[1];
      }
    }

    return {
      id: `catalog-${title.toLowerCase().replace(/\s+/g, '-')}`,
      title,
      price,
      rating,
      image,
      category: '',
      description,
    };
  } catch {
    return null;
  }
}
