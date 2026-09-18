import { expect, test, type Page } from '@playwright/test';

const manager = { id: 'manager', name: 'Gerencia', role: 'gerente', responsable: null,
  sections: ['dashboard', 'inquilinos', 'pagos', 'parqueo', 'reportes'] };
type TestUser = { id: string; name: string; role: string; responsable: string | null; sections: string[] };

async function mockAuth(page: Page, options: { user?: TestUser; expiresIn?: number; badLogin?: boolean; badLogout?: boolean; offline?: boolean } = {}) {
  let authenticated = !!options.user;
  const expiresAt = new Date(Date.now() + (options.expiresIn ?? 600000)).toISOString();
  await page.route('http://localhost:8000/**', async route => {
    if (options.offline) { await route.abort('failed'); return; }
    const path = new URL(route.request().url()).pathname;
    if (path === '/auth/login') {
      if (options.badLogin) { await route.fulfill({ status: 401, json: {} }); return; }
      authenticated = true;
    }
    if (path === '/auth/logout') {
      if (options.badLogout) { await route.fulfill({ status: 500, json: {} }); return; }
      authenticated = false;
      await route.fulfill({ status: 204 }); return;
    }
    await route.fulfill({ status: authenticated ? 200 : 401,
      json: authenticated ? { user: options.user ?? manager, expiresAt } : {} });
  });
}

test('acceso, restauracion de sesion y cierre', async ({ page }) => {
  await mockAuth(page);
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Iniciar sesion' })).toBeVisible();
  await page.getByLabel('Correo electronico').fill('gerencia@example.com');
  await page.getByLabel('Contrasena', { exact: true }).fill('contrasena-de-prueba');
  await page.getByRole('button', { name: 'Ingresar', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard', exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Dashboard', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Cerrar sesion' }).click();
  await expect(page.getByRole('heading', { name: 'Iniciar sesion' })).toBeVisible();
});

test('credenciales incorrectas conservan formulario y muestran error', async ({ page }) => {
  await mockAuth(page, { badLogin: true }); await page.goto('/');
  await page.getByLabel('Correo electronico').fill('incorrecto@example.com');
  await page.getByLabel('Contrasena', { exact: true }).fill('incorrecta');
  await page.getByRole('button', { name: 'Ingresar', exact: true }).click();
  await expect(page.getByRole('alert')).toHaveText('Correo o contrasena incorrectos.');
  await expect(page.getByRole('button', { name: 'Ingresar', exact: true })).toBeEnabled();
});

test('consulta no tiene acciones de escritura', async ({ page }) => {
  await mockAuth(page, { user: { ...manager, role: 'consulta', name: 'Consulta' } });
  await page.goto('/'); await page.getByRole('button', { name: 'Inquilinos', exact: false }).click();
  await expect(page.getByRole('button', { name: 'Nuevo inquilino' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: /^Editar / })).toHaveCount(0);
  await expect(page.getByRole('button', { name: /^Eliminar / })).toHaveCount(0);
  await expect(page.getByRole('button', { name: /^Ver detalle / }).first()).toBeVisible();
  await page.getByRole('button', { name: 'Pagos Cobros y abonos' }).click();
  await expect(page.getByRole('button', { name: 'Registrar pago' })).toHaveCount(0);
});

test('Billy ve su grupo y no ve informacion consolidada ajena', async ({ page }) => {
  await mockAuth(page, { user: { id: 'billy', name: 'Billy', role: 'encargado', responsable: 'Billy', sections: ['inquilinos', 'pagos', 'parqueo'] } });
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Lino', exact: true })).toHaveCount(0);
  await expect(page.getByText('Edgar Esquivel', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: /Dashboard/ })).toHaveCount(0);
  await page.getByRole('button', { name: 'Pagos Cobros y abonos' }).click();
  await expect(page.getByText('Edgar Esquivel', { exact: true })).toHaveCount(0);
  await page.getByRole('button', { name: 'Parqueo Espacios y vehiculos' }).click();
  await expect(page.getByRole('heading', { name: 'Sin registros disponibles' })).toBeVisible();
});

test('sesion expirada regresa al acceso', async ({ page }) => {
  await mockAuth(page, { user: manager, expiresIn: 2500 }); await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Iniciar sesion' })).toBeVisible({ timeout: 10000 });
  await expect(page.getByRole('alert')).toHaveText('Tu sesion vencio. Inicia sesion nuevamente.');
});

test('sin permisos muestra estado vacio y permite cerrar sesion', async ({ page }) => {
  await mockAuth(page, { user: { ...manager, sections: [] } }); await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Sin secciones habilitadas' })).toBeVisible();
  await expect(page.locator('nav button')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Cerrar sesion' })).toBeEnabled();
});

test('fallo de red muestra error recuperable', async ({ page }) => {
  await mockAuth(page, { offline: true }); await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('No pudimos conectar');
  await expect(page.getByRole('button', { name: 'Reintentar conexion' })).toBeVisible();
});

test('fallo de logout no simula cierre exitoso', async ({ page }) => {
  await mockAuth(page, { user: manager, badLogout: true }); await page.goto('/');
  await page.getByRole('button', { name: 'Cerrar sesion' }).click();
  await expect(page.getByRole('alert')).toContainText('No se pudo completar');
  await expect(page.getByRole('heading', { name: 'Dashboard', exact: true })).toBeVisible();
});

test('login legible en desktop y mobile', async ({ page }, testInfo) => {
  await mockAuth(page);
  for (const size of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(size); await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Iniciar sesion' })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.screenshot({ path: testInfo.outputPath(`login-${size.width}.png`), fullPage: true });
  }
});
