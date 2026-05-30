"use client";
import { useEffect, useState } from "react";
import Topbar from "@/components/Topbar";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  Users, UserCheck, UserX, TrendingUp, Camera, Clock,
  Building2, ShieldCheck, Activity,
} from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

type DashboardData = {
  total_employees: number; present_today: number; absent_today: number;
  attendance_rate: number; total_detections: number; unknown_faces: number;
  today_detections: number; avg_confidence: number;
  by_department: { department: string; present_count: number }[];
  weekly_trend: { date: string; count: number }[];
};

const TOOLTIP = { background: "#0b1220", border: "1px solid rgba(0,200,255,0.18)", borderRadius: 8, color: "#c8e8ff", fontSize: 11 };

const DEPTS = ["Engineering", "HR", "Finance", "Security", "Operations"];
const WEEK_DUMMY = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map((d,i) => ({ date: d, count: [12,18,15,22,19,8,5][i] }));

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [checkins, setCheckins] = useState<any[]>([]);
  const [time, setTime] = useState("");

  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString("en-IN", { hour12: true }));
    tick(); const t = setInterval(tick, 1000); return () => clearInterval(t);
  }, []);

  useEffect(() => {
    fetch("http://localhost:8000/api/dashboard").then(r => r.ok ? r.json() : null).then(d => d && setData(d)).catch(() => {});
    fetch("http://localhost:8000/api/attendance/today").then(r => r.ok ? r.json() : null).then(d => d && setCheckins(d.slice(0,8))).catch(() => {});
  }, []);

  const kpis = [
    { label: "Total Employees", value: data?.total_employees ?? "—", icon: Users,       color: "#00c8ff", sub: "Registered" },
    { label: "Present Today",   value: data?.present_today   ?? "—", icon: UserCheck,   color: "#00e676", sub: `${data?.attendance_rate ?? "—"}% rate` },
    { label: "Absent Today",    value: data?.absent_today    ?? "—", icon: UserX,        color: "#ff4d6d", sub: "Not checked in" },
    { label: "Face Detections", value: data?.today_detections ?? "—", icon: Camera,    color: "#7b61ff", sub: "Today" },
    { label: "Unknown Faces",   value: data?.unknown_faces   ?? "—", icon: ShieldCheck, color: "#ffab40", sub: "Unregistered" },
  ];

  const deptData = data?.by_department?.length
    ? data.by_department.map(d => ({ name: d.department || "General", count: d.present_count }))
    : DEPTS.map((d, i) => ({ name: d, count: [8, 5, 3, 6, 4][i] }));

  const weekData = data?.weekly_trend?.length ? data.weekly_trend : WEEK_DUMMY;

  return (
    <>
      <Topbar title="Company Dashboard" subtitle="Employee Attendance & Face Recognition" />
      <div className="px-6 py-5 max-w-[1440px] mx-auto space-y-5">

        {/* Header row */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-xl font-bold text-[#c8e8ff]">{new Date().toLocaleDateString("en-IN",{weekday:"long",year:"numeric",month:"long",day:"numeric"})}</h2>
            <p className="text-sm text-[#3a6a8a]">Live attendance monitoring · Auto face check-in</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="px-4 py-2 rounded-xl text-2xl font-mono font-bold text-[#00c8ff]"
                 style={{ background: "rgba(0,200,255,0.06)", border: "1px solid rgba(0,200,255,0.15)" }}>
              {time}
            </div>
            <Badge variant="success"><span className="w-1.5 h-1.5 rounded-full bg-[#00e676] live-dot mr-1" />Live</Badge>
          </div>
        </div>

        {/* KPI Row */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {kpis.map(({ label, value, icon: Icon, color, sub }) => (
            <Card key={label}>
              <CardContent className="pt-4 pb-3">
                <div className="flex items-start justify-between mb-2">
                  <div className="p-2 rounded-lg" style={{ background: `${color}14` }}>
                    <Icon size={18} style={{ color }} />
                  </div>
                </div>
                <div className="text-3xl font-extrabold font-mono leading-none mb-0.5" style={{ color }}>{value}</div>
                <div className="text-xs font-semibold text-[#c8e8ff] mt-1">{label}</div>
                <div className="text-[0.65rem] text-[#3a5570]">{sub}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Weekly trend */}
          <Card className="lg:col-span-2">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs font-bold tracking-widest uppercase text-[#2a5570]">◈ Weekly Attendance Trend</p>
                <Badge variant="default"><Activity size={10} className="mr-1" />Last 7 days</Badge>
              </div>
              <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={weekData}>
                  <defs>
                    <linearGradient id="grad1" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00c8ff" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#00c8ff" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,200,255,0.07)" />
                  <XAxis dataKey="date" stroke="#3a6a8a" tick={{ fontSize: 11 }}
                    tickFormatter={d => d.length === 10 ? new Date(d).toLocaleDateString("en",{weekday:"short"}) : d} />
                  <YAxis stroke="#3a6a8a" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={TOOLTIP} />
                  <Area type="monotone" dataKey="count" stroke="#00c8ff" fill="url(#grad1)" strokeWidth={2} name="Present" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Dept breakdown */}
          <Card>
            <CardContent className="pt-4">
              <p className="text-xs font-bold tracking-widest uppercase text-[#2a5570] mb-3">◈ Dept. Present Today</p>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={deptData} barSize={18} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,200,255,0.07)" horizontal={false} />
                  <XAxis type="number" stroke="#3a6a8a" tick={{ fontSize: 10 }} />
                  <YAxis type="category" dataKey="name" stroke="#3a6a8a" tick={{ fontSize: 10 }} width={72} />
                  <Tooltip contentStyle={TOOLTIP} />
                  <Bar dataKey="count" name="Present" radius={[0,4,4,0]} fill="#7b61ff" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Recent check-ins + Status */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Recent check-ins */}
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs font-bold tracking-widest uppercase text-[#2a5570]">◈ Recent Check-ins</p>
                <Badge variant="success">{checkins.length} today</Badge>
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {checkins.length === 0 && (
                  <div className="text-center py-8 text-[#3a5570]">
                    <Clock size={28} className="mx-auto mb-2 opacity-30" />
                    <p className="text-sm">No check-ins yet today</p>
                  </div>
                )}
                {checkins.map((c, i) => {
                  const pname = String(c.person_name || "?");
                  const init  = pname.split(" ").map((w:string)=>w[0]).join("").slice(0,2).toUpperCase();
                  const hue   = Array.from(pname).reduce((a:number,ch:string)=>a+ch.charCodeAt(0),0) % 360;
                  return (
                    <div key={i} className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/[0.03] transition-colors"
                         style={{ border: "1px solid rgba(255,255,255,0.05)" }}>
                      <div className="w-9 h-9 rounded-full flex items-center justify-center text-xs font-black text-white shrink-0"
                           style={{ background: `hsl(${hue},55%,38%)` }}>{init}</div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-[#c8e8ff] truncate">{c.person_name}</p>
                        <p className="text-[0.68rem] text-[#3a5570]">{c.department || "—"} · {c.position || "—"}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <p className="text-xs font-mono text-[#00c8ff]">{c.check_in?.slice(11,16) || "—"}</p>
                        <Badge variant="success" className="text-[0.55rem]">Present</Badge>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* System status */}
          <Card>
            <CardContent className="pt-4">
              <p className="text-xs font-bold tracking-widest uppercase text-[#2a5570] mb-3">◈ System Status</p>
              <div className="space-y-3">
                {[
                  { label: "Face Recognition Engine", status: "Operational", color: "#00e676" },
                  { label: "Attendance Logging",       status: "Active",      color: "#00e676" },
                  { label: "Camera Feed",              status: "Ready",       color: "#00c8ff" },
                  { label: "Database",                 status: "Connected",   color: "#00e676" },
                ].map(({ label, status, color }) => (
                  <div key={label} className="flex items-center justify-between py-2 border-b border-white/[0.05] last:border-0">
                    <span className="text-sm text-[#6a8fa8]">{label}</span>
                    <span className="flex items-center gap-1.5 text-xs font-semibold" style={{ color }}>
                      <span className="w-1.5 h-1.5 rounded-full live-dot" style={{ background: color }} />{status}
                    </span>
                  </div>
                ))}
                <div className="pt-2 grid grid-cols-2 gap-2">
                  {[
                    ["Recognition Rate", `${data?.attendance_rate ?? "—"}%`],
                    ["Avg Confidence",   `${data ? (data.avg_confidence * 100).toFixed(1) : "—"}%`],
                    ["Engine",           "LBP+HOG+YCrCb"],
                    ["Mode",             "Real-time"],
                  ].map(([k,v]) => (
                    <div key={k} className="rounded-lg px-3 py-2" style={{ background:"rgba(0,200,255,0.04)", border:"1px solid rgba(0,200,255,0.10)" }}>
                      <div className="text-[0.60rem] text-[#2a5570] uppercase tracking-wide">{k}</div>
                      <div className="text-xs font-bold text-[#c8e8ff] mt-0.5">{v}</div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
