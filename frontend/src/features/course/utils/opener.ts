/** What a row does when it opens its item in place, or nothing when it goes to the item's page. */
export function opener(onOpenItem: ((itemId: string) => void) | undefined, itemId: string): (() => void) | undefined {
  return onOpenItem === undefined
    ? undefined
    : () => {
        onOpenItem(itemId);
      };
}
