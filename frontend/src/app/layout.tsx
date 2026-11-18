import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import "@fontsource-variable/geologica";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v16-appRouter";

import { Provider } from "./provider";

export const metadata: Metadata = {
  icons: {
    apple: [{ sizes: "180x180", type: "image/png", url: "/icons/apple-touch-icon.png" }],
    icon: [
      { type: "image/svg+xml", url: "/icons/icon.svg" },
      { sizes: "32x32", type: "image/png", url: "/icons/favicon-32.png" },
    ],
  },
  title: "dyfal-donc",
};

// Lets the layout use the safe areas of a phone with a notch or a home bar
export const viewport: Viewport = { viewportFit: "cover" };

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
