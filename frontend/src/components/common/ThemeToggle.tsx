import { Moon, Sun } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useUiStore } from "@/stores/uiStore";

/** Toggles between light and dark themes. */
export function ThemeToggle() {
  const theme = useUiStore((s) => s.theme);
  const toggleTheme = useUiStore((s) => s.toggleTheme);

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleTheme}
      aria-label="Toggle theme"
    >
      {theme === "dark" ? <Sun /> : <Moon />}
    </Button>
  );
}
