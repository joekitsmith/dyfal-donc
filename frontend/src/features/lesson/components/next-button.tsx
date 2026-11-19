import { Button } from "@/components/button";
import { ChevronIcon } from "@/components/icons/chevron-icon";

type NextButtonProps = { readonly onClick: () => void };

export function NextButton({ onClick }: NextButtonProps) {
  return (
    <Button edge keyHint="N" onClick={onClick} variant="ghost">
      Next
      <ChevronIcon direction="right" size={18} />
    </Button>
  );
}
