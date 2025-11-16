import type { Metadata } from "next";
import Script from "next/script";

export const metadata: Metadata = {
  title: "Telegram Web App",
  description: "Alfa Business Assistant - Telegram Web App",
};

export default function TelegramAppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Script
        src="https://telegram.org/js/telegram-web-app.js"
        strategy="beforeInteractive"
      />
      {children}
    </>
  );
}
