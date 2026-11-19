import ButtonBase from "@mui/material/ButtonBase";

import { PauseIcon } from "@/components/icons/pause-icon";
import { PlayIcon } from "@/components/icons/play-icon";

import type { ReportSubject } from "../types";

type PlaySubjectButtonProps = {
  readonly onPlay: (path: string) => void;
  /** Whether this subject's clip is the one playing. */
  readonly playing: boolean;
  readonly subject: ReportSubject;
};

const BUTTON_SIZE = 48;

/** Plays the subject's Welsh. It shows nothing for a subject with no audio. */
export function PlaySubjectButton({ onPlay, playing, subject }: PlaySubjectButtonProps) {
  const { audio } = subject;

  if (audio === null) {
    return null;
  }

  return (
    <ButtonBase
      aria-label={subject.kind === "sentence" ? "Play this sentence" : "Play this word"}
      onClick={() => {
        onPlay(audio);
      }}
      sx={{ flexShrink: 0, height: BUTTON_SIZE, width: BUTTON_SIZE }}
    >
      {playing ? <PauseIcon size={16} /> : <PlayIcon size={16} />}
    </ButtonBase>
  );
}
