import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Telegram Web App",
  description: "Alfa Business Assistant - Telegram Web App",
};

export default function TelegramAppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
