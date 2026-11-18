import { Icon } from "./icon";

type ChevronIconProps = {
  readonly direction: "down" | "left" | "right";
  readonly size: number;
};

const ROTATIONS = { down: 90, left: 180, right: 0 } as const;

export function ChevronIcon({ direction, size }: ChevronIconProps) {
  return (
    <Icon size={size}>
      <path d="M9 5l7 7-7 7" transform={`rotate(${ROTATIONS[direction]} 12 12)`} />
    </Icon>
  );
}
