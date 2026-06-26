/**
 * UI state store (Zustand).
 *
 * Holds purely client-side UI concerns: the active repository, the selected
 * file node, theme, and panel/sidebar visibility. Server data lives in React
 * Query, not here.
 */
import { create } from "zustand";

type Theme = "light" | "dark";

interface UiState {
  activeRepositoryId: number | null;
  selectedNodeId: string | null;
  searchQuery: string;
  sidebarOpen: boolean;
  theme: Theme;

  setActiveRepository: (id: number | null) => void;
  selectNode: (id: string | null) => void;
  setSearchQuery: (q: string) => void;
  toggleSidebar: () => void;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.classList.toggle("dark", theme === "dark");
}

export const useUiStore = create<UiState>((set, get) => ({
  activeRepositoryId: null,
  selectedNodeId: null,
  searchQuery: "",
  sidebarOpen: true,
  theme: "dark",

  setActiveRepository: (id) =>
    set({ activeRepositoryId: id, selectedNodeId: null }),
  selectNode: (id) => set({ selectedNodeId: id }),
  setSearchQuery: (q) => set({ searchQuery: q }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setTheme: (theme) => {
    applyTheme(theme);
    set({ theme });
  },
  toggleTheme: () => {
    const next: Theme = get().theme === "dark" ? "light" : "dark";
    applyTheme(next);
    set({ theme: next });
  },
}));
