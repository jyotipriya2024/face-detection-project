"use client";
import { useRef, useState, useCallback, useEffect } from "react";
import Topbar from "@/components/Topbar";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Video, VideoOff, Camera, User, Clock, Building2, Briefcase, Phone, Mail, CheckCircle, AlertTriangle } from "lucide-react";

type Employee = {
  id: number; name: string; age: number; gender: string;
  employee_id: string; department: string; position: string;
  phone: string; email: string; blood_group: string; photo_b64: string;
};

type Detection = {
  id: number; name: string; confidence: number; status: "known"|"unknown";
  employee: Employee | null; check_in_new: boolean; check_in_time: string;
  bbox: number[];
};

export default function LiveDetectionPage() {
  const videoRef    = useRef<HTMLVideoElement>(null);
  const canvasRef   = useRef<HTMLCanvasElement>(null);
  const streamRef   = useRef<MediaStream | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const [running,    setRunning]    = useState(false);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [fps,        setFps]        = useState(0);
  const [selected,   setSelected]   = useState<Detection | null>(null);
  const [error,      setError]      = useState("");
  const [checkinLog, setCheckinLog] = useState<{name:string;time:string;dept:string}[]>([]);
  const frameCountRef = useRef(0);

  const sendFrame = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;
    const ctx = canvasRef.current.getContext("2d")!;
    canvasRef.current.width = 320; canvasRef.current.height = 240;
    ctx.drawImage(videoRef.current, 0, 0, 320, 240);
    try {
      const res  = await fetch("http://localhost:8000/api/detect", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: canvasRef.current.toDataURL("image/jpeg", 0.70), log_attendance: true }),
      });
      if (res.ok) {
        const data = await res.json();
        setDetections(data.detections ?? []);
        if (data.detections?.length > 0) setSelected(data.detections[0]);
        data.detections?.forEach((d: Detection) => {
          if (d.check_in_new && d.employee) {
            setCheckinLog(prev => [
              { name: d.name, time: new Date().toLocaleTimeString("en-IN",{hour12:true}), dept: d.employee!.department },
              ...prev.slice(0, 9),
            ]);
          }
        });
      }
    } catch { /* backend offline */ }
    frameCountRef.current += 1;
  }, []);

  // FPS ticker — stable interval, reads from ref not state
  useEffect(() => {
    const t = setInterval(() => {
      setFps(frameCountRef.current);
      frameCountRef.current = 0;
    }, 1000);
    return () => clearInterval(t);
  }, []);

  const start = useCallback(async () => {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode:"user" } });
      streamRef.current = stream;
      if (videoRef.current) { videoRef.current.srcObject = stream; await videoRef.current.play(); }
      intervalRef.current = setInterval(sendFrame, 600);
      setRunning(true);
    } catch { setError("Camera access denied."); }
  }, [sendFrame]);

  const stop = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
    setRunning(false); setDetections([]); setSelected(null);
  }, []);

  useEffect(() => () => stop(), [stop]);

  const initials = (name: string) => name.split(" ").map(w=>w[0]).join("").slice(0,2).toUpperCase();
  const hue      = (name: string) => Array.from(name).reduce((a,c)=>a+c.charCodeAt(0),0) % 360;

  return (
    <>
      <Topbar title="Live Face Detection" subtitle="Real-time employee identification · Auto attendance" />
      <div className="px-6 py-5 max-w-[1440px] mx-auto">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">

          {/* Camera Feed */}
          <div className="xl:col-span-2 space-y-4">
            <Card>
              <CardContent className="p-0 relative">
                <div className="relative rounded-xl overflow-hidden aspect-video"
                     style={{ background: "#000" }}>
                  <video ref={videoRef} className="w-full h-full object-cover" autoPlay muted playsInline />
                  {!running && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-[#3a5570]">
                      <Video size={64} className="opacity-30" />
                      <p className="text-base font-medium">Camera not active</p>
                      <p className="text-sm text-[#2a4560]">Click Start to begin face detection</p>
                    </div>
                  )}
                  {running && (
                    <div className="absolute top-3 left-3 flex items-center gap-2">
                      <Badge variant="live"><span className="w-1.5 h-1.5 rounded-full bg-[#ff4d6d] live-dot" />LIVE</Badge>
                      <Badge variant="default">{fps} fps</Badge>
                      <Badge variant={detections.length > 0 ? "success" : "default"}>{detections.length} face{detections.length !== 1 ? "s" : ""}</Badge>
                    </div>
                  )}
                  <canvas ref={canvasRef} className="hidden" />
                </div>
              </CardContent>
            </Card>

            <div className="flex gap-3">
              {!running
                ? <Button variant="primary" size="lg" className="flex-1" onClick={start}><Camera size={16} />Start Detection</Button>
                : <Button variant="danger"  size="lg" className="flex-1" onClick={stop}><VideoOff size={16} />Stop Camera</Button>
              }
            </div>
            {error && <p className="text-[#ff4d6d] text-sm">{error}</p>}

            {/* Today's check-in log */}
            {checkinLog.length > 0 && (
              <Card>
                <CardContent className="py-3">
                  <p className="text-[0.60rem] font-bold tracking-widest uppercase text-[#2a5570] mb-2">◈ Today's Check-ins (this session)</p>
                  <div className="space-y-1.5 max-h-32 overflow-y-auto">
                    {checkinLog.map((c,i) => (
                      <div key={i} className="flex items-center gap-3 text-sm">
                        <CheckCircle size={13} className="text-[#00e676] shrink-0" />
                        <span className="font-semibold text-[#c8e8ff]">{c.name}</span>
                        <span className="text-[#3a5570]">{c.dept}</span>
                        <span className="ml-auto text-xs font-mono text-[#00c8ff]">{c.time}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Employee Profile Panel */}
          <div className="space-y-4">

            {/* Detected employee card */}
            {selected && selected.status === "known" && selected.employee ? (
              <Card className="overflow-visible">
                <CardContent className="pt-4">
                  {/* Status header */}
                  <div className={`flex items-center gap-2 px-3 py-2 rounded-lg mb-4 ${selected.check_in_new
                    ? "bg-[rgba(0,230,118,0.10)] border border-[rgba(0,230,118,0.25)]"
                    : "bg-[rgba(0,200,255,0.08)] border border-[rgba(0,200,255,0.20)]"}`}>
                    <CheckCircle size={14} className={selected.check_in_new ? "text-[#00e676]" : "text-[#00c8ff]"} />
                    <div>
                      <p className={`text-xs font-bold ${selected.check_in_new ? "text-[#00e676]" : "text-[#00c8ff]"}`}>
                        {selected.check_in_new ? "✓ Checked In Now!" : "Already Checked In"}
                      </p>
                      {selected.check_in_time && (
                        <p className="text-[0.65rem] text-[#3a5570]">Time: {selected.check_in_time}</p>
                      )}
                    </div>
                    <Badge variant="default" className="ml-auto">{(selected.confidence*100).toFixed(0)}%</Badge>
                  </div>

                  {/* Avatar + name */}
                  <div className="flex items-center gap-4 mb-4">
                    {selected.employee.photo_b64 ? (
                      <img src={selected.employee.photo_b64} className="w-16 h-16 rounded-full object-cover ring-2 ring-[#00c8ff]" alt="" />
                    ) : (
                      <div className="w-16 h-16 rounded-full flex items-center justify-center text-xl font-black text-white ring-2 ring-[#00c8ff]"
                           style={{ background: `hsl(${hue(selected.employee.name)},55%,38%)` }}>
                        {initials(selected.employee.name)}
                      </div>
                    )}
                    <div>
                      <h3 className="text-lg font-bold text-[#e0eeff]">{selected.employee.name}</h3>
                      <p className="text-sm text-[#4a8ab0]">{selected.employee.position || "—"}</p>
                      <Badge variant="default" className="mt-1">{selected.employee.department || "—"}</Badge>
                    </div>
                  </div>

                  {/* Details grid */}
                  <div className="space-y-2">
                    {[
                      { icon: <User size={12}/>,       label: "Employee ID",  value: selected.employee.employee_id || "—" },
                      { icon: <Building2 size={12}/>,  label: "Department",   value: selected.employee.department   || "—" },
                      { icon: <Briefcase size={12}/>,  label: "Position",     value: selected.employee.position     || "—" },
                      { icon: <User size={12}/>,       label: "Age / Gender", value: `${selected.employee.age||"—"} / ${selected.employee.gender||"—"}` },
                      { icon: <Phone size={12}/>,      label: "Phone",        value: selected.employee.phone        || "—" },
                      { icon: <Mail size={12}/>,       label: "Email",        value: selected.employee.email        || "—" },
                    ].map(({ icon, label, value }) => (
                      <div key={label} className="flex items-center gap-2 py-1.5 border-b border-white/[0.05] last:border-0">
                        <span className="text-[#2a5570]">{icon}</span>
                        <span className="text-[0.68rem] text-[#4a7a9a] w-24 shrink-0">{label}</span>
                        <span className="text-xs font-medium text-[#c8e8ff] truncate">{value}</span>
                      </div>
                    ))}
                  </div>

                  {/* Confidence bar */}
                  <div className="mt-3">
                    <div className="flex justify-between text-[0.62rem] text-[#3a5570] mb-1">
                      <span>Match Confidence</span>
                      <span className="text-[#00c8ff] font-bold">{(selected.confidence*100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 rounded-full overflow-hidden" style={{ background:"rgba(255,255,255,0.07)" }}>
                      <div className="h-full rounded-full transition-all duration-500"
                           style={{ width:`${selected.confidence*100}%`, background:"linear-gradient(90deg,#00c8ff,#00e676)" }} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : selected && selected.status === "unknown" ? (
              <Card>
                <CardContent className="pt-4 text-center py-8">
                  <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3"
                       style={{ background:"rgba(255,77,109,0.12)", border:"2px solid rgba(255,77,109,0.35)" }}>
                    <AlertTriangle size={28} className="text-[#ff4d6d]" />
                  </div>
                  <h3 className="text-base font-bold text-[#ff4d6d] mb-1">Unknown Person</h3>
                  <p className="text-xs text-[#5a3a4a]">Face not found in employee database</p>
                  <Badge variant="danger" className="mt-3">Not Registered</Badge>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="pt-4 text-center py-10">
                  <User size={48} className="mx-auto mb-3 text-[#2a4a60] opacity-40" />
                  <p className="text-sm text-[#3a5570]">{running ? "Waiting for face…" : "Start camera to detect"}</p>
                </CardContent>
              </Card>
            )}

            {/* Multi-face list */}
            {detections.length > 1 && (
              <Card>
                <CardContent className="py-3">
                  <p className="text-[0.60rem] font-bold tracking-widest uppercase text-[#2a5570] mb-2">All Detected Faces</p>
                  <div className="space-y-1.5">
                    {detections.map(d => (
                      <button key={d.id} onClick={() => setSelected(d)}
                              className={`w-full flex items-center gap-2 px-2.5 py-2 rounded-lg text-left transition-colors ${
                                selected?.id===d.id ? "bg-[rgba(0,200,255,0.10)]" : "hover:bg-white/[0.04]"}`}>
                        <div className="w-7 h-7 rounded-full flex items-center justify-center text-[0.62rem] font-black text-white shrink-0"
                             style={{ background: d.status==="known" ? `hsl(${hue(d.name)},55%,38%)` : "#3a1a24" }}>
                          {d.status==="known" ? initials(d.name) : "?"}
                        </div>
                        <span className="text-xs font-semibold text-[#c8e8ff] flex-1 truncate">{d.name}</span>
                        <Badge variant={d.status==="known"?"success":"danger"} className="text-[0.55rem]">{(d.confidence*100).toFixed(0)}%</Badge>
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Stats */}
            <Card>
              <CardContent className="py-3 grid grid-cols-2 gap-2">
                {[
                  ["Faces Detected", detections.length],
                  ["Recognised",     detections.filter(d=>d.status==="known").length],
                  ["Unknown",        detections.filter(d=>d.status==="unknown").length],
                  ["Frame Rate",     `${fps} fps`],
                ].map(([k,v]) => (
                  <div key={String(k)} className="rounded-lg px-2.5 py-2 text-center"
                       style={{ background:"rgba(0,200,255,0.04)", border:"1px solid rgba(0,200,255,0.10)" }}>
                    <div className="text-lg font-bold text-[#00c8ff]">{v}</div>
                    <div className="text-[0.60rem] text-[#3a5570] uppercase tracking-wide">{k}</div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}
