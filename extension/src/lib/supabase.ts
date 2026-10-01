import { createClient } from '@supabase/supabase-js';

// Essas chaves devem vir do seu painel do Supabase
// Não tem problema essas chaves ficarem expostas na extensão (elas são públicas por design)
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://sua-url.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'sua-chave-anon-aqui';

// Adaptador de storage para funcionar no Chrome Extension (Service Worker e UI)
const chromeStorage = {
  getItem: (key: string): Promise<string | null> => {
    return new Promise((resolve) => {
      if (typeof chrome !== 'undefined' && chrome.storage?.local) {
        chrome.storage.local.get([key], (result) => {
          resolve((result[key] as string) || null);
        });
      } else if (typeof localStorage !== 'undefined') {
        resolve(localStorage.getItem(key));
      } else {
        resolve(null);
      }
    });
  },
  setItem: (key: string, value: string): Promise<void> => {
    return new Promise((resolve) => {
      if (typeof chrome !== 'undefined' && chrome.storage?.local) {
        chrome.storage.local.set({ [key]: value }, () => resolve());
      } else if (typeof localStorage !== 'undefined') {
        localStorage.setItem(key, value);
        resolve();
      } else {
        resolve();
      }
    });
  },
  removeItem: (key: string): Promise<void> => {
    return new Promise((resolve) => {
      if (typeof chrome !== 'undefined' && chrome.storage?.local) {
        chrome.storage.local.remove([key], () => resolve());
      } else if (typeof localStorage !== 'undefined') {
        localStorage.removeItem(key);
        resolve();
      } else {
        resolve();
      }
    });
  },
};

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: chromeStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});
