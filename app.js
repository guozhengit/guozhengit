const root = document.documentElement;
const themeButton = document.querySelector('.theme-toggle');
const label = document.querySelector('[data-theme-label]');

function setTheme(theme) {
  const light = theme === 'light';
  root.dataset.theme = light ? 'light' : 'dark';
  themeButton.setAttribute('aria-pressed', String(light));
  themeButton.setAttribute('aria-label', light ? '切换为深色主题' : '切换为浅色主题');
  label.textContent = light ? '深色' : '浅色';
}

try {
  setTheme(localStorage.getItem('profile-theme'));
} catch {
  setTheme('dark');
}

themeButton.addEventListener('click', () => {
  const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
  setTheme(theme);
  try {
    localStorage.setItem('profile-theme', theme);
  } catch {
    // Storage can be disabled while the theme switch remains usable.
  }
});

function revealNote() {
  const target = document.getElementById(location.hash.slice(1));
  if (target instanceof HTMLDetailsElement) target.open = true;
}

for (const link of document.querySelectorAll('[data-note-link]')) {
  link.addEventListener('click', () => {
    const target = document.getElementById(link.hash.slice(1));
    if (target instanceof HTMLDetailsElement) target.open = true;
  });
}
window.addEventListener('hashchange', revealNote);
revealNote();
