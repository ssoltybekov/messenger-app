const API = 'http://127.0.0.1:8000';
let accessToken = localStorage.getItem('access_token') || null;
let currentUser = JSON.parse(localStorage.getItem('current_user') || 'null');
let currentChatId = null;
let isGroup = false;
let pollInterval = null;

// ── AUTH ──────────────────────────────────────────────────────
function switchTab(tab) {
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('login-form').style.display = tab === 'login' ? 'block' : 'none';
  document.getElementById('register-form').style.display = tab === 'register' ? 'block' : 'none';
  hideError('auth-error');
}

function showError(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.style.display = 'block';
}

function hideError(id) {
  document.getElementById(id).style.display = 'none';
}

async function login() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  if (!username || !password) return showError('auth-error', 'Заполните все поля');

  try {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (!res.ok) return showError('auth-error', data.detail || 'Ошибка входа');

    accessToken = data.access_token;
    localStorage.setItem('access_token', accessToken);
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token);

    await loadCurrentUser(username);
    showApp();
  } catch (e) {
    showError('auth-error', 'Ошибка подключения к серверу');
  }
}

async function register() {
  const username = document.getElementById('reg-username').value.trim();
  const phone = document.getElementById('reg-phone').value.trim();
  const password = document.getElementById('reg-password').value;
  if (!username || !password) return showError('auth-error', 'Заполните обязательные поля');

  try {
    const res = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, phone: phone || null, password })
    });
    const data = await res.json();
    if (!res.ok) return showError('auth-error', data.detail || 'Ошибка регистрации');

    // Auto login after register
    document.getElementById('login-username').value = username;
    document.getElementById('login-password').value = password;
    switchTab('login');
    await login();
  } catch (e) {
    showError('auth-error', 'Ошибка подключения к серверу');
  }
}

async function loadCurrentUser(username) {
  currentUser = { username };
  localStorage.setItem('current_user', JSON.stringify(currentUser));
}

function logout() {
  const refresh = localStorage.getItem('refresh_token');
  if (refresh) {
    fetch(`${API}/auth/logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
      body: JSON.stringify({ refresh_token: refresh })
    }).catch(() => {});
  }
  accessToken = null;
  currentUser = null;
  currentChatId = null;
  localStorage.clear();
  if (pollInterval) clearInterval(pollInterval);
  document.getElementById('app-screen').style.display = 'none';
  document.getElementById('auth-screen').style.display = 'flex';
}

// ── APP ───────────────────────────────────────────────────────
function showApp() {
  document.getElementById('auth-screen').style.display = 'none';
  const app = document.getElementById('app-screen');
  app.style.display = 'flex';

  const name = currentUser?.username || '?';
  document.getElementById('user-display-name').textContent = name;
  document.getElementById('user-avatar-letter').textContent = name[0].toUpperCase();

  loadChats();
}

async function authFetch(url, options = {}) {
  options.headers = options.headers || {};
  options.headers['Authorization'] = `Bearer ${accessToken}`;
  return fetch(url, options);
}

// ── CHATS ─────────────────────────────────────────────────────
async function loadChats() {
  try {
    const res = await authFetch(`${API}/chats/`);
    if (!res.ok) { if (res.status === 401) { logout(); return; } }
    const chats = await res.json();
    renderChats(chats);
  } catch (e) {
    document.getElementById('chats-list').innerHTML = '<div class="no-chats">Ошибка загрузки</div>';
  }
}

function renderChats(chats) {
  const list = document.getElementById('chats-list');
  if (!chats.length) {
    list.innerHTML = '<div class="no-chats">Нет чатов<br/>Создайте первый →</div>';
    return;
  }

  list.innerHTML = chats.map(chat => {
    const name = chat.name || (chat.is_group ? 'Группа' : 'Личный чат');
    const letter = name[0].toUpperCase();
    const type = chat.is_group ? 'группа' : 'личный';
    const active = chat.id === currentChatId ? 'active' : '';
    return `
      <div class="chat-item ${active}" onclick="openChat(${chat.id}, '${escHtml(name)}', ${chat.is_group})">
        <div class="chat-avatar">${letter}</div>
        <div class="chat-info">
          <div class="chat-name">${escHtml(name)}</div>
          <div class="chat-meta">${type}</div>
        </div>
      </div>
    `;
  }).join('');
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── OPEN CHAT ─────────────────────────────────────────────────
function openChat(chatId, name, isGroupChat) {
  currentChatId = chatId;

  document.getElementById('empty-state').style.display = 'none';
  const chatView = document.getElementById('chat-view');
  chatView.style.display = 'flex';

  const letter = name[0].toUpperCase();
  document.getElementById('chat-header-avatar').textContent = letter;
  document.getElementById('chat-header-name').textContent = name;
  document.getElementById('chat-header-meta').textContent = isGroupChat ? 'группа' : 'личный чат';

  loadChats(); // refresh active state
  loadMessages();

  if (pollInterval) clearInterval(pollInterval);
  pollInterval = setInterval(loadMessages, 3000);

  document.getElementById('message-input').focus();
}

// ── MESSAGES ──────────────────────────────────────────────────
async function loadMessages() {
  if (!currentChatId) return;
  try {
    const res = await authFetch(`${API}/messages/${currentChatId}`);
    if (!res.ok) return;
    const msgs = await res.json();
    renderMessages(msgs);
  } catch (e) {}
}

function renderMessages(msgs) {
  const area = document.getElementById('messages-area');
  if (!msgs.length) {
    area.innerHTML = '<div style="text-align:center; font-family: IBM Plex Mono, monospace; font-size:10px; color: var(--text3); margin-top: 40px;">Нет сообщений. Напишите первым!</div>';
    return;
  }

  const myId = currentUser?.id;
  area.innerHTML = msgs.map(msg => {
    const isOwn = msg.sender_id === myId;
    const cls = isOwn ? 'own' : 'other';
    const time = new Date(msg.created_at).toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' });
    return `
      <div class="msg ${cls}">
        ${!isOwn ? `<div class="msg-sender">id:${msg.sender_id}</div>` : ''}
        ${escHtml(msg.content)}
        <div class="msg-time">${time}</div>
      </div>
    `;
  }).join('');

  area.scrollTop = area.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById('message-input');
  const content = input.value.trim();
  if (!content || !currentChatId) return;

  input.value = '';
  autoResize(input);

  try {
    const res = await authFetch(`${API}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: currentChatId, content })
    });
    if (res.ok) loadMessages();
  } catch (e) {}
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// ── NEW CHAT MODAL ─────────────────────────────────────────────
function openNewChatModal() {
  document.getElementById('new-chat-modal').classList.add('open');
  document.getElementById('new-chat-name').value = '';
  hideError('chat-error');
  isGroup = false;
  selectChatType(false);
}

function closeNewChatModal() {
  document.getElementById('new-chat-modal').classList.remove('open');
}

function selectChatType(group) {
  isGroup = group;
  document.getElementById('toggle-personal').classList.toggle('selected', !group);
  document.getElementById('toggle-group').classList.toggle('selected', group);
}

async function createChat() {
  const name = document.getElementById('new-chat-name').value.trim() || null;
  try {
    const res = await authFetch(`${API}/chats/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, is_group: isGroup, is_public: false, participant_ids: [] })
    });
    const data = await res.json();
    if (!res.ok) return showError('chat-error', data.detail || 'Ошибка создания');

    closeNewChatModal();
    await loadChats();
    const chatName = data.name || (isGroup ? 'Группа' : 'Личный чат');
    openChat(data.id, chatName, data.is_group);
  } catch (e) {
    showError('chat-error', 'Ошибка подключения');
  }
}

// ── INIT ──────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  if (accessToken && currentUser) {
    showApp();
  }

  // Enter to submit auth forms
  document.getElementById('login-password').addEventListener('keydown', e => {
    if (e.key === 'Enter') login();
  });
});
