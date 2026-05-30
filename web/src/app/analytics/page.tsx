"use client";
import { useEffect, useState } from "react";
import Topbar from "@/components/Topbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";

const TT = { background:"#0b1220", border:"1px solid rgba(0,200,255,0.18)", borderRadius:8, color:"#c8e8ff", fontSize:11 };
const COLORS = ["#00c8ff","#7b61ff","#00e676","#ff4d6d","#ffab40","#a371f7"];

const DUMMY_WEEK  = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map((d,i)=>({day:d,present:[38,45,42,50,47,22,18][i],absent:[12,5,8,0,3,18,22][i]}));
const DUMMY_DEPT  = [{name:"Engineering",value:35},{name:"HR",value:12},{name:"Finance",value:8},{name:"Security",value:15},{name:"IT",value:10},{name:"Operations",value:20}];
const DUMMY_TIME  = [
  {range:"7-8 AM",count:4},{range:"8-9 AM",count:18},{range:"9-10 AM",count:32},
  {range:"10-11AM",count:12},{range:"11-12PM",count:6},{range:"12+ PM",count:3},
];
const DUMMY_TREND = Array.from({length:30},(_,i)=>({
  date: new Date(Date.now()-i*86400000).toLocaleDateString("en",{month:"short",day:"numeric"}),
  rate: Math.round(75+Math.random()*20),
})).reverse();

export default function AnalyticsPage() {
  const [stats, setStats] = useState({
    total_employees:50, present_today:42, absent_today:8, attendance_rate:84,
    by_department:[] as {department:string;present_count:number}[],
    weekly_trend:[] as {date:string;count:number}[],
  });

  useEffect(() => {
    fetch("http://localhost:8000/api/attendance/stats").then(r=>r.ok?r.json():null).then(d=>d&&setStats(d)).catch(()=>{});
  }, []);

  const deptPie = stats.by_department?.length
    ? stats.by_department.map(d=>({name:d.department||"Other",value:d.present_count}))
    : DUMMY_DEPT;

  return (
    <>
      <Topbar title="Analytics" subtitle="Attendance trends · department breakdown · timing analysis" />
      <div className="px-6 py-5 max-w-[1400px] mx-auto space-y-5">

        {/* KPI Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            {label:"Total Employees",   value:stats.total_employees,                color:"#00c8ff"},
            {label:"Present Today",     value:stats.present_today,                  color:"#00e676"},
            {label:"Absent Today",      value:stats.absent_today,                   color:"#ff4d6d"},
            {label:"Attendance Rate",   value:`${stats.attendance_rate}%`,          color:"#ffab40"},
          ].map(({label,value,color})=>(
            <Card key={label}>
              <CardContent className="pt-4 pb-3 text-center">
                <div className="text-3xl font-extrabold font-mono" style={{color}}>{value}</div>
                <div className="text-[0.65rem] text-[#4a7a9a] uppercase tracking-wide mt-1">{label}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* 30-day trend */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>30-Day Attendance Rate Trend</CardTitle>
              <Badge variant="default">Last 30 days</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={DUMMY_TREND}>
                <defs>
                  <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#00c8ff" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#00c8ff" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,200,255,0.07)"/>
                <XAxis dataKey="date" stroke="#3a6a8a" tick={{fontSize:9}} interval={4}/>
                <YAxis stroke="#3a6a8a" tick={{fontSize:10}} domain={[50,100]} unit="%"/>
                <Tooltip contentStyle={TT} formatter={(v)=>`${v ?? 0}%`}/>
                <Area type="monotone" dataKey="rate" stroke="#00c8ff" fill="url(#g1)" strokeWidth={2} name="Rate"/>
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Weekly pattern */}
          <Card>
            <CardHeader><CardTitle>Weekly Attendance Pattern</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={DUMMY_WEEK} barSize={18}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,200,255,0.07)"/>
                  <XAxis dataKey="day" stroke="#3a6a8a" tick={{fontSize:11}}/>
                  <YAxis stroke="#3a6a8a" tick={{fontSize:10}}/>
                  <Tooltip contentStyle={TT}/>
                  <Legend wrapperStyle={{fontSize:11,color:"#6a9ab0"}}/>
                  <Bar dataKey="present" name="Present" radius={[4,4,0,0]} fill="#00c8ff" stackId="a"/>
                  <Bar dataKey="absent"  name="Absent"  radius={[4,4,0,0]} fill="#ff4d6d" stackId="a"/>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Dept distribution */}
          <Card>
            <CardHeader><CardTitle>Department-wise Present Today</CardTitle></CardHeader>
            <CardContent className="flex items-center justify-center">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={deptPie} cx="50%" cy="50%" outerRadius={78} innerRadius={36}
                       dataKey="value" nameKey="name" paddingAngle={3}>
                    {deptPie.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                  </Pie>
                  <Tooltip contentStyle={TT}/>
                  <Legend wrapperStyle={{fontSize:11,color:"#6a9ab0"}}/>
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Check-in time distribution */}
          <Card>
            <CardHeader><CardTitle>Check-in Time Distribution</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={DUMMY_TIME} barSize={24}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,200,255,0.07)"/>
                  <XAxis dataKey="range" stroke="#3a6a8a" tick={{fontSize:10}}/>
                  <YAxis stroke="#3a6a8a" tick={{fontSize:10}}/>
                  <Tooltip contentStyle={TT}/>
                  <Bar dataKey="count" name="Employees" radius={[4,4,0,0]}>
                    {DUMMY_TIME.map((_,i)=>(
                      <Cell key={i} fill={i===2?"#00e676":i===1?"#00c8ff":"#7b61ff"}/>
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <p className="text-[0.65rem] text-center text-[#3a5570] mt-2">Peak: 9–10 AM · On-time window: 8:30–9:30 AM</p>
            </CardContent>
          </Card>

          {/* Dept attendance table */}
          <Card>
            <CardHeader><CardTitle>Department Attendance Summary</CardTitle></CardHeader>
            <CardContent className="p-0">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{borderBottom:"1px solid rgba(0,200,255,0.10)"}}>
                    {["Department","Present","Rate"].map(h=>(
                      <th key={h} className="text-left px-4 py-2.5 text-[0.62rem] font-bold uppercase tracking-wider text-[#2a5570]">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[
                    {dept:"Engineering", present:35, total:40},
                    {dept:"HR",          present:10, total:12},
                    {dept:"Finance",     present:7,  total:8},
                    {dept:"Security",    present:14, total:15},
                    {dept:"IT",          present:9,  total:10},
                    {dept:"Operations",  present:18, total:20},
                  ].map(row=>{
                    const rate = Math.round(row.present/row.total*100);
                    return (
                      <tr key={row.dept} className="border-b border-white/[0.04] hover:bg-white/[0.025]">
                        <td className="px-4 py-2.5 text-xs font-semibold text-[#c8e8ff]">{row.dept}</td>
                        <td className="px-4 py-2.5 text-xs text-[#8ab0cc]">{row.present}/{row.total}</td>
                        <td className="px-4 py-2.5">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 rounded-full overflow-hidden" style={{background:"rgba(255,255,255,0.07)"}}>
                              <div className="h-full rounded-full" style={{width:`${rate}%`,background:rate>=80?"#00e676":rate>=60?"#ffab40":"#ff4d6d"}}/>
                            </div>
                            <span className="text-[0.68rem] font-bold" style={{color:rate>=80?"#00e676":rate>=60?"#ffab40":"#ff4d6d"}}>{rate}%</span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
