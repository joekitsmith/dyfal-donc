import { Icon } from "./icon";

type MenuIconProps = { readonly size: number };

export function MenuIcon({ size }: MenuIconProps) {
  return (
    <Icon filled size={size} stroked={false}>
      <circle cx="5" cy="12" r="1.6" />
      <circle cx="12" cy="12" r="1.6" />
      <circle cx="19" cy="12" r="1.6" />
    </Icon>
  );
}
