import { Icon } from "./icon";

type SearchIconProps = { readonly size: number };

export function SearchIcon({ size }: SearchIconProps) {
  return (
    <Icon size={size}>
      <circle cx="11" cy="11" r="6.5" />
      <path d="M16 16l4.5 4.5" />
    </Icon>
  );
}
