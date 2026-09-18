const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const SESSION_EXPIRED_EVENT = 'lubriparqueo:session-expired';

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function apiRequest<TResponse>(
  path: string,
  options?: RequestInit,
): Promise<TResponse> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 15000);
  const headers = new Headers(options?.headers);
  if (options?.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  try {
    const response = await fetch(`${API_BASE_URL.replace(/\/$/, '')}${path}`, {
      ...options,
      headers,
      credentials: 'include',
      signal: options?.signal ? AbortSignal.any([options.signal, controller.signal]) : controller.signal,
    });
    if (!response.ok) {
      if (response.status === 401 && !path.startsWith('/auth/')) {
        window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
      }
      throw new ApiError(response.status, response.status === 403
        ? 'No tienes permiso para realizar esta accion.'
        : response.status === 401
          ? 'La sesion no es valida.'
          : 'No se pudo completar la solicitud. Intenta de nuevo.');
    }
    if (response.status === 204) return undefined as TResponse;
    return await response.json() as TResponse;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new Error('No pudimos conectar con el servidor. Revisa tu conexion e intenta de nuevo.');
  } finally {
    window.clearTimeout(timeout);
  }
}
