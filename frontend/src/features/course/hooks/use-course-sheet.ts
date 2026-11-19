import { useState } from "react";

/**
 * The course as a sheet over something else, such as a lesson that is paused behind it. There are
 * no pages to go to in a sheet, so it keeps which word or phrase is open, and going back from one
 * returns to the list.
 */
export function useCourseSheet() {
  const [isOpen, setIsOpen] = useState(false);
  const [item, setItem] = useState<null | string>(null);

  return {
    close: () => {
      setIsOpen(false);
      setItem(null);
    },
    isOpen,
    item: {
      close: () => {
        setItem(null);
      },
      id: item,
      open: (itemId: string) => {
        setItem(itemId);
      },
    },
    open: () => {
      setIsOpen(true);
    },
  };
}
