import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AppRouterCacheProvider } from "@mui/material-nextjs/v16-appRouter";

import { Provider } from "./provider";

// The placeholder mark, also shown on the lock screen. The design pass replaces it
export const metadata: Metadata = {
  icons: { apple: "/icons/icon-192.png", icon: [{ sizes: "192x192", type: "image/png", url: "/icons/icon-192.png" }] },
  title: "Dyfal donc",
};

export default function RootLayout({ children }: { readonly children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppRouterCacheProvider>
          <Provider>{children}</Provider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
