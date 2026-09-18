import { LoaderCircle, ShieldAlert, Inbox, RefreshCw } from 'lucide-react';

type Props = { kind: 'loading' | 'error' | 'empty'; title: string; message?: string; onRetry?: () => void };
export function ViewState({ kind, title, message, onRetry }: Props) {
  const Icon = kind === 'loading' ? LoaderCircle : kind === 'error' ? ShieldAlert : Inbox;
  return <div className="view-state" role={kind === 'error' ? 'alert' : 'status'} aria-live="polite">
    <Icon size={28} className={kind === 'loading' ? 'loading-icon' : ''} aria-hidden="true" />
    <h2>{title}</h2>
    {message && <p>{message}</p>}
    {onRetry && <button className="ghost-button" onClick={onRetry} type="button"><RefreshCw size={16} /> Reintentar</button>}
  </div>;
}
