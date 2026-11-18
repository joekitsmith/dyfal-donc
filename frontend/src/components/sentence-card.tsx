import type { ReactNode } from "react";

import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";

import { textStyle } from "@/theme/text-style";

import { PauseIcon } from "./icons/pause-icon";
import { PlayIcon } from "./icons/play-icon";

export type ClipSpeed = "slow" | "standard";

type SentenceCardProps = {
  /** The clip that did not play, if one has failed lately. */
  readonly failedClip: ClipSpeed | null;
  readonly onPlay: (speed: ClipSpeed) => void;
  /** Gives the card a Report button. */
  readonly onReport?: (() => void) | undefined;
  /** The clip that is playing. */
  readonly playing: ClipSpeed | null;
  readonly sentence: { readonly english: string; readonly welsh: string };
};

const ACTION_HEIGHT = 48;

/** A sentence in both languages, with its Welsh to play at either pace. */
export function SentenceCard({ failedClip, onPlay, onReport, playing, sentence }: SentenceCardProps) {
  const { english, welsh } = sentence;

  return (
    <Box sx={{ backgroundColor: "var(--dd-surface)", borderRadius: "10px", p: "14px 16px 4px" }}>
      <Box lang="cy" sx={{ ...textStyle("label"), fontWeight: 600 }}>
        {welsh}
      </Box>
      <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)", mt: "2px" }}>{english}</Box>
      {failedClip === null ? null : (
        <Box role="status" sx={{ ...textStyle("hint"), color: "var(--dd-muted)", mt: "4px" }}>
          That couldn&apos;t be played. Try again.
        </Box>
      )}
      <Box sx={{ alignItems: "center", display: "flex", gap: "20px" }}>
        <ActionButton
          label={`Play ${welsh}`}
          onClick={() => {
            onPlay("standard");
          }}
        >
          {playing === "standard" ? <PauseIcon size={16} /> : <PlayIcon size={16} />}
          Play
        </ActionButton>
        <ActionButton
          label={`Play ${welsh} slowly`}
          onClick={() => {
            onPlay("slow");
          }}
        >
          {playing === "slow" ? <PauseIcon size={16} /> : <PlayIcon size={16} />}
          Slowly
        </ActionButton>
        {onReport === undefined ? null : (
          <ActionButton label={`Report ${welsh}`} muted onClick={onReport}>
            Report
          </ActionButton>
        )}
      </Box>
    </Box>
  );
}

function ActionButton({
  children,
  label,
  muted = false,
  onClick,
}: {
  readonly children: ReactNode;
  readonly label: string;
  /** The last action sits at the right, quieter than the rest. */
  readonly muted?: boolean;
  readonly onClick: () => void;
}) {
  return (
    <ButtonBase
      aria-label={label}
      onClick={onClick}
      sx={{
        ...textStyle("body"),
        alignItems: "center",
        color: muted ? "var(--dd-muted)" : "var(--dd-ink)",
        display: "flex",
        fontWeight: muted ? 400 : 500,
        gap: "6px",
        height: ACTION_HEIGHT,
        ml: muted ? "auto" : 0,
      }}
    >
      {children}
    </ButtonBase>
  );
}
