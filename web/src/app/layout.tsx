import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import AppShell from "@/components/AppShell";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "AI Vision — Face Recognition System",
  description: "Real-time face recognition · M.Tech CSE Research · GIFT Bhubaneswar",
  appleWebApp: { capable: true, statusBarStyle: "black-translucent", title: "AI Vision" },
};

export const viewport: Viewport = {
  themeColor: "#040810",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen" style={{ background: "#040810" }}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
