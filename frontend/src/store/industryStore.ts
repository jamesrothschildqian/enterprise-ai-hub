import { create } from 'zustand';
import { getIndustries, switchIndustry, getIndustryData } from '../services/api';

interface Industry {
  id: string;
  name: string;
  name_en: string;
  icon: string;
  description: string;
}

interface IndustryState {
  industries: Industry[];
  currentId: string;
  currentData: any;
  loading: boolean;
  init: () => Promise<void>;
  switchTo: (id: string) => Promise<void>;
}

export const useIndustryStore = create<IndustryState>((set, get) => ({
  industries: [],
  currentId: 'international_trade',
  currentData: null,
  loading: false,

  init: async () => {
    set({ loading: true });
    try {
      const res = await getIndustries();
      set({ industries: res.industries });
      const data = await getIndustryData(get().currentId);
      set({ currentData: data, loading: false });
    } catch {
      set({ loading: false });
    }
  },

  switchTo: async (id: string) => {
    set({ loading: true, currentId: id });
    try {
      await switchIndustry(id);
      const data = await getIndustryData(id);
      set({ currentData: data, loading: false });
    } catch {
      set({ loading: false });
    }
  },
}));
