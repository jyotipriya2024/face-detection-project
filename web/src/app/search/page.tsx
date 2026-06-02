"use client";
import { useRef, useState, useCallback } from "react";
import Topbar from "@/components/Topbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  Upload, Search, Loader2, ImageIcon, User, Building2,
  Briefcase, Phone, Mail, Calendar, CheckCircle, XCircle, ScanFace,
} from "lucide-react";

type Employee = {
  name: string; age: number; gender: string; employee_id: string;
  department: string; position: string; phone: string; email: string;
  blood_group: string; join_date: string; photo_b64: string;
};
type AttHistory = { date: string; check_in: string; department: string; status: string };
type Match = {
  name: string; confidence: number; status: "known" | "unknown";
  employee: Employee | null;
  attendance_history: AttHistory[];
  monthly_attendance_rate: number;
};
type SearchResponse = {
  matches: Match[];
  count: number;
  no_face_detected?: boolean;
  message?: string;
};

type UIState = "idle" | "loading" | "no_face" | "no_match" | "found";

export default function SearchPage() {
  const inputRef  = useRef<HTMLInputElement>(null);
  const [preview,  setPreview]  = useState<string | null>(null);
  const [result,   setResult]   = useState<Match | null>(null);
  const [uiState,  setUiState]  = useState<UIState>("idle");
  const [apiMsg,   setApiMsg]   = useState("");
  const [error,    setError]    = useState("");

  const handleFile = useCallback((file: File) => {
    const r = new FileReader();
    r.onload = e => {
      setPreview(e.target?.result as string);
      setResult(null); setUiState("idle"); setError(""); setApiMsg("");
    };
    r.readAsDataURL(file);
  }, []);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const runSearch = async () => {
    if (!preview) return;
    setUiState("loading"); setError(""); setApiMsg("");
    try {
      const res = await fetch("http://localhost:8000/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: preview }),
      });

      if (!res.ok) {
        setError(`Server error ${res.status}. Please try again.`);
        setUiState("idle");
        return;
      }

      const data: SearchResponse = await res.json();

      if (data.no_face_detected) {
        setApiMsg(data.message ?? "No face detected in image.");
        setUiState("no_face");
        return;
      }

      const first = data.matches?.[0] ?? null;
      setResult(first);

      if (!first || first.status === "unknown") {
        setUiState("no_match");
      } else {
        setUiState("found");
      }
    } catch {
      setError("Cannot connect to backend. Make sure the API server is running on port 8000.");
      setUiState("idle");
    }
  };

  const emp      = result?.employee;
  const initials = (n: string) => n.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
  const hue      = (n: string) => Array.from(n).reduce((a, c) => a + c.charCodeAt(0), 0) % 360;

  return (
    <>
      <Topbar title="Face Search" subtitle="Upload a photo to identify employee & view attendance" />
      <div className="px-6 py-5 max-w-[1400px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">

          {/* ── Left: Upload panel ─────────────────────────────────────── */}
          <div className="lg:col-span-2 space-y-4">
            <Card>
              <CardHeader><CardTitle>Upload Employee Photo</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {/* Drop zone */}
                <div
                  className="rounded-xl border-2 border-dashed flex flex-col items-center justify-center cursor-pointer transition-all hover:border-[#00c8ff] hover:bg-[rgba(0,200,255,0.04)]"
                  style={{ minHeight: 200, borderColor: "rgba(0,200,255,0.25)", background: "rgba(0,200,255,0.02)" }}
                  onClick={() => inputRef.current?.click()}
                  onDrop={onDrop}
                  onDragOver={e => e.preventDefault()}
                >
                  {preview ? (
                    <img src={preview} className="max-h-52 max-w-full rounded-lg object-contain" alt="Preview" />
                  ) : (
                    <>
                      <ScanFace size={48} className="text-[#2a5570] mb-3" />
                      <p className="text-sm text-[#4a7a9a] font-medium">Drop image here or click to browse</p>
                      <p className="text-xs text-[#2a4255] mt-1">JPG · PNG · WEBP supported</p>
                    </>
                  )}
                </div>
                <input
                  ref={inputRef} type="file" accept="image/*" className="hidden"
                  onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
                />

                <div className="flex gap-2">
                  <Button variant="secondary" className="flex-1" size="sm"
                          onClick={() => inputRef.current?.click()}>
                    <Upload size={13} />{preview ? "Change Photo" : "Browse Files"}
                  </Button>
                  <Button variant="primary" className="flex-1" size="md"
                          onClick={runSearch} disabled={!preview || uiState === "loading"}>
                    {uiState === "loading"
                      ? <><Loader2 size={14} className="animate-spin" />Searching…</>
                      : <><Search size={14} />Search Employee</>}
                  </Button>
                </div>

                {error && (
                  <div className="flex items-center gap-2 p-2.5 rounded-lg text-xs text-[#ff4d6d]"
                       style={{ background: "rgba(255,77,109,0.08)", border: "1px solid rgba(255,77,109,0.22)" }}>
                    <XCircle size={13} className="shrink-0" />{error}
                  </div>
                )}

                {/* Tips */}
                <div className="pt-1 space-y-1">
                  <p className="text-[0.58rem] font-bold tracking-widest uppercase text-[#2a4a60]">For best results</p>
                  {[
                    "Use a clear, front-facing photo",
                    "Good lighting — no harsh shadows",
                    "Face must be visible and unobstructed",
                    "Same person registered in the system",
                  ].map(t => (
                    <div key={t} className="flex items-center gap-1.5 text-[0.65rem] text-[#3a5570]">
                      <span className="text-[#00c8ff]">›</span>{t}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Monthly attendance gauge — shown only on found */}
            {uiState === "found" && result && (
              <Card>
                <CardContent className="pt-4">
                  <p className="text-[0.60rem] font-bold tracking-widest uppercase text-[#2a5570] mb-3">◈ This Month's Attendance</p>
                  <div className="text-center">
                    <div className="text-4xl font-extrabold text-[#00c8ff] font-mono">
                      {result.monthly_attendance_rate}%
                    </div>
                    <p className="text-xs text-[#4a7a9a] mt-1">Monthly Attendance Rate</p>
                    <div className="mt-3 h-2.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.07)" }}>
                      <div className="h-full rounded-full transition-all duration-500" style={{
                        width: `${result.monthly_attendance_rate}%`,
                        background: result.monthly_attendance_rate >= 80
                          ? "linear-gradient(90deg,#00c8ff,#00e676)"
                          : result.monthly_attendance_rate >= 60
                            ? "linear-gradient(90deg,#ffab40,#00c8ff)"
                            : "linear-gradient(90deg,#ff4d6d,#ffab40)",
                      }} />
                    </div>
                    <Badge
                      variant={result.monthly_attendance_rate >= 80 ? "success" : result.monthly_attendance_rate >= 60 ? "warning" : "danger"}
                      className="mt-2"
                    >
                      {result.monthly_attendance_rate >= 80 ? "Excellent" : result.monthly_attendance_rate >= 60 ? "Average" : "Below Target"}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* ── Right: Results panel ───────────────────────────────────── */}
          <div className="lg:col-span-3 space-y-4">

            {/* Idle */}
            {uiState === "idle" && (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-20 text-[#3a5570]">
                  <Search size={52} className="opacity-20 mb-3" />
                  <p className="text-base font-medium">Upload a photo and click Search</p>
                  <p className="text-sm mt-1 text-[#2a4050]">Results include full employee profile + attendance history</p>
                </CardContent>
              </Card>
            )}

            {/* Loading */}
            {uiState === "loading" && (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-20 gap-4">
                  <Loader2 size={44} className="text-[#00c8ff] animate-spin" />
                  <div className="text-center">
                    <p className="text-sm font-semibold text-[#8ab0cc]">Analysing image…</p>
                    <p className="text-xs text-[#3a5570] mt-1">Detecting face · Extracting features · Matching database</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* No face detected in uploaded image */}
            {uiState === "no_face" && (
              <Card>
                <CardContent className="flex flex-col items-center py-16 text-center space-y-3">
                  <div className="w-16 h-16 rounded-full flex items-center justify-center"
                       style={{ background: "rgba(255,171,64,0.12)", border: "2px solid rgba(255,171,64,0.35)" }}>
                    <ScanFace size={30} className="text-[#ffab40]" />
                  </div>
                  <h3 className="text-base font-bold text-[#ffab40]">No Face Detected</h3>
                  <p className="text-sm text-[#5a4a30] max-w-xs">{apiMsg}</p>
                  <div className="flex gap-2 flex-wrap justify-center mt-2">
                    <Badge variant="warning">Try a clearer photo</Badge>
                    <Badge variant="warning">Ensure face is visible</Badge>
                    <Badge variant="warning">Better lighting</Badge>
                  </div>
                  <Button variant="secondary" size="sm" onClick={() => inputRef.current?.click()}>
                    <Upload size={13} />Upload Different Photo
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Face detected but no match in DB */}
            {uiState === "no_match" && (
              <Card>
                <CardContent className="flex flex-col items-center py-16 text-center space-y-3">
                  <div className="w-16 h-16 rounded-full flex items-center justify-center"
                       style={{ background: "rgba(255,77,109,0.12)", border: "2px solid rgba(255,77,109,0.35)" }}>
                    <XCircle size={30} className="text-[#ff4d6d]" />
                  </div>
                  <h3 className="text-lg font-bold text-[#ff4d6d]">No Match Found</h3>
                  <p className="text-sm text-[#5a3a4a]">Face detected but not found in the employee database.</p>
                  <div className="flex gap-2 flex-wrap justify-center mt-1">
                    <Badge variant="danger">Unregistered Person</Badge>
                  </div>
                  <p className="text-xs text-[#3a4a50]">
                    If this is a registered employee, try with a clearer photo or re-register them.
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Match found */}
            {uiState === "found" && result && emp && (
              <>
                {/* Employee profile */}
                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-start gap-4 mb-4">
                      {emp.photo_b64 ? (
                        <img src={emp.photo_b64}
                             className="w-20 h-20 rounded-xl object-cover ring-2 ring-[#00c8ff] shrink-0"
                             alt={emp.name} />
                      ) : (
                        <div className="w-20 h-20 rounded-xl flex items-center justify-center text-xl font-black text-white ring-2 ring-[#00c8ff] shrink-0"
                             style={{ background: `hsl(${hue(emp.name)},55%,38%)` }}>
                          {initials(emp.name)}
                        </div>
                      )}
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <h2 className="text-xl font-bold text-[#e0eeff]">{emp.name}</h2>
                          <Badge variant="success">
                            <CheckCircle size={10} className="mr-0.5" />
                            {(result.confidence * 100).toFixed(1)}% match
                          </Badge>
                        </div>
                        <p className="text-sm text-[#4a8ab0] mt-0.5">{emp.position || "—"}</p>
                        <div className="flex gap-2 mt-1.5 flex-wrap">
                          <Badge variant="default"><Building2 size={10} className="mr-0.5" />{emp.department || "—"}</Badge>
                          {emp.employee_id && <Badge variant="purple">ID: {emp.employee_id}</Badge>}
                          {emp.blood_group && <Badge variant="danger">{emp.blood_group}</Badge>}
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-x-4">
                      {[
                        { icon: <User size={12} />,      label: "Age",      value: `${emp.age || "—"} yrs` },
                        { icon: <User size={12} />,      label: "Gender",   value: emp.gender   || "—" },
                        { icon: <Phone size={12} />,     label: "Phone",    value: emp.phone    || "—" },
                        { icon: <Mail size={12} />,      label: "Email",    value: emp.email    || "—" },
                        { icon: <Calendar size={12} />,  label: "Join Date",value: emp.join_date || "—" },
                        { icon: <Briefcase size={12} />, label: "Position", value: emp.position || "—" },
                      ].map(({ icon, label, value }) => (
                        <div key={label} className="flex items-center gap-2 py-1.5 border-b border-white/[0.05] last:border-0">
                          <span className="text-[#2a5570] shrink-0">{icon}</span>
                          <span className="text-[0.65rem] text-[#4a7a9a] w-20 shrink-0">{label}</span>
                          <span className="text-xs font-medium text-[#c8e8ff] truncate">{value}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Attendance history table */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Attendance History</CardTitle>
                      <Badge variant={result.attendance_history?.length > 0 ? "default" : "danger"}>
                        {result.attendance_history?.length ?? 0} records
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="p-0">
                    {result.attendance_history?.length > 0 ? (
                      <table className="w-full text-sm">
                        <thead>
                          <tr style={{ borderBottom: "1px solid rgba(0,200,255,0.10)" }}>
                            {["Date", "Check-in Time", "Department", "Status"].map(h => (
                              <th key={h} className="text-left px-4 py-2.5 text-[0.62rem] font-bold uppercase tracking-wider text-[#2a5570]">{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {result.attendance_history.map((h, i) => (
                            <tr key={i} className="border-b border-white/[0.04] hover:bg-white/[0.025] transition-colors">
                              <td className="px-4 py-2.5 text-xs font-mono text-[#8ab0cc]">{h.date}</td>
                              <td className="px-4 py-2.5 text-xs font-mono text-[#00c8ff]">
                                {h.check_in ? h.check_in.slice(11, 16) : "—"}
                              </td>
                              <td className="px-4 py-2.5 text-xs text-[#6a8fa8]">{h.department || "—"}</td>
                              <td className="px-4 py-2.5">
                                <Badge variant="success" className="text-[0.55rem]">Present</Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <div className="text-center py-8 text-[#3a5570]">
                        <p className="text-sm">No attendance records found for this employee</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
