export async function safeAsync<T>(fn: () => Promise<T>, fallback: T): Promise<{ data: T; error: unknown }>{
  try {
    const data = await fn();
    return { data, error: null };
  } catch (err) {
    logError(err);
    return { data: fallback, error: err };
  }
}

export function logError(error: unknown, context?: Record<string, unknown>) {
  if (process.env.NODE_ENV !== 'production') {
    console.error(context, error);
  }
}

export function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
