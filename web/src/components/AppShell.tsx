"use client";
import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLogin  = pathname === "/login";

  if (isLogin) {
    // Login page — no sidebar, no topbar, full screen
    return <>{children}</>;
  }

  return (
    <>
      <Sidebar />
      <main
        style={{
          marginLeft: "var(--sidebar-width, 220px)",
          paddingTop: "var(--topbar-height, 52px)",
          minHeight:  "100vh",
        }}
      >
        {children}
      </main>
    </>
  );
}
