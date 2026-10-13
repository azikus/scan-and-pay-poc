'use strict';
// Apply before CSS. Persist appearance only, never credentials or invoice data.
const adminThemeMedia = window.matchMedia('(prefers-color-scheme: dark)');
let adminThemePreference = 'system';
try {
  const saved = localStorage.getItem('scanpay-admin-theme');
  if (['system', 'light', 'dark'].includes(saved)) adminThemePreference = saved;
} catch { /* Use the system default when storage is unavailable. */ }
function applyAdminTheme(preference) {
  adminThemePreference = ['system', 'light', 'dark'].includes(preference) ? preference : 'system';
  document.documentElement.dataset.theme = adminThemePreference === 'system'
    ? (adminThemeMedia.matches ? 'dark' : 'light') : adminThemePreference;
}
applyAdminTheme(adminThemePreference);
adminThemeMedia.addEventListener('change', () => applyAdminTheme(adminThemePreference));
