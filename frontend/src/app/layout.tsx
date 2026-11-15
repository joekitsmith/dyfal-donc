import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AppRouterCacheProvider } from "@mui/material-nextjs/v16-appRouter";

import { Provider } from "./provider";

export const metadata: Metadata = { title: "Dyfal donc" };

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
