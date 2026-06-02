"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Eye, EyeOff, Shield, Lock, User, Loader2,
  AlertCircle, CheckCircle, XCircle, Info,
} from "lucide-react";

// ── Validation rules ──────────────────────────────────────────────────────────

type FieldErrors = { username?: string; password?: string };

const USERNAME_RULES = {
  required:   (v: string) => v.length > 0                      || "Username is required.",
  minLen:     (v: string) => v.length >= 3                     || "Must be at least 3 characters.",
  maxLen:     (v: string) => v.length <= 30                    || "Must be 30 characters or fewer.",
  startsLetter:(v: string) => /^[a-zA-Z]/.test(v)             || "Must start with a letter.",
  chars:      (v: string) => /^[a-zA-Z0-9_-]+$/.test(v)      || "Only letters, digits, _ and - allowed. No spaces.",
};

const PASSWORD_RULES = [
  { id: "len",     label: "8–64 characters",          test: (p: string) => p.length >= 8 && p.length <= 64 },
  { id: "upper",   label: "One uppercase letter (A–Z)",test: (p: string) => /[A-Z]/.test(p) },
  { id: "lower",   label: "One lowercase letter (a–z)",test: (p: string) => /[a-z]/.test(p) },
  { id: "digit",   label: "One digit (0–9)",           test: (p: string) => /[0-9]/.test(p) },
  { id: "special", label: "One special character (!@#$%…)", test: (p: string) => /[!@#$%^&*()\-_=+\[\]{};':"\\|,.<>/?`~]/.test(p) },
  { id: "noSpace", label: "No whitespace",             test: (p: string) => !/\s/.test(p) },
];

function validateUsername(v: string): string {
  for (const rule of Object.values(USERNAME_RULES)) {
    const result = rule(v);
    if (result !== true) return result as string;
  }
  return "";
}

function validatePassword(v: string): string {
  if (!v) return "Password is required.";
  const failing = PASSWORD_RULES.filter(r => !r.test(v));
  if (failing.length === 0) return "";
  return failing[0].label + " required.";
}

function passwordStrength(p: string): { score: number; label: string; color: string } {
  if (!p) return { score: 0, label: "", color: "" };
  const passed = PASSWORD_RULES.filter(r => r.test(p)).length;
  if (passed <= 2) return { score: 1, label: "Weak",        color: "#ff4d6d" };
  if (passed <= 3) return { score: 2, label: "Fair",        color: "#ffab40" };
  if (passed <= 4) return { score: 3, label: "Good",        color: "#00c8ff" };
  if (passed <= 5) return { score: 4, label: "Strong",      color: "#00e676" };
  return              { score: 5, label: "Very Strong",  color: "#00e676" };
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function LoginPage() {
  const router       = useRouter();
  const searchParams = useSearchParams();
  const userRef      = useRef<HTMLInputElement>(null);

  const [form,      setForm]      = useState({ username: "", password: "" });
  const [touched,   setTouched]   = useState({ username: false, password: false });
  const [showPass,  setShowPass]  = useState(false);
  const [showRules, setShowRules] = useState(false);
  const [loading,   setLoading]   = useState(false);
  const [success,   setSuccess]   = useState(false);
  const [apiError,  setApiError]  = useState("");
  const [attempts,  setAttempts]  = useState(0);
  const [locked,    setLocked]    = useState(false);
  const [lockSecs,  setLockSecs]  = useState(0);

  const uErr  = touched.username ? validateUsername(form.username) : "";
  const pErr  = touched.password ? validatePassword(form.password) : "";
  const pStr  = passwordStrength(form.password);
  const isValid = !validateUsername(form.username) && !validatePassword(form.password);

  // Lockout countdown
  useEffect(() => {
    if (!locked) return;
    const t = setInterval(() => {
      setLockSecs(s => {
        if (s <= 1) { setLocked(false); clearInterval(t); return 0; }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(t);
  }, [locked]);

  useEffect(() => { userRef.current?.focus(); }, []);

  const touch = (field: "username" | "password") =>
    setTouched(t => ({ ...t, [field]: true }));

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched({ username: true, password: true });
    if (!isValid || locked) return;

    setLoading(true); setApiError("");
    try {
      const res  = await fetch("/api/auth/login", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(form),
      });
      const data = await res.json();

      if (res.ok && data.success) {
        setSuccess(true);
        setTimeout(() => {
          router.push(searchParams.get("from") || "/");
          router.refresh();
        }, 800);
        return;
      }

      const next = attempts + 1;
      setAttempts(next);
      setApiError(data.message || "Invalid credentials.");
      setForm(f => ({ ...f, password: "" }));
      setTouched(t => ({ ...t, password: false }));

      if (next >= 5) {
        setLocked(true); setLockSecs(30);
        setApiError("Too many failed attempts. Locked for 30 seconds.");
      }
    } catch {
      setApiError("Connection error. Please check your network and try again.");
    }
    setLoading(false);
  }, [form, isValid, locked, attempts, router, searchParams]);

  // ── Styles ──────────────────────────────────────────────────────────────────
  const baseInp = "w-full pl-10 pr-10 py-3 rounded-xl text-sm font-medium transition-all duration-200 focus:outline-none text-[#e0eeff] placeholder-[#2a4a60]";
  const inpStyle = (err: string, ok: boolean) => ({
    background:  "rgba(0,200,255,0.05)",
    border: err ? "1px solid rgba(255,77,109,0.60)"
          : ok  ? "1px solid rgba(0,230,118,0.55)"
          :       "1px solid rgba(0,200,255,0.22)",
    boxShadow: err ? "0 0 0 3px rgba(255,77,109,0.08)"
             : ok  ? "0 0 0 3px rgba(0,230,118,0.06)"
             :       "none",
  } as React.CSSProperties);

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden"
         style={{ background: "#040810" }}>

      {/* Ambient glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full"
             style={{ background:"radial-gradient(circle,rgba(0,200,255,0.10),transparent)", filter:"blur(80px)" }} />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 rounded-full"
             style={{ background:"radial-gradient(circle,rgba(123,97,255,0.08),transparent)", filter:"blur(80px)" }} />
      </div>

      {/* Grid */}
      <div className="absolute inset-0 opacity-[0.025] pointer-events-none"
           style={{ backgroundImage:"linear-gradient(rgba(0,200,255,0.6) 1px,transparent 1px),linear-gradient(90deg,rgba(0,200,255,0.6) 1px,transparent 1px)", backgroundSize:"60px 60px" }} />

      <div className="relative w-full max-w-md mx-4 z-10">
        <div className="rounded-2xl p-8"
             style={{ background:"rgba(8,18,36,0.94)", border:"1px solid rgba(0,200,255,0.18)", boxShadow:"0 32px 80px rgba(0,0,0,0.60)", backdropFilter:"blur(20px)" }}>

          {/* Logo */}
          <div className="text-center mb-7">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-3"
                 style={{ background:"linear-gradient(135deg,rgba(0,200,255,0.15),rgba(123,97,255,0.15))", border:"1px solid rgba(0,200,255,0.28)" }}>
              <Shield size={28} className="text-[#00c8ff]" />
            </div>
            <h1 className="text-2xl font-black tracking-widest text-[#e0eeff]"
                style={{ fontFamily:"Orbitron,sans-serif" }}>AI VISION</h1>
            <p className="text-[0.68rem] tracking-[0.20em] text-[#2a5570] uppercase mt-1">Enterprise Face Recognition</p>
            <div className="flex items-center justify-center gap-1.5 mt-2.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#00e676]" style={{ animation:"blink 1.4s ease-in-out infinite" }} />
              <span className="text-[0.60rem] font-semibold text-[#00e676] tracking-widest uppercase">System Online</span>
            </div>
          </div>

          {/* Banner */}
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl mb-5"
               style={{ background:"rgba(123,97,255,0.08)", border:"1px solid rgba(123,97,255,0.22)" }}>
            <Lock size={12} className="text-[#7b61ff] shrink-0" />
            <p className="text-[0.70rem] text-[#8a7acc]">
              <span className="font-bold text-[#a390ff]">Admin access required.</span> Authorised personnel only.
            </p>
          </div>

          <form onSubmit={handleSubmit} noValidate className="space-y-4">

            {/* ── Username ──────────────────────────────────────────────── */}
            <div>
              <label className="block text-[0.68rem] font-bold text-[#4a7a9a] uppercase tracking-wide mb-1.5">
                Username
              </label>
              <div className="relative">
                <User size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#2a5570] pointer-events-none" />
                <input
                  ref={userRef}
                  type="text"
                  placeholder="Enter username"
                  autoComplete="username"
                  maxLength={30}
                  value={form.username}
                  onChange={e => {
                    setForm(f => ({ ...f, username: e.target.value }));
                    setApiError("");
                  }}
                  onBlur={() => touch("username")}
                  disabled={loading || success || locked}
                  className={baseInp}
                  style={inpStyle(uErr, touched.username && !uErr && !!form.username)}
                />
                {touched.username && form.username && (
                  <span className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none">
                    {uErr ? <XCircle size={14} className="text-[#ff4d6d]" /> : <CheckCircle size={14} className="text-[#00e676]" />}
                  </span>
                )}
              </div>
              {uErr && (
                <p className="flex items-center gap-1.5 text-[0.65rem] text-[#ff4d6d] mt-1.5">
                  <XCircle size={10} className="shrink-0" />{uErr}
                </p>
              )}
              {!uErr && touched.username && form.username && (
                <p className="flex items-center gap-1.5 text-[0.65rem] text-[#00e676] mt-1.5">
                  <CheckCircle size={10} className="shrink-0" />Username looks good
                </p>
              )}
              <p className="text-[0.60rem] text-[#1e3a50] mt-1">
                3–30 characters · letters, digits, _ and - only · must start with a letter
              </p>
            </div>

            {/* ── Password ──────────────────────────────────────────────── */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-[0.68rem] font-bold text-[#4a7a9a] uppercase tracking-wide">
                  Password
                </label>
                <button type="button" className="flex items-center gap-1 text-[0.60rem] text-[#2a5570] hover:text-[#00c8ff] transition-colors"
                        onClick={() => setShowRules(v => !v)}>
                  <Info size={10} />{showRules ? "Hide" : "Show"} requirements
                </button>
              </div>
              <div className="relative">
                <Lock size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#2a5570] pointer-events-none" />
                <input
                  type={showPass ? "text" : "password"}
                  placeholder="Enter password"
                  autoComplete="current-password"
                  maxLength={64}
                  value={form.password}
                  onChange={e => {
                    setForm(f => ({ ...f, password: e.target.value }));
                    setApiError("");
                  }}
                  onBlur={() => touch("password")}
                  onFocus={() => setShowRules(true)}
                  disabled={loading || success || locked}
                  className={baseInp}
                  style={inpStyle(pErr, touched.password && !pErr && !!form.password)}
                />
                <button
                  type="button"
                  tabIndex={-1}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#2a5570] hover:text-[#8ab0cc] transition-colors"
                  onClick={() => setShowPass(v => !v)}
                >{showPass ? <EyeOff size={14} /> : <Eye size={14} />}</button>
              </div>

              {/* Strength bar */}
              {form.password && (
                <div className="mt-2 space-y-1">
                  <div className="flex gap-1">
                    {[1,2,3,4,5].map(i => (
                      <div key={i} className="h-1 flex-1 rounded-full transition-all duration-300"
                           style={{ background: i <= pStr.score ? pStr.color : "rgba(255,255,255,0.08)" }} />
                    ))}
                  </div>
                  {pStr.label && (
                    <p className="text-[0.62rem] font-bold" style={{ color: pStr.color }}>
                      Strength: {pStr.label}
                    </p>
                  )}
                </div>
              )}

              {pErr && touched.password && (
                <p className="flex items-center gap-1.5 text-[0.65rem] text-[#ff4d6d] mt-1.5">
                  <XCircle size={10} className="shrink-0" />{pErr}
                </p>
              )}

              {/* Password rules checklist */}
              {showRules && (
                <div className="mt-2.5 rounded-xl p-3 space-y-1.5"
                     style={{ background:"rgba(0,0,0,0.30)", border:"1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[0.58rem] font-bold tracking-widest uppercase text-[#2a4a60] mb-2">
                    Password Requirements
                  </p>
                  {PASSWORD_RULES.map(rule => {
                    const ok = rule.test(form.password);
                    return (
                      <div key={rule.id} className="flex items-center gap-2">
                        {ok
                          ? <CheckCircle size={11} className="text-[#00e676] shrink-0" />
                          : <XCircle    size={11} className="text-[#3a5570] shrink-0" />}
                        <span className={`text-[0.65rem] ${ok ? "text-[#4a8a6a]" : "text-[#3a5070]"}`}>
                          {rule.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* API error */}
            {apiError && (
              <div className="flex items-center gap-2 px-3 py-2.5 rounded-xl"
                   style={{ background:"rgba(255,77,109,0.08)", border:"1px solid rgba(255,77,109,0.28)" }}>
                <AlertCircle size={13} className="text-[#ff4d6d] shrink-0" />
                <span className="text-[0.70rem] text-[#ff4d6d] flex-1">{apiError}</span>
                {locked && <span className="text-[#ff4d6d] font-mono text-xs font-bold">{lockSecs}s</span>}
              </div>
            )}

            {/* Attempt warning */}
            {attempts > 0 && attempts < 5 && !locked && (
              <div className="flex items-center gap-2 px-3 py-2 rounded-xl"
                   style={{ background:"rgba(255,171,64,0.07)", border:"1px solid rgba(255,171,64,0.20)" }}>
                <AlertCircle size={12} className="text-[#ffab40] shrink-0" />
                <p className="text-[0.65rem] text-[#c08030]">
                  {5 - attempts} attempt{5 - attempts !== 1 ? "s" : ""} remaining before 30-second lockout.
                </p>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading || success || locked || (!isValid && touched.username && touched.password)}
              className="w-full py-3 rounded-xl text-sm font-bold tracking-wide transition-all duration-200 mt-1"
              style={{
                background: success
                  ? "linear-gradient(135deg,#00e676,#00c8ff)"
                  : loading
                    ? "rgba(0,200,255,0.20)"
                    : "linear-gradient(135deg,#00c8ff,#7b61ff)",
                boxShadow: success ? "0 4px 24px rgba(0,230,118,0.40)" : "0 4px 24px rgba(0,200,255,0.28)",
                color: "#fff",
                opacity: (locked || (!isValid && touched.username && touched.password)) && !loading && !success ? 0.45 : 1,
              }}
            >
              {success ? (
                <span className="flex items-center justify-center gap-2">
                  <CheckCircle size={16} />Access Granted — Redirecting…
                </span>
              ) : loading ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 size={16} className="animate-spin" />Authenticating…
                </span>
              ) : locked ? (
                `Account locked · ${lockSecs}s`
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <Shield size={15} />Sign In
                </span>
              )}
            </button>

          </form>

          {/* Footer */}
          <div className="mt-6 pt-5 border-t border-white/[0.06] text-center space-y-1">
            <p className="text-[0.60rem] text-[#1e3a50]">AI Vision Enterprise · M.Tech CSE · GIFT Bhubaneswar</p>
            <p className="text-[0.58rem] text-[#142430]">Jyotipriya Panda · Reg. 2407432009</p>
          </div>
        </div>

        <p className="text-center text-[0.58rem] text-[#162838] mt-3">
          🔒 This system is monitored. Unauthorised access is prohibited.
        </p>
      </div>

      <style>{`
        @keyframes blink {
          0%,100% { opacity:1; box-shadow:0 0 6px #00e676; }
          50%      { opacity:0.3; box-shadow:none; }
        }
      `}</style>
    </div>
  );
}
