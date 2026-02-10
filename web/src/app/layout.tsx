import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Japan Explorer - Tev & Louis Places",
  description:
    "Interactive map and data dashboard of places recommended by Tev & Louis from their Japan travel videos.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
