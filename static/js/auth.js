/**
 * auth.js — Manejo de sesión con token en localStorage
 * Portal de Egresados TecNM
 */

const API = 'http://localhost:5000/api';

let currentUser = null;

// ─────────────────────────────────────────────────────────────
// Token helpers
// ─────────────────────────────────────────────────────────────
function getToken() {
  return localStorage.getItem('tecnm_token') || '';
}

function setToken(token) {
  localStorage.setItem('tecnm_token', token);
}

function clearToken() {
  localStorage.removeItem('tecnm_token');
  localStorage.removeItem('tecnm_user');
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-Auth-Token': getToken()
  };
}

// ─────────────────────────────────────────────────────────────
// Verificar sesión activa
// ─────────────────────────────────────────────────────────────
async function checkSession() {
  const token = getToken();
  if (!token) {
    currentUser = null;
    updateNavAuthArea();
    return null;
  }
  try {
    const res  = await fetch(`${API}/auth/me`, {
      headers: { 'X-Auth-Token': token }
    });
    const data = await res.json();
    if (data.authenticated) {
      currentUser = data.user;
      updateNavAuthArea();
      return data.user;
    }
  } catch (e) {}
  clearToken();
  currentUser = null;
  updateNavAuthArea();
  return null;
}

// ─────────────────────────────────────────────────────────────
// Navbar
// ─────────────────────────────────────────────────────────────
function updateNavAuthArea() {
  const area = document.getElementById('nav-auth-area');
  if (!area) return;

  if (currentUser) {
    const role    = currentUser.role;
    const isAdmin = role === 'admin';
    const isOrg   = role === 'organizacion';
    const isEgr   = role === 'egresado';

    const roleLabel = isAdmin ? 'Administrador' : isOrg ? 'Organización' : 'Egresado';
    const roleIcon  = isAdmin ? 'fa-shield-halved' : isOrg ? 'fa-building' : 'fa-user-graduate';

    // Quick link solo para admin (Panel Admin)
    const quickLink = isAdmin
      ? `<a href="admin.html" class="font-semibold text-sm flex items-center gap-1" style="color:#E8A020"><i class="fas fa-shield-halved"></i><span class="hidden lg:inline">Panel Admin</span></a>`
      : '';

    // Ítem de cuestionario en el dropdown — mismo estilo para egresado y organización
    const cuestionarioItem = isEgr
      ? `<a href="cuestionario.html" class="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50" style="color:#1A3A5C"><i class="fas fa-clipboard-list w-4"></i>Cuestionario Egresados</a>`
      : isOrg
      ? `<a href="cuestionario_organizacion.html" class="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50" style="color:#1A3A5C"><i class="fas fa-building w-4"></i>Mi Cuestionario</a>`
      : '';

    area.innerHTML = `
      <div class="flex items-center gap-3">
        ${quickLink}
        <div class="relative group">
          <button class="flex items-center gap-2 border border-gray-200 rounded px-3 py-2 text-sm font-medium text-gray-700 transition">
            <div class="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold" style="background:#1A3A5C">
              ${currentUser.nombre.charAt(0).toUpperCase()}
            </div>
            <span class="hidden lg:inline max-w-28 truncate">${currentUser.nombre}</span>
            <i class="fas fa-chevron-down text-xs text-gray-400"></i>
          </button>
          <div class="absolute right-0 mt-1 w-52 bg-white border border-gray-200 rounded-lg shadow-lg py-1 hidden group-hover:block z-50">
            <div class="px-4 py-2 border-b border-gray-100">
              <p class="text-xs font-semibold text-gray-900 truncate">${currentUser.nombre}</p>
              <p class="text-xs text-gray-400"><i class="fas ${roleIcon} mr-1"></i>${roleLabel}</p>
            </div>
            ${isAdmin ? `<a href="admin.html" class="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50" style="color:#1A3A5C"><i class="fas fa-users-gear w-4"></i>Gestionar usuarios</a>` : ''}
            ${cuestionarioItem}
            <button onclick="doLogout()" class="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 text-left">
              <i class="fas fa-sign-out-alt w-4"></i>Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    `;
  } else {
    area.innerHTML = `
      <button onclick="showLoginModal()"
        class="flex items-center gap-2 border px-4 py-2 rounded font-semibold text-sm transition duration-200"
        style="border-color:#1A3A5C; color:#1A3A5C;"
        onmouseover="this.style.background='#1A3A5C';this.style.color='white'"
        onmouseout="this.style.background='';this.style.color='#1A3A5C'">
        <i class="fas fa-sign-in-alt"></i>
        <span>Iniciar Sesión</span>
      </button>
    `;
  }
}

// ─────────────────────────────────────────────────────────────
// Modal de login
// ─────────────────────────────────────────────────────────────
function showLoginModal() {
  if (!document.getElementById('login-modal')) {
    const modal = document.createElement('div');
    modal.id = 'login-modal';
    modal.className = 'fixed inset-0 z-[200] flex items-center justify-center p-4';
    modal.innerHTML = `
      <div class="absolute inset-0 bg-black/50" onclick="hideLoginModal()"></div>
      <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-sm p-8 z-10">
        <div class="flex items-center gap-3 mb-7">
          <div class="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0" style="background:#1A3A5C">
            <i class="fas fa-lock text-white text-lg"></i>
          </div>
          <div>
            <h2 class="text-xl font-bold" style="color:#1A3A5C">Iniciar Sesión</h2>
            <p class="text-xs text-gray-400">Portal de Egresados TecNM</p>
          </div>
          <button onclick="hideLoginModal()" class="ml-auto text-gray-300 hover:text-gray-500 transition">
            <i class="fas fa-times text-lg"></i>
          </button>
        </div>
        <div id="login-error" class="hidden mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-sm text-red-700">
          <i class="fas fa-exclamation-circle text-red-500"></i>
          <span id="login-error-msg"></span>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-gray-700 text-xs font-semibold mb-1 uppercase tracking-wide">Usuario</label>
            <div class="relative">
              <i class="fas fa-user absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
              <input id="login-username" type="text" placeholder="Tu nombre de usuario"
                class="w-full pl-9 pr-4 py-2.5 rounded-lg border border-gray-200 focus:outline-none focus:border-blue-900 text-sm"
                onkeydown="if(event.key==='Enter') doLogin()">
            </div>
          </div>
          <div>
            <label class="block text-gray-700 text-xs font-semibold mb-1 uppercase tracking-wide">Contraseña</label>
            <div class="relative">
              <i class="fas fa-lock absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
              <input id="login-password" type="password" placeholder="Tu contraseña"
                class="w-full pl-9 pr-10 py-2.5 rounded-lg border border-gray-200 focus:outline-none focus:border-blue-900 text-sm"
                onkeydown="if(event.key==='Enter') doLogin()">
              <button type="button" onclick="togglePasswordVisibility()" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                <i id="eye-icon" class="fas fa-eye text-sm"></i>
              </button>
            </div>
          </div>
          <button id="login-btn" onclick="doLogin()"
            class="w-full text-white py-3 rounded-lg font-semibold text-sm transition duration-200 flex items-center justify-center gap-2 mt-2"
            style="background:#1A3A5C">
            <i class="fas fa-sign-in-alt"></i>
            Entrar
          </button>
        </div>
        <p class="text-center text-xs text-gray-400 mt-5">
          Para obtener una cuenta, contacta al administrador del sistema.
        </p>
      </div>
    `;
    document.body.appendChild(modal);
  }
  const modal = document.getElementById('login-modal');
  modal.classList.remove('hidden');
  document.getElementById('login-error').classList.add('hidden');
  document.getElementById('login-username').value = '';
  document.getElementById('login-password').value = '';
  setTimeout(() => document.getElementById('login-username').focus(), 100);
}

function hideLoginModal() {
  const modal = document.getElementById('login-modal');
  if (modal) modal.classList.add('hidden');
}

function togglePasswordVisibility() {
  const input = document.getElementById('login-password');
  const icon  = document.getElementById('eye-icon');
  if (input.type === 'password') {
    input.type = 'text';
    icon.classList.replace('fa-eye', 'fa-eye-slash');
  } else {
    input.type = 'password';
    icon.classList.replace('fa-eye-slash', 'fa-eye');
  }
}

async function doLogin() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const btn      = document.getElementById('login-btn');
  const errorDiv = document.getElementById('login-error');

  if (!username || !password) {
    showLoginError('Por favor ingresa usuario y contraseña.');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verificando...';
  errorDiv.classList.add('hidden');

  try {
    const res  = await fetch(`${API}/auth/login`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ username, password })
    });
    const data = await res.json();

    if (data.success) {
      setToken(data.token);
      currentUser = data.user;
      hideLoginModal();
      updateNavAuthArea();
      document.dispatchEvent(new CustomEvent('auth:login', { detail: data.user }));
    } else {
      showLoginError(data.error || 'Credenciales incorrectas.');
    }
  } catch (e) {
    showLoginError('No se pudo conectar al servidor. ¿Está corriendo app.py?');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Entrar';
  }
}

function showLoginError(msg) {
  const div = document.getElementById('login-error');
  document.getElementById('login-error-msg').textContent = msg;
  div.classList.remove('hidden');
}

async function doLogout() {
  try {
    await fetch(`${API}/auth/logout`, {
      method:  'POST',
      headers: { 'X-Auth-Token': getToken() }
    });
  } catch(e) {}
  clearToken();
  currentUser = null;
  updateNavAuthArea();
  document.dispatchEvent(new CustomEvent('auth:logout'));
  const protectedPages = ['cuestionario.html', 'admin.html', 'egresados_lista.html'];
  const page = window.location.pathname.split('/').pop();
  if (protectedPages.includes(page)) window.location.href = 'index.html';
}

// ─────────────────────────────────────────────────────────────
// Utilidades de protección de páginas
// ─────────────────────────────────────────────────────────────
async function requireAuth(onSuccess, onFail) {
  const user = await checkSession();
  if (user) {
    if (onSuccess) onSuccess(user);
  } else {
    if (onFail) onFail();
    else showAuthWall();
  }
  return user;
}

async function requireAdmin(onSuccess, onFail) {
  const user = await checkSession();
  if (user && user.role === 'admin') {
    if (onSuccess) onSuccess(user);
  } else if (user) {
    if (onFail) onFail();
    else window.location.href = 'index.html';
  } else {
    showLoginModal();
    document.addEventListener('auth:login', (e) => {
      if (e.detail.role === 'admin') {
        if (onSuccess) onSuccess(e.detail);
      } else {
        window.location.href = 'index.html';
      }
    }, { once: true });
  }
  return user;
}

// ─────────────────────────────────────────────────────────────
// Muro de acceso
// ─────────────────────────────────────────────────────────────
function showAuthWall(message) {
  const main = document.getElementById('protected-content');
  if (main) main.classList.add('hidden');

  const existing = document.getElementById('auth-wall');
  if (existing) { existing.classList.remove('hidden'); return; }

  const div = document.createElement('div');
  div.id = 'auth-wall';
  div.className = 'min-h-screen flex items-center justify-center bg-gray-50 p-6';
  div.innerHTML = `
    <div class="text-center max-w-sm">
      <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6" style="background:#1A3A5C">
        <i class="fas fa-lock text-white text-3xl"></i>
      </div>
      <h2 class="text-2xl font-bold mb-3" style="color:#1A3A5C">Contenido Restringido</h2>
      <p class="text-gray-500 text-sm mb-7">${message || 'Debes iniciar sesión para acceder a esta sección.'}</p>
      <button onclick="showLoginModal(); document.addEventListener('auth:login', () => location.reload(), {once:true});"
        class="text-white px-8 py-3 rounded-lg font-semibold transition duration-200 inline-flex items-center gap-2"
        style="background:#E8A020">
        <i class="fas fa-sign-in-alt"></i>Iniciar Sesión
      </button>
    </div>
  `;
  const nav = document.querySelector('nav');
  if (nav && nav.nextSibling) nav.parentNode.insertBefore(div, nav.nextSibling);
  else document.body.appendChild(div);
}

// ─────────────────────────────────────────────────────────────
// Init automático
// ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  checkSession();
});
