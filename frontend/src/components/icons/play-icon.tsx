type PlayIconProps = { readonly size: number };

export function PlayIcon({ size }: PlayIconProps) {
  return (
    <svg
      aria-hidden="true"
      fill="currentColor"
      height={size}
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      viewBox="0 0 24 24"
      width={size}
    >
      <path d="M8 5l11 7-11 7z" />
    </svg>
  );
}
