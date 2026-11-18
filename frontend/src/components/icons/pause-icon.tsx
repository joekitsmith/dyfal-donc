import { Icon } from "./icon";

type PauseIconProps = { readonly size: number };

export function PauseIcon({ size }: PauseIconProps) {
  return (
    <Icon size={size}>
      <path d="M9 5v14M15 5v14" />
    </Icon>
  );
}
