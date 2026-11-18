import { TYPE_SCALE } from "./tokens";

const BASE_FONT_SIZE = 16;

/** Sizes are in rem so they follow the browser's font size. */
export function textStyle(name: keyof typeof TYPE_SCALE) {
  const { fontSize, fontWeight, lineHeight } = TYPE_SCALE[name];

  return { fontSize: `${fontSize / BASE_FONT_SIZE}rem`, fontWeight, lineHeight };
}
