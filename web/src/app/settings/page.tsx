"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Topbar from "@/components/Topbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  Lock, Eye, EyeOff, CheckCircle, XCircle, AlertCircle,
  Loader2, ShieldCheck, User, KeyRound,
} from "lucide-react";

// ── Shared validation (mirrors server) ───────────────────────────────────────

const USERNAME_RULES: { id: string; label: string; test: (v: string) => boolean }[] = [
  { id:"required",    label:"Required",                            test: v => v.length > 0 },
  { id:"minLen",      label:"3–30 characters",                     test: v => v.length >= 3 && v.length <= 30 },
  { id:"startsLetter",label:"Must start with a letter",            test: v => /^[a-zA-Z]/.test(v) },
  { id:"chars",       label:"Only letters, digits, _ and - allowed",test: v => /^[a-zA-Z0-9_-]+$/.test(v) },
];

const PASSWORD_RULES: { id: string; label: string; test: (v: string) => boolean }[] = [
  { id:"len",     label:"8–64 characters",               test: p => p.length >= 8 && p.length <= 64 },
  { id:"upper",   label:"At least one uppercase (A–Z)",  test: p => /[A-Z]/.test(p) },
  { id:"lower",   label:"At least one lowercase (a–z)",  test: p => /[a-z]/.test(p) },
  { id:"digit",   label:"At least one digit (0–9)",      test: p => /[0-9]/.test(p) },
  { id:"special", label:"At least one special character", test: p => /[!@#$%^&*()\-_=+\[\]{};':"\\|,.<>/?`~]/.test(p) },
  { id:"noSpace", label:"No whitespace allowed",          test: p => !/\s/.test(p) },
];

function passesAll(v: string, rules: typeof PASSWORD_RULES) {
  return rules.every(r => r.test(v));
}

function strength(p: string) {
  const n = PASSWORD_RULES.filter(r => r.test(p)).length;
  if (!p)  return { score:0, label:"",           color:"" };
  if (n<=2) return { score:1, label:"Weak",       color:"#ff4d6d" };
  if (n<=3) return { score:2, label:"Fair",       color:"#ffab40" };
  if (n<=4) return { score:3, label:"Good",       color:"#00c8ff" };
  if (n<=5) return { score:4, label:"Strong",     color:"#00e676" };
  return     { score:5, label:"Very Strong", color:"#00e676" };
}

type FieldKey = "currentPassword" | "newUsername" | "newPassword" | "confirmPassword";

// ── Component ─────────────────────────────────────────────────────────────────

export default function SettingsPage() {
  const router = useRouter();

  const [form, setForm] = useState({
    currentPassword: "", newUsername: "", newPassword: "", confirmPassword: "",
  });
  const [show,    setShow]    = useState({ current:false, new:false, confirm:false });
  const [touched, setTouched] = useState<Set<FieldKey>>(new Set());
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [apiErr,  setApiErr]  = useState<{ message:string; field?:string } | null>(null);

  const touch = (k: FieldKey) => setTouched(p => new Set(p).add(k));

  const fieldErr = (k: FieldKey): string => {
    if (!touched.has(k)) return "";
    const v = form[k];
    if (k === "currentPassword") return v ? "" : "Current password is required.";
    if (k === "newUsername")     return v ? (passesAll(v, USERNAME_RULES as typeof PASSWORD_RULES) ? "" : "Invalid username format.") : "";
    if (k === "newPassword")     return passesAll(v, PASSWORD_RULES) ? "" : "Password does not meet requirements.";
    if (k === "confirmPassword") return v === form.newPassword ? "" : "Passwords do not match.";
    return "";
  };

  const canSubmit =
    !!form.currentPassword &&
    passesAll(form.newPassword, PASSWORD_RULES) &&
    form.newPassword === form.confirmPassword &&
    form.newPassword !== form.currentPassword &&
    (!form.newUsername || passesAll(form.newUsername, USERNAME_RULES as typeof PASSWORD_RULES));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(new Set(["currentPassword","newUsername","newPassword","confirmPassword"] as FieldKey[]));
    if (!canSubmit) return;

    setLoading(true); setApiErr(null);
    try {
      const res  = await fetch("/api/auth/change-password", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(form),
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess(true);
        // Force re-login with new credentials
        setTimeout(async () => {
          await fetch("/api/auth/logout", { method:"POST" });
          router.push("/login");
        }, 2000);
      } else {
        setApiErr({ message: data.message, field: data.field });
      }
    } catch {
      setApiErr({ message: "Connection error. Please try again." });
    }
    setLoading(false);
  };

  const pStr = strength(form.newPassword);

  // ── Input style helpers ────────────────────────────────────────────────────
  const inp = (k: FieldKey) => {
    const err = fieldErr(k) || (apiErr?.field === k ? apiErr.message : "");
    const ok  = touched.has(k) && !err && !!form[k];
    return {
      className: "w-full pl-10 pr-10 py-2.5 rounded-lg text-sm text-[#e0eeff] placeholder-[#3a5570] focus:outline-none focus:ring-1 transition-all",
      style: {
        background: "rgba(0,200,255,0.05)",
        border: err ? "1px solid rgba(255,77,109,0.55)" : ok ? "1px solid rgba(0,230,118,0.50)" : "1px solid rgba(0,200,255,0.20)",
        focusRingColor: err ? "#ff4d6d" : "#00c8ff",
      } as React.CSSProperties,
    };
  };

  const lbl = "block text-[0.68rem] font-bold text-[#4a7a9a] uppercase tracking-wide mb-1.5";

  const FieldMsg = ({ k }: { k: FieldKey }) => {
    const err = fieldErr(k) || (apiErr?.field === k ? apiErr.message : "");
    const ok  = touched.has(k) && !err && !!form[k];
    if (err) return <p className="flex items-center gap-1 text-[0.65rem] text-[#ff4d6d] mt-1.5"><XCircle size={10} />{err}</p>;
    if (ok)  return <p className="flex items-center gap-1 text-[0.65rem] text-[#00e676] mt-1.5"><CheckCircle size={10} />Looks good</p>;
    return null;
  };

  const IconEnd = ({ k }: { k: FieldKey }) => {
    const err = fieldErr(k);
    const ok  = touched.has(k) && !err && !!form[k];
    if (!touched.has(k) || !form[k]) return null;
    return err ? <XCircle size={14} className="text-[#ff4d6d]" /> : ok ? <CheckCircle size={14} className="text-[#00e676]" /> : null;
  };

  return (
    <>
      <Topbar title="Settings" subtitle="Manage admin credentials" />
      <div className="px-6 py-5 max-w-3xl mx-auto space-y-5">

        {/* Success state */}
        {success && (
          <div className="flex items-center gap-3 p-4 rounded-xl"
               style={{ background:"rgba(0,230,118,0.10)", border:"1px solid rgba(0,230,118,0.30)" }}>
            <ShieldCheck size={22} className="text-[#00e676] shrink-0" />
            <div>
              <p className="font-bold text-[#00e676]">Password changed successfully!</p>
              <p className="text-sm text-[#3a7a5a] mt-0.5">Signing out — please log in with your new credentials…</p>
            </div>
          </div>
        )}

        {/* Current credentials info */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Admin Account</CardTitle>
              <Badge variant="success"><ShieldCheck size={10} className="mr-0.5" />Active Session</Badge>
            </div>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3">
            {[
              { icon:<User size={14}/>,     label:"Username",   value:"admin",         color:"#00c8ff" },
              { icon:<KeyRound size={14}/>, label:"Last changed",value:"See settings below", color:"#8ab0cc" },
            ].map(({ icon, label, value, color }) => (
              <div key={label} className="flex items-center gap-3 px-3 py-2.5 rounded-lg"
                   style={{ background:"rgba(0,200,255,0.04)", border:"1px solid rgba(0,200,255,0.10)" }}>
                <span style={{ color }}>{icon}</span>
                <div>
                  <p className="text-[0.60rem] uppercase tracking-wide text-[#2a5570]">{label}</p>
                  <p className="text-sm font-semibold" style={{ color }}>{value}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Change password form */}
        <Card>
          <CardHeader><CardTitle>Change Password</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} noValidate className="space-y-5">

              {/* Current password */}
              <div>
                <label className={lbl}>Current Password *</label>
                <div className="relative">
                  <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#2a5570] pointer-events-none" />
                  <input
                    type={show.current ? "text" : "password"}
                    placeholder="Enter your current password"
                    autoComplete="current-password"
                    {...inp("currentPassword")}
                    value={form.currentPassword}
                    onChange={e => { setForm(f=>({...f,currentPassword:e.target.value})); setApiErr(null); }}
                    onBlur={() => touch("currentPassword")}
                    disabled={loading || success}
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5">
                    <IconEnd k="currentPassword" />
                    <button type="button" tabIndex={-1} className="text-[#2a5570] hover:text-[#8ab0cc]"
                            onClick={() => setShow(s=>({...s,current:!s.current}))}>
                      {show.current ? <EyeOff size={14}/> : <Eye size={14}/>}
                    </button>
                  </div>
                </div>
                <FieldMsg k="currentPassword" />
              </div>

              <div className="border-t border-white/[0.06]" />

              {/* New username (optional) */}
              <div>
                <label className={lbl}>New Username <span className="text-[#3a5570] font-normal normal-case tracking-normal">(optional — leave blank to keep current)</span></label>
                <div className="relative">
                  <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#2a5570] pointer-events-none" />
                  <input
                    type="text"
                    placeholder="admin"
                    autoComplete="username"
                    maxLength={30}
                    {...inp("newUsername")}
                    value={form.newUsername}
                    onChange={e => { setForm(f=>({...f,newUsername:e.target.value})); setApiErr(null); }}
                    onBlur={() => form.newUsername && touch("newUsername")}
                    disabled={loading || success}
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2"><IconEnd k="newUsername" /></div>
                </div>
                <FieldMsg k="newUsername" />
                <p className="text-[0.60rem] text-[#1e3a50] mt-1">3–30 chars · letters, digits, _ - · must start with a letter</p>
              </div>

              {/* New password */}
              <div>
                <label className={lbl}>New Password *</label>
                <div className="relative">
                  <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#2a5570] pointer-events-none" />
                  <input
                    type={show.new ? "text" : "password"}
                    placeholder="Enter new password"
                    autoComplete="new-password"
                    maxLength={64}
                    {...inp("newPassword")}
                    value={form.newPassword}
                    onChange={e => { setForm(f=>({...f,newPassword:e.target.value})); setApiErr(null); }}
                    onBlur={() => touch("newPassword")}
                    disabled={loading || success}
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5">
                    <IconEnd k="newPassword" />
                    <button type="button" tabIndex={-1} className="text-[#2a5570] hover:text-[#8ab0cc]"
                            onClick={() => setShow(s=>({...s,new:!s.new}))}>
                      {show.new ? <EyeOff size={14}/> : <Eye size={14}/>}
                    </button>
                  </div>
                </div>

                {/* Strength bar */}
                {form.newPassword && (
                  <div className="mt-2 space-y-1">
                    <div className="flex gap-1">
                      {[1,2,3,4,5].map(i=>(
                        <div key={i} className="h-1.5 flex-1 rounded-full transition-all duration-300"
                             style={{ background: i<=pStr.score ? pStr.color : "rgba(255,255,255,0.08)" }} />
                      ))}
                    </div>
                    {pStr.label && <p className="text-[0.62rem] font-bold" style={{ color:pStr.color }}>Strength: {pStr.label}</p>}
                  </div>
                )}

                <FieldMsg k="newPassword" />

                {/* Rules checklist */}
                {form.newPassword && (
                  <div className="mt-2.5 rounded-xl p-3 grid grid-cols-2 gap-1.5"
                       style={{ background:"rgba(0,0,0,0.25)", border:"1px solid rgba(255,255,255,0.06)" }}>
                    {PASSWORD_RULES.map(r => {
                      const ok = r.test(form.newPassword);
                      return (
                        <div key={r.id} className="flex items-center gap-1.5">
                          {ok ? <CheckCircle size={11} className="text-[#00e676] shrink-0"/> : <XCircle size={11} className="text-[#3a5570] shrink-0"/>}
                          <span className={`text-[0.63rem] ${ok?"text-[#4a8a6a]":"text-[#3a5070]"}`}>{r.label}</span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Confirm password */}
              <div>
                <label className={lbl}>Confirm New Password *</label>
                <div className="relative">
                  <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#2a5570] pointer-events-none" />
                  <input
                    type={show.confirm ? "text" : "password"}
                    placeholder="Re-enter new password"
                    autoComplete="new-password"
                    maxLength={64}
                    {...inp("confirmPassword")}
                    value={form.confirmPassword}
                    onChange={e => { setForm(f=>({...f,confirmPassword:e.target.value})); setApiErr(null); }}
                    onBlur={() => touch("confirmPassword")}
                    disabled={loading || success}
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5">
                    <IconEnd k="confirmPassword" />
                    <button type="button" tabIndex={-1} className="text-[#2a5570] hover:text-[#8ab0cc]"
                            onClick={() => setShow(s=>({...s,confirm:!s.confirm}))}>
                      {show.confirm ? <EyeOff size={14}/> : <Eye size={14}/>}
                    </button>
                  </div>
                </div>
                <FieldMsg k="confirmPassword" />
              </div>

              {/* Same-as-current warning */}
              {form.newPassword && form.newPassword === form.currentPassword && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs text-[#ffab40]"
                     style={{ background:"rgba(255,171,64,0.08)", border:"1px solid rgba(255,171,64,0.22)" }}>
                  <AlertCircle size={13} className="shrink-0" />
                  New password must be different from the current password.
                </div>
              )}

              {/* API error */}
              {apiErr && !apiErr.field && (
                <div className="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm text-[#ff4d6d]"
                     style={{ background:"rgba(255,77,109,0.08)", border:"1px solid rgba(255,77,109,0.28)" }}>
                  <AlertCircle size={14} className="shrink-0" />{apiErr.message}
                </div>
              )}

              <Button variant="primary" size="lg" className="w-full mt-2" type="submit"
                      disabled={loading || success || !canSubmit}>
                {loading
                  ? <><Loader2 size={15} className="animate-spin"/>Updating credentials…</>
                  : <><ShieldCheck size={15}/>Update Password</>}
              </Button>

              <p className="text-center text-[0.65rem] text-[#2a4a60]">
                After saving, you will be signed out and must log in with the new password.
              </p>
            </form>
          </CardContent>
        </Card>

      </div>
    </>
  );
}
