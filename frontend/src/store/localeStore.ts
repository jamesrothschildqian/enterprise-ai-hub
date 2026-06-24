import { create } from 'zustand';
import { setLocale, getLocale, t, localeIsZh } from '../i18n';

const LOCALE_ORDER = ['zh', 'en', 'vi', 'ms'];

interface LocaleState {
  locale: string;
  t: (key: string, vars?: Record<string, string | number>) => string;
  isZh: () => boolean;
  toggle: () => void;
  setLang: (lang: string) => void;
}

export const useLocaleStore = create<LocaleState>((set) => ({
  locale: getLocale(),
  t,
  isZh: localeIsZh,
  toggle: () => {
    const cur = getLocale();
    const idx = LOCALE_ORDER.indexOf(cur);
    const next = LOCALE_ORDER[(idx + 1) % LOCALE_ORDER.length];
    setLocale(next);
    set({ locale: next });
  },
  setLang: (lang: string) => {
    if (['zh', 'en', 'vi', 'ms'].includes(lang)) {
      setLocale(lang);
      set({ locale: lang });
    }
  },
}));
