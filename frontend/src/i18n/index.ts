import zh from './zh';
import en from './en';
import vi from './vi';
import ms from './ms';

const locales: Record<string, Record<string, string>> = { zh, en, vi, ms };

let currentLocale = 'en';

export function setLocale(locale: string) {
  currentLocale = locale;
}

export function getLocale() {
  return currentLocale;
}

export function t(key: string, vars?: Record<string, string | number>): string {
  let val = locales[currentLocale]?.[key] ?? locales['en']?.[key] ?? key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      val = val.replace(`{${k}}`, String(v));
    }
  }
  return val;
}

export function localeIsZh(): boolean {
  return currentLocale === 'zh';
}

export function localeIs(locale: string): boolean {
  return currentLocale === locale;
}
