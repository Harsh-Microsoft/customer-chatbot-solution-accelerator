export function CatalogItemSkeleton() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 shadow-sm">
      <div className="h-4 w-24 animate-pulse rounded-full bg-slate-200" />
      <div className="mt-4 h-40 animate-pulse rounded-2xl bg-slate-200" />
      <div className="mt-4 space-y-2">
        <div className="h-3 w-3/4 animate-pulse rounded-full bg-slate-200" />
        <div className="h-3 w-2/3 animate-pulse rounded-full bg-slate-200" />
      </div>
    </div>
  );
}
