"""Full change-password API test using Python requests."""
import requests

BASE = "http://localhost:3000"

# ── Login ─────────────────────────────────────────────────────────────────────
r = requests.post(f"{BASE}/api/auth/login",
                  json={"username":"admin","password":"Admin@123"})
assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
session_cookie = r.cookies.get("aivision_admin")
print(f"PASS Login 200  cookie={session_cookie}\n")

cookies = {"aivision_admin": session_cookie}

def chk(label, body, expect):
    r = requests.post(f"{BASE}/api/auth/change-password",
                      json=body, cookies=cookies)
    ok  = r.status_code == expect
    msg = r.json().get("message","") if r.headers.get("content-type","").startswith("application/json") else r.text[:80]
    print(f"{'PASS' if ok else 'FAIL'} [{r.status_code}] {label}  ->  {msg}")
    return r.status_code

chk("1. Wrong current password",    {"currentPassword":"WrongPass1!","newPassword":"Valid@999X","confirmPassword":"Valid@999X"},  401)
chk("2. Same as current",           {"currentPassword":"Admin@123","newPassword":"Admin@123","confirmPassword":"Admin@123"},      422)
chk("3. Confirm mismatch",          {"currentPassword":"Admin@123","newPassword":"Valid@999X","confirmPassword":"Valid@888X"},    422)
chk("4. Weak (no uppercase)",       {"currentPassword":"Admin@123","newPassword":"weakpass1!","confirmPassword":"weakpass1!"},    422)
chk("5. No special character",      {"currentPassword":"Admin@123","newPassword":"ValidPass1A","confirmPassword":"ValidPass1A"}, 422)
chk("6. Bad username (starts '1')", {"currentPassword":"Admin@123","newUsername":"1admin","newPassword":"Valid@999X","confirmPassword":"Valid@999X"}, 422)

print()
chk("7. Valid change -> NewPass@1",  {"currentPassword":"Admin@123","newPassword":"NewPass@1","confirmPassword":"NewPass@1"},     200)

# ── Verify SQLite ─────────────────────────────────────────────────────────────
import sqlite3
db_path = r"d:\Users\dibya\jyoti\face-detection-project\web\auth.db"
conn = sqlite3.connect(db_path)
row  = conn.execute("SELECT username, password, updated_at FROM admin_credentials WHERE id=1").fetchone()
conn.close()
print(f"\nSQLite: username={row[0]}  password={row[1]}  updated_at={row[2]}")
assert row[1] == "NewPass@1", f"DB not updated! Got: {row[1]}"
print("PASS SQLite updated correctly\n")

# ── Login with new password ───────────────────────────────────────────────────
r2 = requests.post(f"{BASE}/api/auth/login",
                   json={"username":"admin","password":"NewPass@1"})
print(f"{'PASS' if r2.status_code==200 else 'FAIL'} Login NewPass@1: {r2.status_code}")
session2 = r2.cookies.get("aivision_admin")

# ── Restore Admin@123 ─────────────────────────────────────────────────────────
r3 = requests.post(f"{BASE}/api/auth/change-password",
                   json={"currentPassword":"NewPass@1","newPassword":"Admin@123","confirmPassword":"Admin@123"},
                   cookies={"aivision_admin": session2})
print(f"{'PASS' if r3.status_code==200 else 'FAIL'} Restore Admin@123: {r3.status_code}  {r3.json().get('message','')}")

# Confirm restored
conn = sqlite3.connect(db_path)
final = conn.execute("SELECT password FROM admin_credentials WHERE id=1").fetchone()
conn.close()
print(f"PASS Final password in DB: {final[0]}")
