import type { ReactNode } from "react";

type IconProps = {
  readonly children: ReactNode;
  /** Solid shapes are filled as well as stroked, so their corners stay rounded. */
  readonly filled?: boolean;
  readonly size: number;
  /** Without an outline, for shapes drawn as plain areas. */
  readonly stroked?: boolean;
};

/** The shared frame of the icons: a 24 unit grid drawn with a round 2 unit stroke in the text colour. */
export function Icon({ children, filled = false, size, stroked = true }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      fill={filled ? "currentColor" : "none"}
      height={size}
      stroke={stroked ? "currentColor" : "none"}
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      viewBox="0 0 24 24"
      width={size}
    >
      {children}
    </svg>
  );
}
