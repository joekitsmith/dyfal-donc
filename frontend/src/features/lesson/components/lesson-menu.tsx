import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";
import { useState } from "react";

import { MenuIcon } from "@/components/icons/menu-icon";
import { Sheet } from "@/components/sheet";
import { ROUTES } from "@/config/paths";
import { textStyle } from "@/theme/text-style";

import { MenuRow } from "./menu-row";

type LessonMenuProps = {
  readonly menu: { readonly isOpen: boolean; readonly onClose: () => void; readonly onOpen: () => void };
  readonly onReport: () => void;
  /** Only while a lesson is running, since only then is there something to stop. */
  readonly onStop?: () => void;
};

const BUTTON_SIZE = 48;

/** The menu button for the header, and the sheet it opens. */
export function LessonMenu({ menu, onReport, onStop }: LessonMenuProps) {
  const [button, setButton] = useState<HTMLElement | null>(null);

  return (
    <>
      <ButtonBase
        aria-expanded={menu.isOpen}
        aria-haspopup="dialog"
        aria-label="Menu"
        onClick={menu.onOpen}
        ref={setButton}
        sx={{ height: BUTTON_SIZE, width: BUTTON_SIZE }}
      >
        <MenuIcon size={24} />
      </ButtonBase>
      <Sheet anchor={button} label="Menu" onClose={menu.onClose} open={menu.isOpen}>
        <MenuRow href={ROUTES.course}>Look something up</MenuRow>
        <MenuRow
          onClick={() => {
            menu.onClose();
            onReport();
          }}
        >
          Report a problem
        </MenuRow>
        <MenuRow href={ROUTES.settings}>Settings</MenuRow>
        <MenuRow href={ROUTES.account}>Account</MenuRow>
        {onStop === undefined ? null : (
          <MenuRow
            chevron={false}
            onClick={() => {
              menu.onClose();
              onStop();
            }}
          >
            Stop for now
          </MenuRow>
        )}
        <Box
          sx={{
            ...textStyle("hint"),
            backgroundColor: "var(--dd-ground)",
            borderRadius: "10px",
            mt: "8px",
            p: "12px 14px",
          }}
        >
          On headphones and the lock screen: play and pause hold the lesson, back replays the sentence, forward marks
          Missed it.
        </Box>
      </Sheet>
    </>
  );
}
