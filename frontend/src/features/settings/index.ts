"use client";

// A client module, so the pages that import this feature on the server get components and not hooks
export { useSettings } from "./api/use-settings";
export { SettingsPage } from "./settings-page";
