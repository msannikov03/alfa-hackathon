import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import QueryProvider from "@/components/QueryProvider";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Alfa Intelligence",
  description: "Your autonomous business co-pilot.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body className={`${inter.variable} font-sans antialiased bg-gray-900 text-gray-100`}>
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}
