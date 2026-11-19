import { Icon } from "./icon";

type CloseIconProps = { readonly size: number };

export function CloseIcon({ size }: CloseIconProps) {
  return (
    <Icon size={size}>
      <path d="M6 6l12 12M18 6L6 18" />
    </Icon>
  );
}
