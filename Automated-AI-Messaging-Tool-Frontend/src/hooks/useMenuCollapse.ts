import { useEffect, Dispatch, SetStateAction } from 'react';

// types
import { NavItemType } from 'types/menu';

// Type alias for setting state
// Allows setting a state value or null
// Used for managing selected menu and anchor element

type SetState<T> = (value: T | null) => void;

// ==============================|| MENU COLLAPSED - RECURSIVE FUNCTION ||============================== //

/**
 * Recursively traverses menu items to find and open the correct parent menu.
 * If a menu item matches the current pathname, it marks the corresponding menu as selected and opens it.
 *
 * @param {NavItemType[]} items - List of menu items.
 * @param {string} pathname - Current route pathname.
 * @param {string | undefined} menuId - ID of the menu to be set as selected.
 * @param {SetState<string | null>} setSelected - Function to update the selected menu.
 * @param {Dispatch<SetStateAction<boolean>>} setOpen - Function to update the open state.
 */

function setParentOpenedMenu(
  items: NavItemType[],
  pathname: string,
  menuId: string | undefined,
  setSelected: SetState<string | null>,
  setOpen: Dispatch<SetStateAction<boolean>>
): void {
  for (const item of items) {
    // Recursively check child menus
    if (item.children?.length) {
      setParentOpenedMenu(item.children, pathname, menuId, setSelected, setOpen);
    }

    if (pathname && pathname.includes('product-details')) {
      if (item.url && item.url.includes('product-details')) {
        setSelected(menuId ?? null);
        setOpen(true);
      }
    }

    if (pathname && pathname.includes('invoice')) {
      if (item.url && item.url.includes('invoice')) {
        setSelected(menuId ?? null);
        setOpen(true);
      }
    }

    if (pathname && pathname.includes('profiles')) {
      if (item.url && item.url.includes('profiles')) {
        setSelected(menuId ?? null);
        setOpen(true);
      }
    }

    if (item.url === pathname) {
      setSelected(menuId ?? null);
      setOpen(true);
    }
  }
}

// ==============================|| MENU COLLAPSED - HOOK ||============================== //

/**
 * Hook to handle menu collapse behavior based on the current route.
 * Automatically expands the parent menu of the active route item.
 *
 * @param {NavItemType} menu - The menu object containing items.
 * @param {string} pathname - Current route pathname.
 * @param {boolean} miniMenuOpened - Flag indicating if the mini menu is open.
 * @param {SetState<string | null>} setSelected - Function to update selected menu state.
 * @param {Dispatch<SetStateAction<boolean>>} setOpen - Function to update menu open state.
 * @param {SetState<HTMLElement>} setAnchorEl - Function to update the anchor element state.
 */

export default function useMenuCollapse(
  menu: NavItemType,
  pathname: string,
  miniMenuOpened: boolean,
  setSelected: SetState<string | null>,
  setOpen: Dispatch<SetStateAction<boolean>>,
  setAnchorEl: SetState<HTMLElement>
): void {
  useEffect(() => {
    setOpen(false); // Close the menu initially

    // Reset selection based on menu state
    if (!miniMenuOpened) {
      setSelected(null);
    } else {
      setAnchorEl(null);
    }

    // If menu has children, determine which should be opened
    if (menu.children?.length) {
      setParentOpenedMenu(menu.children, pathname, menu.id, setSelected, setOpen);
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname, menu.children]);
}
