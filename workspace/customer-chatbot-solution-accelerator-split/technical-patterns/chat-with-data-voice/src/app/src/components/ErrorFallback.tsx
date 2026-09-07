import type { FallbackProps } from 'react-error-boundary';

import { Button } from '@/components/ui/button';

export function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="grid min-h-screen place-items-center bg-slate-50 p-6 text-slate-900">
      <div className="max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Application error</p>
        <h1 className="mt-2 text-xl font-semibold">Something stopped the app from rendering.</h1>
        <p className="mt-3 text-sm text-slate-600">{error.message}</p>
        <div className="mt-6">
          <Button onClick={resetErrorBoundary}>Try again</Button>
        </div>
      </div>
    </div>
  );
}
