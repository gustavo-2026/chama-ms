import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Chama - Community Treasury",
  description: "Manage your chama treasury, contributions, and loans",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
