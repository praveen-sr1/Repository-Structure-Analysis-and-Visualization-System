import { Toaster } from "sonner";

import { Dashboard } from "@/pages/Dashboard";
import { useUiStore } from "@/stores/uiStore";

export default function App() {
  const theme = useUiStore((s) => s.theme);

  return (
    <>
      <Dashboard />
      <Toaster theme={theme} position="bottom-right" richColors closeButton />
    </>
  );
}
