"use client";

// A client module, so the pages that import this feature on the server get components and not hooks
export { HeadphoneHint } from "./components/headphone-hint";
export { HomeCards } from "./components/home-cards";
export { HomeLinks } from "./components/home-links";
export { useHeadphoneVisit } from "./hooks/use-headphone-visit";
export { useHome } from "./hooks/use-home";
export { recordUse as recordHeadphoneUse } from "./stores/headphone-hint-store";
