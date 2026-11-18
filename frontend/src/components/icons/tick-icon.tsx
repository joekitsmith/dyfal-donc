import { Icon } from "./icon";

type TickIconProps = { readonly size: number };

export function TickIcon({ size }: TickIconProps) {
  return (
    <Icon size={size}>
      <path d="M5 12.5l4.5 4.5L19 7" />
    </Icon>
  );
}
