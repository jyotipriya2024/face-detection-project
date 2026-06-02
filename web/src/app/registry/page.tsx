"use client";
import { useEffect, useState } from "react";
import Topbar from "@/components/Topbar";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Search, Trash2, RefreshCw, Users, UserCheck, Building2, Phone, Mail, Calendar, Briefcase } from "lucide-react";

type Employee = {
  id:number; name:string; age:number; gender:string; employee_id:string;
  department:string; position:string; phone:string; email:string;
  blood_group:string; join_date:string; photo_b64:string; registered_at:string;
  monthly_attendance:number; monthly_total:number; attendance_rate:number;
};

export default function RegistryPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [query,     setQuery]     = useState("");
  const [deptFilter,setDeptFilter]= useState("");
  const [loading,   setLoading]   = useState(false);
  const [deleting,  setDeleting]  = useState<number|null>(null);

  const fetch_ = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/employees");
      if (res.ok) setEmployees(await res.json());
    } catch {}
    setLoading(false);
  };

  useEffect(()=>{ fetch_(); },[]);

  const handleDelete = async (id:number, name:string) => {
    if(!confirm(`Delete employee "${name}" from the system?`)) return;
    setDeleting(id);
    try {
      const r = await fetch(`http://localhost:8000/api/employees/${id}`,{method:"DELETE"});
      if(r.ok) setEmployees(p=>p.filter(e=>e.id!==id));
    } catch {}
    setDeleting(null);
  };

  const depts    = Array.from(new Set(employees.map(e=>e.department).filter(Boolean)));
  const filtered = employees.filter(e=>{
    const q = query.toLowerCase();
    return (
      (!q || e.name?.toLowerCase().includes(q) || e.employee_id?.includes(q) || e.department?.toLowerCase().includes(q)) &&
      (!deptFilter || e.department === deptFilter)
    );
  });

  const initials = (n:string) => n.split(" ").map(w=>w[0]).join("").slice(0,2).toUpperCase();
  const hue      = (n:string) => Array.from(n).reduce((a,c)=>a+c.charCodeAt(0),0)%360;

  return (
    <>
      <Topbar title="Employee Registry" subtitle="Manage registered employees · face biometrics" />
      <div className="px-6 py-5 max-w-[1400px] mx-auto space-y-5">

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            {icon:<Users size={16}/>,     label:"Total Employees", value:employees.length,                           color:"#00c8ff"},
            {icon:<UserCheck size={16}/>, label:"Departments",     value:depts.length,                               color:"#7b61ff"},
            {icon:<Building2 size={16}/>, label:"Avg Attendance",  value:`${Math.round(employees.reduce((a,e)=>a+(e.attendance_rate||0),0)/Math.max(employees.length,1))}%`, color:"#00e676"},
            {icon:<Calendar size={16}/>,  label:"Showing",         value:filtered.length,                            color:"#ffab40"},
          ].map(({icon,label,value,color})=>(
            <Card key={label}>
              <CardContent className="py-3 flex items-center gap-3">
                <div className="p-2 rounded-lg shrink-0" style={{background:`${color}14`,color}}>{icon}</div>
                <div>
                  <div className="text-xl font-bold" style={{color}}>{value}</div>
                  <div className="text-[0.62rem] uppercase tracking-wide text-[#4a7a9a]">{label}</div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Controls */}
        <div className="flex flex-wrap gap-3 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#3a5570]"/>
            <input className="w-full pl-8 pr-3 py-2 rounded-lg text-sm text-[#e0eeff] placeholder-[#3a5570] focus:outline-none focus:ring-1 focus:ring-[#00c8ff]"
                   style={{background:"rgba(0,200,255,0.05)",border:"1px solid rgba(0,200,255,0.20)"}}
                   placeholder="Search by name, ID or department…" value={query} onChange={e=>setQuery(e.target.value)}/>
          </div>
          <select className="px-3 py-2 rounded-lg text-sm text-[#e0eeff] focus:outline-none focus:ring-1 focus:ring-[#00c8ff]"
                  style={{background:"rgba(0,200,255,0.05)",border:"1px solid rgba(0,200,255,0.20)"}}
                  value={deptFilter} onChange={e=>setDeptFilter(e.target.value)}>
            <option value="" style={{background:"#0b1220"}}>All Departments</option>
            {depts.map(d=><option key={d} value={d} style={{background:"#0b1220"}}>{d}</option>)}
          </select>
          <Button variant="secondary" size="sm" onClick={fetch_} disabled={loading}>
            <RefreshCw size={13} className={loading?"animate-spin":""}/>Refresh
          </Button>
        </div>

        {/* Employee grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(emp=>(
            <Card key={emp.id} className="hover:-translate-y-0.5 transition-transform duration-200">
              <CardContent className="pt-4">
                {/* Header */}
                <div className="flex items-start gap-3 mb-3">
                  {emp.photo_b64 ? (
                    <img src={emp.photo_b64} className="w-14 h-14 rounded-xl object-cover ring-2 ring-[rgba(0,200,255,0.30)] shrink-0" alt=""/>
                  ) : (
                    <div className="w-14 h-14 rounded-xl flex items-center justify-center text-lg font-black text-white ring-2 ring-[rgba(0,200,255,0.20)] shrink-0"
                         style={{background:`hsl(${hue(emp.name)},55%,38%)`}}>
                      {initials(emp.name)}
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-[#c8e8ff] truncate text-sm">{emp.name}</h3>
                    <p className="text-[0.70rem] text-[#4a7a9a] truncate">{emp.position||"—"}</p>
                    <div className="flex gap-1.5 mt-1 flex-wrap">
                      {emp.department && <Badge variant="default" className="text-[0.58rem]">{emp.department}</Badge>}
                      {emp.blood_group && <Badge variant="danger" className="text-[0.58rem]">{emp.blood_group}</Badge>}
                    </div>
                  </div>
                  <Button variant="danger" size="sm" className="!px-2 !py-1.5 shrink-0" onClick={()=>handleDelete(emp.id,emp.name)} disabled={deleting===emp.id}>
                    <Trash2 size={12}/>
                  </Button>
                </div>

                {/* Info grid */}
                <div className="space-y-1 border-t border-white/[0.07] pt-2.5">
                  {[
                    {icon:<Briefcase size={11}/>, label:"Employee ID", value:emp.employee_id||"—"},
                    {icon:<Phone size={11}/>,     label:"Phone",       value:emp.phone||"—"},
                    {icon:<Mail size={11}/>,      label:"Email",       value:emp.email||"—"},
                    {icon:<Calendar size={11}/>,  label:"Joined",      value:emp.join_date||"—"},
                  ].map(({icon,label,value})=>(
                    <div key={label} className="flex items-center gap-2 text-xs">
                      <span className="text-[#2a5570] shrink-0">{icon}</span>
                      <span className="text-[#3a5570] w-20 shrink-0">{label}</span>
                      <span className="text-[#8ab0cc] truncate">{value}</span>
                    </div>
                  ))}
                </div>

                {/* Attendance this month */}
                <div className="mt-3 pt-2.5 border-t border-white/[0.07]">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-[0.62rem] text-[#3a5570] uppercase tracking-wide">This month's attendance</span>
                    <span className="text-xs font-bold" style={{color:emp.attendance_rate>=80?"#00e676":emp.attendance_rate>=60?"#ffab40":"#ff4d6d"}}>
                      {emp.monthly_attendance}/{emp.monthly_total} days
                    </span>
                  </div>
                  <div className="h-1.5 rounded-full overflow-hidden" style={{background:"rgba(255,255,255,0.07)"}}>
                    <div className="h-full rounded-full transition-all" style={{
                      width:`${emp.attendance_rate||0}%`,
                      background:emp.attendance_rate>=80?"linear-gradient(90deg,#00c8ff,#00e676)":emp.attendance_rate>=60?"linear-gradient(90deg,#ffab40,#00c8ff)":"linear-gradient(90deg,#ff4d6d,#ffab40)",
                    }}/>
                  </div>
                  <div className="flex justify-between items-center mt-1">
                    <Badge variant={emp.attendance_rate>=80?"success":emp.attendance_rate>=60?"warning":"danger"} className="text-[0.55rem]">
                      {emp.attendance_rate>=80?"Excellent":emp.attendance_rate>=60?"Average":"Below Target"}
                    </Badge>
                    <span className="text-[0.65rem] font-bold" style={{color:emp.attendance_rate>=80?"#00e676":emp.attendance_rate>=60?"#ffab40":"#ff4d6d"}}>
                      {emp.attendance_rate||0}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {filtered.length===0 && (
            <div className="col-span-3 text-center py-14 text-[#3a5570]">
              <Users size={44} className="mx-auto mb-3 opacity-25"/>
              <p className="text-base font-medium">{query||deptFilter?"No employees match your filter":"No employees registered yet"}</p>
              <p className="text-sm mt-1 text-[#2a4050]">{!query&&!deptFilter&&"Go to Register Employee to add the first employee"}</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
