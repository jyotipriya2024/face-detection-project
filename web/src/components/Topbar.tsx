"use client";
import { Bell, Cpu, Shield } from "lucide-react";

export default function Topbar({ title, subtitle }: { title:string; subtitle?:string }) {
  const now = new Date().toLocaleDateString("en-IN",{weekday:"short",month:"short",day:"numeric",year:"numeric"});
  return (
    <header className="fixed right-0 top-0 z-30 flex items-center justify-between px-6"
            style={{
              left:"var(--sidebar-width,220px)",
              height:"var(--topbar-height,52px)",
              background:"rgba(7,12,24,0.90)",
              backdropFilter:"blur(12px)",
              borderBottom:"1px solid rgba(255,255,255,0.06)",
            }}>
      <div>
        <h1 className="text-[0.86rem] font-bold text-[#c8e8ff] leading-none">{title}</h1>
        {subtitle && <p className="text-[0.60rem] text-[#2e4a60] mt-0.5 tracking-wider">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-2.5">
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[0.62rem] font-semibold"
             style={{background:"rgba(0,200,255,0.07)",border:"1px solid rgba(0,200,255,0.18)",color:"#3a7a9a"}}>
          <Cpu size={10}/><span>LBP+HOG · 416-d</span>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[0.62rem] font-semibold"
             style={{background:"rgba(0,230,118,0.07)",border:"1px solid rgba(0,230,118,0.20)",color:"#00a854"}}>
          <Shield size={10}/><span>Secure</span>
        </div>
        <div className="hidden sm:block text-[0.60rem] text-[#1e3a50] font-medium">{now}</div>
        <button className="p-1.5 rounded-lg text-[#2a4a60] hover:text-[#00c8ff] hover:bg-white/5 transition-colors">
          <Bell size={15}/>
        </button>
      </div>
    </header>
  );
}
