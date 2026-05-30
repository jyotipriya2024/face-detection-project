"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, UserPlus, Video, Search,
  BarChart2, ClipboardList, Users, ChevronRight,
  Shield, Building2, LogOut, Settings,
} from "lucide-react";
import { useState } from "react";

const MAIN_NAV = [
  { href: "/",          label: "Dashboard",          icon: LayoutDashboard, badge: null },
  { href: "/live",      label: "Live Detection",      icon: Video,           badge: "LIVE" },
  { href: "/register",  label: "Register Employee",   icon: UserPlus,        badge: null },
  { href: "/search",    label: "Face Search",         icon: Search,          badge: null },
];

const SYSTEM_NAV = [
  { href: "/analytics", label: "Analytics",           icon: BarChart2,       badge: null },
  { href: "/logs",      label: "Attendance Logs",     icon: ClipboardList,   badge: null },
  { href: "/registry",  label: "Employee Registry",   icon: Users,           badge: null },
];

const ADMIN_NAV = [
  { href: "/settings",  label: "Change Password",     icon: Settings,        badge: null },
];

function NavItem({ href, label, icon: Icon, badge, active }:
  { href:string; label:string; icon:React.ElementType; badge:string|null; active:boolean }) {
  return (
    <Link href={href} className={cn(
      "flex items-center gap-2.5 px-3 py-2 rounded-lg text-[0.82rem] font-medium transition-all duration-150",
      "border-l-2",
      active
        ? "bg-[rgba(0,200,255,0.10)] text-[#40d4ff] border-l-[#00c8ff]"
        : "text-[#5a7a92] border-l-transparent hover:bg-white/[0.05] hover:text-[#b0d0e8] hover:border-l-[rgba(0,200,255,0.30)]"
    )}>
      <Icon size={15} className="shrink-0" />
      <span className="flex-1 truncate">{label}</span>
      {badge && (
        <span className={cn(
          "text-[0.52rem] font-bold px-1.5 py-0.5 rounded tracking-wide",
          badge === "LIVE"
            ? "bg-[rgba(255,77,109,0.18)] text-[#ff4d6d] border border-[rgba(255,77,109,0.35)]"
            : "bg-[rgba(0,200,255,0.12)] text-[#00c8ff] border border-[rgba(0,200,255,0.28)]"
        )}>{badge}</span>
      )}
      {active && <ChevronRight size={11} className="text-[#00c8ff] shrink-0" />}
    </Link>
  );
}

export default function Sidebar() {
  const pathname    = usePathname();
  const router      = useRouter();
  const [loggingOut,setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  };

  return (
    <aside className="fixed left-0 top-0 h-full flex flex-col z-40"
           style={{ width:"var(--sidebar-width,220px)", background:"#0b1220", borderRight:"1px solid rgba(255,255,255,0.07)" }}>

      {/* Logo */}
      <div className="px-4 py-4 border-b border-white/[0.07]">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
               style={{ background:"linear-gradient(135deg,#00c8ff,#7b61ff)" }}>
            <Shield size={16} className="text-white" />
          </div>
          <div>
            <div className="text-[0.76rem] font-black tracking-widest text-[#e0eeff]"
                 style={{ fontFamily:"Orbitron,sans-serif" }}>FACE ID</div>
            <div className="text-[0.54rem] tracking-widest text-[#2a4a60] uppercase">Enterprise</div>
          </div>
        </div>
        <div className="flex items-center gap-1.5 mt-2 px-2 py-1 rounded-md" style={{background:"rgba(0,230,118,0.07)",border:"1px solid rgba(0,230,118,0.18)"}}>
          <span className="w-1.5 h-1.5 rounded-full bg-[#00e676] live-dot shrink-0"/>
          <span className="text-[0.60rem] font-semibold text-[#00e676] tracking-widest">SYSTEM ONLINE</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3">
        <p className="px-4 pt-1 pb-1.5 text-[0.56rem] font-bold tracking-[0.18em] uppercase text-[#1e3a50]">Main</p>
        <div className="px-2 space-y-0.5">
          {MAIN_NAV.map(item => <NavItem key={item.href} {...item} active={pathname===item.href} />)}
        </div>

        <div className="mx-3 my-3 border-t border-white/[0.06]" />

        <p className="px-4 pb-1.5 text-[0.56rem] font-bold tracking-[0.18em] uppercase text-[#1e3a50]">Reports</p>
        <div className="px-2 space-y-0.5">
          {SYSTEM_NAV.map(item => <NavItem key={item.href} {...item} active={pathname===item.href} />)}
        </div>

        <div className="mx-3 my-3 border-t border-white/[0.06]" />

        <p className="px-4 pb-1.5 text-[0.56rem] font-bold tracking-[0.18em] uppercase text-[#1e3a50]">Admin</p>
        <div className="px-2 space-y-0.5">
          {ADMIN_NAV.map(item => <NavItem key={item.href} {...item} active={pathname===item.href} />)}
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t border-white/[0.07] px-3 py-3 space-y-2">
        {/* Admin badge */}
        <div className="flex items-center gap-2 px-2 py-1.5 rounded-lg"
             style={{ background:"rgba(0,200,255,0.06)", border:"1px solid rgba(0,200,255,0.12)" }}>
          <div className="w-6 h-6 rounded-full flex items-center justify-center text-[0.58rem] font-black text-white shrink-0"
               style={{ background:"linear-gradient(135deg,#00c8ff,#7b61ff)" }}>A</div>
          <div className="flex-1 min-w-0">
            <p className="text-[0.70rem] font-bold text-[#8ab0cc] truncate">Administrator</p>
            <p className="text-[0.58rem] text-[#2a4a60]">Full Access</p>
          </div>
          <Shield size={10} className="text-[#2a5570] shrink-0" />
        </div>

        {/* Logout button */}
        <button
          onClick={handleLogout}
          disabled={loggingOut}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-[0.78rem] font-semibold transition-all duration-150 disabled:opacity-50"
          style={{ color:"#ff4d6d", background:"rgba(255,77,109,0.06)", border:"1px solid rgba(255,77,109,0.18)" }}
          onMouseEnter={e=>(e.currentTarget.style.background="rgba(255,77,109,0.14)")}
          onMouseLeave={e=>(e.currentTarget.style.background="rgba(255,77,109,0.06)")}
        >
          <LogOut size={13} className="shrink-0" />
          {loggingOut ? "Signing out…" : "Sign Out"}
        </button>

        {/* Project info */}
        <div className="flex items-center gap-1.5 px-1">
          <Building2 size={9} className="text-[#1a3040]" />
          <span className="text-[0.56rem] text-[#1a3040]">Jyotipriya Panda · GIFT Bhubaneswar · 2024–26</span>
        </div>
      </div>
    </aside>
  );
}
