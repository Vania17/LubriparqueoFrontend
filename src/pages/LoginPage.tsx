import { useState, type FormEvent } from 'react';
import { Eye, EyeOff, LogIn, LoaderCircle } from 'lucide-react';
import { useAuth } from '../auth/context';
import { demoAuth } from '../services/auth';
import { FormField } from '../components/FormField';

export function LoginPage() {
  const { login, loginDemo, message, status, retry } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [visible, setVisible] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const data = new FormData(event.currentTarget);
    setBusy(true); setError('');
    try {
      if (demoAuth) loginDemo(String(data.get('profile')));
      else await login(String(data.get('email')).trim(), String(data.get('password')));
    } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo iniciar sesion.'); }
    finally { setBusy(false); }
  }
  return <main className="login-shell">
    <section className="login-panel" aria-labelledby="login-title">
      <div className="brand"><span className="brand-mark">L</span><div><p className="brand-name">Lubriparqueo</p><p className="brand-caption">Control administrativo</p></div></div>
      <div><h1 id="login-title">Iniciar sesion</h1><p>Accede a tu cuenta.</p></div>
      {demoAuth && <p className="auth-notice">Entorno de prueba</p>}
      {(error || message) && <div className="auth-error" role="alert">{error || message}</div>}
      {status === 'error' && <button className="ghost-button" onClick={retry} type="button">Reintentar conexion</button>}
      <form onSubmit={submit} className="login-form" aria-busy={busy}>
        {demoAuth ? <FormField label="Perfil de prueba"><select name="profile" disabled={busy}><option value="gerente">Gerencia</option><option value="encargada">Administracion</option><option value="billy">Billy</option><option value="lino">Lino</option><option value="consulta">Solo consulta</option></select></FormField> : <>
          <FormField label="Correo electronico"><input name="email" type="email" autoComplete="username" required maxLength={254} disabled={busy} /></FormField>
          <FormField label="Contrasena"><div className="password-field"><input name="password" type={visible ? 'text' : 'password'} autoComplete="current-password" required maxLength={256} disabled={busy} /><button className="icon-button" type="button" title={visible ? 'Ocultar contrasena' : 'Mostrar contrasena'} aria-label={visible ? 'Ocultar contrasena' : 'Mostrar contrasena'} aria-pressed={visible} onClick={() => setVisible(!visible)}>{visible ? <EyeOff size={18} /> : <Eye size={18} />}</button></div></FormField>
        </>}
        <button className="primary-button auth-submit" disabled={busy} type="submit">{busy ? <LoaderCircle className="loading-icon" size={18} /> : <LogIn size={18} />}{busy ? 'Ingresando...' : 'Ingresar'}</button>
      </form>
    </section>
  </main>;
}
