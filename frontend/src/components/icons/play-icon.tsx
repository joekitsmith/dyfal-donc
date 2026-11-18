import { Icon } from "./icon";

type PlayIconProps = { readonly size: number };

export function PlayIcon({ size }: PlayIconProps) {
  return (
    <Icon filled size={size}>
      <path d="M8 5l11 7-11 7z" />
    </Icon>
  );
}
