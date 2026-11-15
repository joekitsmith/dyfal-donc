import { useState } from "react";

/** Whether something (a dialog, say) is open, with the two ways to change it. */
export function useDisclosure() {
  const [isOpen, setIsOpen] = useState(false);

  return {
    close: () => {
      setIsOpen(false);
    },
    isOpen,
    open: () => {
      setIsOpen(true);
    },
  };
}
