import { NextRequest, NextResponse } from "next/server";
import { readCredentials, isValidUsername, isValidPassword } from "@/lib/credentials";

export const runtime = "nodejs";   // better-sqlite3 requires Node.js runtime

const COOKIE = "aivision_admin";

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  if (!body) {
    return NextResponse.json({ success: false, message: "Invalid request body." }, { status: 400 });
  }

  const { username = "", password = "" } = body as { username?: string; password?: string };

  if (!isValidUsername(username)) {
    return NextResponse.json({ success: false, message: "Username format is invalid." }, { status: 422 });
  }
  if (!isValidPassword(password)) {
    return NextResponse.json({ success: false, message: "Password does not meet security requirements." }, { status: 422 });
  }

  const creds = readCredentials();
  if (username === creds.username && password === creds.password) {
    const res = NextResponse.json({ success: true, message: "Login successful" });
    res.cookies.set(COOKIE, "authenticated", {
      httpOnly: true,
      sameSite: "strict",
      path:     "/",
      maxAge:   60 * 60 * 8,
    });
    return res;
  }

  return NextResponse.json({ success: false, message: "Invalid username or password." }, { status: 401 });
}
