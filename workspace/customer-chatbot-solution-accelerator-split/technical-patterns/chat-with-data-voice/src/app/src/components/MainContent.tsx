import type { ReactNode } from 'react';

interface MainContentProps {
  children?: ReactNode;
  itemCount?: number;
  isLoading?: boolean;
}

export function MainContent({ children, itemCount = 0, isLoading = false }: MainContentProps) {
  return (
    <div className="h-full flex flex-col">
      <div className="p-4 pt-6">
        <div className="flex items-center justify-between">
          <span className="text-lg font-semibold">Results</span>
          <span className="text-sm text-muted-foreground">
            {isLoading ? 'Loading…' : `Showing ${itemCount} results`}
          </span>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-4 pt-0">
        <div className="max-w-full">{children}</div>
      </div>
    </div>
  );
}
