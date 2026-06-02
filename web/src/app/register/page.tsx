"use client";
import { useRef, useState, useCallback } from "react";
import Topbar from "@/components/Topbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  Camera, CheckCircle, AlertCircle, Loader2, UserPlus, RefreshCw, User,
  XCircle,
} from "lucide-react";

type Status = "idle" | "capturing" | "preview" | "submitting" | "success" | "error";
type Errors = Partial<Record<keyof FormData | "photo", string>>;
type FormData = {
  name: string; age: string; gender: string; employee_id: string;
  department: string; position: string; phone: string; email: string;
  blood_group: string; join_date: string; notes: string;
};

const DEPARTMENTS  = ["Engineering","HR","Finance","Marketing","Security","Operations","IT","Legal","Admin","Other"];
const POSITIONS    = ["Manager","Senior Engineer","Engineer","Analyst","Executive","Director","Intern","Supervisor","Staff","Other"];
const BLOOD_GROUPS = ["A+","A−","B+","B−","AB+","AB−","O+","O−"];
const SAMPLE_COUNT = 5;           // face samples captured per enrollment
const SAMPLE_DELAY = 350;         // ms between burst frames

const EMPTY: FormData = {
  name:"", age:"", gender:"", employee_id:"",
  department:"", position:"", phone:"", email:"",
  blood_group:"", join_date:"", notes:"",
};

// ── Validation rules ───────────────────────────────────────────────────────
function validate(form: FormData, photo: string | null): Errors {
  const errs: Errors = {};

  if (!photo) errs.photo = "Face photo is required before submitting.";

  const name = form.name.trim();
  if (!name)                    errs.name = "Full name is required.";
  else if (name.length < 2)     errs.name = "Name must be at least 2 characters.";
  else if (name.length > 80)    errs.name = "Name must be 80 characters or fewer.";
  else if (!/^[A-Za-z\s.'-]+$/.test(name)) errs.name = "Name can only contain letters, spaces, dots, hyphens and apostrophes.";

  const age = parseInt(form.age);
  if (form.age && (isNaN(age) || age < 18 || age > 70))
    errs.age = "Age must be between 18 and 70.";

  const empId = form.employee_id.trim();
  if (!empId)                     errs.employee_id = "Employee ID is required.";
  else if (!/^[A-Za-z0-9\-_]+$/.test(empId)) errs.employee_id = "Employee ID: letters, numbers, hyphens and underscores only.";
  else if (empId.length > 20)     errs.employee_id = "Employee ID must be 20 characters or fewer.";

  if (!form.gender)     errs.gender     = "Please select a gender.";
  if (!form.department) errs.department = "Please select a department.";
  if (!form.position)   errs.position   = "Please select a position/role.";

  const phone = form.phone.replace(/\s/g, "");
  if (phone) {
    const digits = phone.replace(/^\+91/, "").replace(/\D/g,"");
    if (digits.length !== 10)
      errs.phone = "Mobile number must be exactly 10 digits.";
    else if (!/^[6-9]/.test(digits))
      errs.phone = "Indian mobile numbers must start with 6, 7, 8 or 9.";
  }

  const email = form.email.trim();
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email))
    errs.email = "Enter a valid email address.";

  return errs;
}

export default function RegisterPage() {
  const videoRef  = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [status,   setStatus]   = useState<Status>("idle");
  const [captured, setCaptured] = useState<string | null>(null);
  const [samples,  setSamples]  = useState<string[]>([]);
  const [bursting, setBursting] = useState(false);
  const [shotNo,   setShotNo]   = useState(0);
  const [message,  setMessage]  = useState("");
  const [form,     setForm]     = useState<FormData>(EMPTY);
  const [errors,   setErrors]   = useState<Errors>({});
  const [touched,  setTouched]  = useState<Set<string>>(new Set());

  const touch = (k: string) => setTouched(prev => new Set(prev).add(k));

  const set = (k: keyof FormData) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      const val = e.target.value;
      setForm(f => {
        const next = { ...f, [k]: val };
        setErrors(validate(next, captured));
        return next;
      });
      touch(k);
    };

  const startCamera = useCallback(async () => {
    setStatus("capturing");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: "user" } });
      streamRef.current = stream;
      if (videoRef.current) { videoRef.current.srcObject = stream; await videoRef.current.play(); }
    } catch { setStatus("idle"); setMessage("Camera access denied. Please allow camera permissions."); }
  }, []);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
  }, []);

  // Capture a short burst of frames → multi-sample face template (more robust,
  // and lets the backend reject look-alikes far more reliably).
  const capture = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || bursting) return;
    const video  = videoRef.current;
    const canvas = canvasRef.current;
    const ctx    = canvas.getContext("2d")!;
    canvas.width  = video.videoWidth;
    canvas.height = video.videoHeight;

    setBursting(true);
    const shots: string[] = [];
    for (let i = 0; i < SAMPLE_COUNT; i++) {
      ctx.drawImage(video, 0, 0);
      shots.push(canvas.toDataURL("image/jpeg", 0.92));
      setShotNo(i + 1);
      if (i < SAMPLE_COUNT - 1) await new Promise(r => setTimeout(r, SAMPLE_DELAY));
    }
    setSamples(shots);
    setCaptured(shots[0]);
    setErrors(e => { const next = { ...e }; delete next.photo; return next; });
    stopCamera();
    setBursting(false);
    setShotNo(0);
    setStatus("preview");
  }, [stopCamera, bursting]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Touch all fields so errors show
    setTouched(new Set(Object.keys(EMPTY).concat("photo")));
    const errs = validate(form, captured);
    setErrors(errs);
    if (Object.keys(errs).length > 0) {
      setMessage("Please fix the errors above before submitting.");
      setStatus("error");
      return;
    }

    setStatus("submitting"); setMessage("");
    try {
      const imageList = samples.length ? samples : (captured ? [captured] : []);
      const res  = await fetch("http://localhost:8000/api/employees/register", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, age: parseInt(form.age) || 0, images: imageList }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus("success");
        setMessage(`Employee "${form.name}" registered with ${data.samples ?? imageList.length} face sample(s)!`);
        setCaptured(null);
        setSamples([]);
        setForm(EMPTY);
        setErrors({});
        setTouched(new Set());
      } else {
        setStatus("error");
        setMessage(data.detail ?? "Registration failed. Please try again.");
      }
    } catch {
      setStatus("error");
      setMessage("Cannot connect to the backend. Make sure the API server is running on port 8000.");
    }
  };

  // Field styling helpers
  const fieldState = (k: keyof FormData | "photo") => {
    if (!touched.has(k)) return "normal";
    return errors[k] ? "error" : "ok";
  };

  const borderStyle = (k: keyof FormData | "photo") => {
    const s = fieldState(k);
    return s === "error" ? "1px solid rgba(255,77,109,0.65)"
         : s === "ok"    ? "1px solid rgba(0,230,118,0.50)"
         :                 "1px solid rgba(0,200,255,0.20)";
  };

  const inp = (k: keyof FormData) =>
    `w-full px-3 py-2 rounded-lg text-sm text-[#e0eeff] placeholder-[#3a5570] focus:outline-none focus:ring-1 ${
      fieldState(k) === "error" ? "focus:ring-[#ff4d6d]" : "focus:ring-[#00c8ff]"
    } transition-all`;

  const sty = (k: keyof FormData) => ({
    background: "rgba(0,200,255,0.05)",
    border: borderStyle(k),
  } as React.CSSProperties);

  const lbl = "block text-[0.68rem] font-bold text-[#4a7a9a] mb-1 uppercase tracking-wide";

  const FieldError = ({ k }: { k: keyof FormData | "photo" }) =>
    touched.has(k) && errors[k]
      ? <p className="text-[0.65rem] text-[#ff4d6d] mt-1 flex items-center gap-1">
          <XCircle size={10} className="shrink-0" />{errors[k]}
        </p>
      : null;

  const totalErrors = Object.keys(errors).length;

  return (
    <>
      <Topbar title="Register Employee" subtitle="Enrol a new employee with face biometric" />
      <div className="px-6 py-5 max-w-6xl mx-auto">
        <form onSubmit={handleSubmit} noValidate>
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">

            {/* ── Camera panel ──────────────────────────────────────────── */}
            <div className="lg:col-span-2 space-y-4">
              <Card>
                <CardHeader><CardTitle>Face Photo</CardTitle></CardHeader>
                <CardContent className="space-y-3">
                  <div
                    className="rounded-xl overflow-hidden aspect-video flex items-center justify-center relative"
                    style={{
                      background: "#000810",
                      border: borderStyle("photo"),
                    }}
                  >
                    {status === "capturing" && (
                      <video ref={videoRef} className="w-full h-full object-cover" autoPlay muted playsInline />
                    )}
                    {(status === "preview" || (status === "error" && captured)) && captured && (
                      <img src={captured} className="w-full h-full object-cover" alt="Captured" />
                    )}
                    {(status === "idle" || status === "success" || (status === "error" && !captured)) && (
                      <div className="flex flex-col items-center gap-3 text-[#3a5570]">
                        <User size={52} className="opacity-40" />
                        <p className="text-sm">No photo captured</p>
                      </div>
                    )}
                    {(status === "preview" || (status === "error" && !!captured)) && (
                      <Badge variant="success" className="absolute top-2 right-2">✓ {samples.length || 1} Samples Captured</Badge>
                    )}
                    {status === "capturing" && (
                      <>
                        <div className="absolute top-3 left-3 w-8 h-8 border-t-2 border-l-2 border-[#00c8ff] rounded-tl-lg" />
                        <div className="absolute top-3 right-3 w-8 h-8 border-t-2 border-r-2 border-[#00c8ff] rounded-tr-lg" />
                        <div className="absolute bottom-3 left-3 w-8 h-8 border-b-2 border-l-2 border-[#00c8ff] rounded-bl-lg" />
                        <div className="absolute bottom-3 right-3 w-8 h-8 border-b-2 border-r-2 border-[#00c8ff] rounded-br-lg" />
                      </>
                    )}
                  </div>
                  <canvas ref={canvasRef} className="hidden" />
                  <FieldError k="photo" />

                  <div className="flex gap-2">
                    {(status === "idle" || status === "success" || (status === "error" && !captured)) && (
                      <Button variant="primary" size="md" className="flex-1" type="button" onClick={startCamera}>
                        <Camera size={14} /> Start Camera
                      </Button>
                    )}
                    {status === "capturing" && (
                      <Button variant="primary" size="md" className="flex-1" type="button" onClick={capture} disabled={bursting}>
                        {bursting
                          ? <><Loader2 size={14} className="animate-spin" /> Capturing {shotNo}/{SAMPLE_COUNT}…</>
                          : <><Camera size={14} /> Capture {SAMPLE_COUNT} Samples</>}
                      </Button>
                    )}
                    {(status === "preview" || (status === "error" && !!captured)) && (
                      <>
                        <Button variant="secondary" size="md" className="flex-1" type="button"
                                onClick={() => { setCaptured(null); setSamples([]); setErrors(v=>({...v,photo:"Face photo is required."})); startCamera(); }}>
                          <RefreshCw size={13} /> Retake
                        </Button>
                      </>
                    )}
                  </div>

                  {/* Submit status message */}
                  {message && (
                    <div className={`flex items-start gap-2 p-3 rounded-lg text-sm ${
                      status === "success"
                        ? "bg-[rgba(0,230,118,0.08)] text-[#00e676] border border-[rgba(0,230,118,0.25)]"
                        : "bg-[rgba(255,77,109,0.08)] text-[#ff4d6d] border border-[rgba(255,77,109,0.25)]"
                    }`}>
                      {status === "success"
                        ? <CheckCircle size={15} className="shrink-0 mt-0.5" />
                        : <AlertCircle size={15} className="shrink-0 mt-0.5" />}
                      <span>{message}</span>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Photo tips */}
              <Card>
                <CardContent className="py-3 space-y-1.5">
                  <p className="text-[0.60rem] font-bold tracking-widest uppercase text-[#2a5570] mb-2">Photo Tips</p>
                  {[
                    "Face clearly visible, no obstructions",
                    "Good lighting — avoid harsh shadows",
                    "Look straight at the camera",
                    "Remove glasses if possible",
                    "Neutral expression works best",
                  ].map(t => (
                    <div key={t} className="flex items-center gap-2 text-xs text-[#4a7a9a]">
                      <span className="text-[#00e676]">✓</span>{t}
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* ── Form panel ────────────────────────────────────────────── */}
            <div className="lg:col-span-3">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <CardTitle>Employee Information</CardTitle>
                    <div className="flex gap-2">
                      {totalErrors > 0 && touched.size > 0 && (
                        <Badge variant="danger"><XCircle size={10} className="mr-0.5" />{totalErrors} error{totalErrors > 1 ? "s" : ""}</Badge>
                      )}
                      <Badge variant="default">★ = required</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-5">

                  {/* Personal Details */}
                  <div>
                    <p className="text-[0.60rem] font-bold tracking-widest uppercase text-[#00c8ff] mb-3 pb-1.5 border-b border-[rgba(0,200,255,0.12)]">
                      Personal Details
                    </p>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="col-span-2">
                        <label className={lbl}>Full Name ★</label>
                        <input
                          className={inp("name")} style={sty("name")}
                          placeholder="e.g. Jyotipriya Panda"
                          value={form.name}
                          onChange={set("name")}
                          onBlur={() => touch("name")}
                        />
                        <FieldError k="name" />
                      </div>

                      <div>
                        <label className={lbl}>Age (18–70)</label>
                        <input
                          className={inp("age")} style={sty("age")}
                          type="number" placeholder="e.g. 28"
                          min="18" max="70"
                          value={form.age}
                          onChange={set("age")}
                          onBlur={() => touch("age")}
                        />
                        <FieldError k="age" />
                      </div>

                      <div>
                        <label className={lbl}>Gender ★</label>
                        <select
                          className={inp("gender")} style={sty("gender")}
                          value={form.gender}
                          onChange={set("gender")}
                          onBlur={() => touch("gender")}
                        >
                          <option value="" style={{ background:"#0b1220" }}>Select gender</option>
                          {["Male","Female","Other"].map(g =>
                            <option key={g} value={g} style={{ background:"#0b1220" }}>{g}</option>
                          )}
                        </select>
                        <FieldError k="gender" />
                      </div>

                      <div>
                        <label className={lbl}>Blood Group</label>
                        <select className={inp("blood_group")} style={sty("blood_group")}
                          value={form.blood_group} onChange={set("blood_group")}>
                          <option value="" style={{ background:"#0b1220" }}>Select</option>
                          {BLOOD_GROUPS.map(b => <option key={b} value={b} style={{ background:"#0b1220" }}>{b}</option>)}
                        </select>
                      </div>

                      <div>
                        <label className={lbl}>Join Date</label>
                        <input className={inp("join_date")} style={sty("join_date")}
                          type="date" value={form.join_date} onChange={set("join_date")} />
                      </div>
                    </div>
                  </div>

                  {/* Company Details */}
                  <div>
                    <p className="text-[0.60rem] font-bold tracking-widest uppercase text-[#7b61ff] mb-3 pb-1.5 border-b border-[rgba(123,97,255,0.15)]">
                      Company Details
                    </p>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className={lbl}>Employee ID ★</label>
                        <input
                          className={inp("employee_id")} style={sty("employee_id")}
                          placeholder="e.g. EMP-2024-001"
                          value={form.employee_id}
                          onChange={set("employee_id")}
                          onBlur={() => touch("employee_id")}
                        />
                        <FieldError k="employee_id" />
                      </div>

                      <div>
                        <label className={lbl}>Department ★</label>
                        <select
                          className={inp("department")} style={sty("department")}
                          value={form.department}
                          onChange={set("department")}
                          onBlur={() => touch("department")}
                        >
                          <option value="" style={{ background:"#0b1220" }}>Select department</option>
                          {DEPARTMENTS.map(d => <option key={d} value={d} style={{ background:"#0b1220" }}>{d}</option>)}
                        </select>
                        <FieldError k="department" />
                      </div>

                      <div className="col-span-2">
                        <label className={lbl}>Position / Role ★</label>
                        <select
                          className={inp("position")} style={sty("position")}
                          value={form.position}
                          onChange={set("position")}
                          onBlur={() => touch("position")}
                        >
                          <option value="" style={{ background:"#0b1220" }}>Select position</option>
                          {POSITIONS.map(p => <option key={p} value={p} style={{ background:"#0b1220" }}>{p}</option>)}
                        </select>
                        <FieldError k="position" />
                      </div>
                    </div>
                  </div>

                  {/* Contact Details */}
                  <div>
                    <p className="text-[0.60rem] font-bold tracking-widest uppercase text-[#ffab40] mb-3 pb-1.5 border-b border-[rgba(255,171,64,0.15)]">
                      Contact Details
                    </p>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className={lbl}>Mobile Number (10 digits)</label>
                        <input
                          className={inp("phone")} style={sty("phone")}
                          type="tel"
                          placeholder="e.g. 9876543210"
                          maxLength={13}
                          value={form.phone}
                          onChange={set("phone")}
                          onBlur={() => touch("phone")}
                        />
                        <FieldError k="phone" />
                        {!errors.phone && form.phone && touched.has("phone") && (
                          <p className="text-[0.65rem] text-[#00e676] mt-1 flex items-center gap-1">
                            <CheckCircle size={10} />Valid mobile number
                          </p>
                        )}
                      </div>

                      <div>
                        <label className={lbl}>Email Address</label>
                        <input
                          className={inp("email")} style={sty("email")}
                          type="email"
                          placeholder="name@company.com"
                          value={form.email}
                          onChange={set("email")}
                          onBlur={() => touch("email")}
                        />
                        <FieldError k="email" />
                      </div>

                      <div className="col-span-2">
                        <label className={lbl}>Notes</label>
                        <textarea
                          className={inp("notes")} style={sty("notes")}
                          rows={2}
                          placeholder="Any additional notes about this employee…"
                          value={form.notes}
                          onChange={set("notes")}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Submit */}
                  <div className="pt-1 space-y-2">
                    <Button
                      variant="primary" size="lg" className="w-full"
                      type="submit"
                      disabled={status === "submitting"}
                    >
                      {status === "submitting"
                        ? <><Loader2 size={15} className="animate-spin" /> Registering Employee…</>
                        : <><UserPlus size={15} /> Register Employee</>}
                    </Button>

                    {/* Pre-submit checklist */}
                    <div className="grid grid-cols-2 gap-1.5 pt-1">
                      {[
                        { key: "photo",       label: "Face photo",       ok: !!captured },
                        { key: "name",        label: "Full name",         ok: !!form.name.trim() && !errors.name },
                        { key: "employee_id", label: "Employee ID",      ok: !!form.employee_id.trim() && !errors.employee_id },
                        { key: "gender",      label: "Gender",           ok: !!form.gender },
                        { key: "department",  label: "Department",       ok: !!form.department },
                        { key: "position",    label: "Position",         ok: !!form.position },
                        { key: "phone",       label: "Phone (10 digits)", ok: !!form.phone && !errors.phone },
                      ].map(({ key, label, ok }) => (
                        <div key={key} className="flex items-center gap-1.5 text-[0.65rem]">
                          {ok
                            ? <CheckCircle size={11} className="text-[#00e676] shrink-0" />
                            : <XCircle    size={11} className="text-[#3a5570] shrink-0" />}
                          <span className={ok ? "text-[#4a9a70]" : "text-[#3a5570]"}>{label}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                </CardContent>
              </Card>
            </div>

          </div>
        </form>
      </div>
    </>
  );
}
