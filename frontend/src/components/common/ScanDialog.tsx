import { useState } from "react";
import { FolderSearch } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { useScanRepository } from "@/hooks/useRepositories";
import { useUiStore } from "@/stores/uiStore";

interface ScanDialogProps {
  open: boolean;
  onClose: () => void;
}

/** Dialog for scanning a new repository by absolute path. */
export function ScanDialog({ open, onClose }: ScanDialogProps) {
  const [path, setPath] = useState("");
  const [name, setName] = useState("");
  const scan = useScanRepository();
  const setActiveRepository = useUiStore((s) => s.setActiveRepository);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!path.trim()) return;
    scan.mutate(
      { path: path.trim(), name: name.trim() || undefined },
      {
        onSuccess: (data) => {
          setActiveRepository(data.repository.id);
          setPath("");
          setName("");
          onClose();
        },
      },
    );
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Scan a repository"
      description="Provide the absolute path to a local repository on this machine."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-sm font-medium" htmlFor="repo-path">
            Repository path
          </label>
          <Input
            id="repo-path"
            placeholder="/home/user/projects/my-repo"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            autoFocus
          />
        </div>
        <div className="space-y-1.5">
          <label className="text-sm font-medium" htmlFor="repo-name">
            Display name <span className="text-muted-foreground">(optional)</span>
          </label>
          <Input
            id="repo-name"
            placeholder="my-repo"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={scan.isPending || !path.trim()}>
            <FolderSearch />
            {scan.isPending ? "Scanning…" : "Scan repository"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
