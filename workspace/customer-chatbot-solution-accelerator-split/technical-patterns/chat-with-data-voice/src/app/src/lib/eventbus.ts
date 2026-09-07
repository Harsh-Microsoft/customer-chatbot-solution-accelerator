type Handler<T = unknown> = (payload: T) => void;

const listeners = new Map<string, Set<Handler>>();

export function on<T = unknown>(event: string, handler: Handler<T>): () => void {
  const bucket = listeners.get(event) ?? new Set<Handler>();
  bucket.add(handler as Handler);
  listeners.set(event, bucket);
  return () => off(event, handler);
}

export function off<T = unknown>(event: string, handler: Handler<T>): void {
  listeners.get(event)?.delete(handler as Handler);
}

export function emit<T = unknown>(event: string, payload: T): void {
  listeners.get(event)?.forEach((handler) => handler(payload));
}
