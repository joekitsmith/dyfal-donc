"use client";

import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { fetchClip } from "@/api/clips";

export function ClipButton({ label, path }: { readonly label: string; readonly path: string }) {
  const [status, setStatus] = useState("");

  async function play() {
    try {
      const clip = await fetchClip(path);
      const url = URL.createObjectURL(clip.blob);
      const audio = new Audio(url);

      console.info(`${label}: ${clip.milliseconds.toFixed(0)} ms to fetch`);
      setStatus(`${clip.milliseconds.toFixed(0)} ms`);
      audio.addEventListener("ended", () => {
        URL.revokeObjectURL(url);
      });
      await audio.play();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not play");
    }
  }

  return (
    <>
      <Button onClick={() => void play()} variant="outlined">
        {label}
      </Button>
      <Typography aria-live="polite" variant="caption">
        {status}
      </Typography>
    </>
  );
}
