import { NextRequest, NextResponse } from "next/server";
import { readCredentials, writeCredentials, isValidUsername, isValidPassword } from "@/lib/credentials";

export const runtime = "nodejs";   // better-sqlite3 requires Node.js runtime

export async function POST(req: NextRequest) {
  // Session enforced by proxy.ts; double-check the cookie here too
  const session = req.cookies.get("aivision_admin");
  if (session?.value !== "authenticated") {
    return NextResponse.json({ success: false, message: "Unauthorised. Please log in." }, { status: 401 });
  }

  const body = await req.json().catch(() => null);
  if (!body) {
    return NextResponse.json({ success: false, message: "Invalid request body." }, { status: 400 });
  }

  const {
    currentPassword = "",
    newUsername     = "",
    newPassword     = "",
    confirmPassword = "",
  } = body as {
    currentPassword?: string;
    newUsername?:     string;
    newPassword?:     string;
    confirmPassword?: string;
  };

  if (!currentPassword) {
    return NextResponse.json({ success: false, message: "Current password is required.", field: "currentPassword" }, { status: 422 });
  }

  const creds = readCredentials();

  if (currentPassword !== creds.password) {
    return NextResponse.json({ success: false, message: "Current password is incorrect.", field: "currentPassword" }, { status: 401 });
  }

  if (!newPassword) {
    return NextResponse.json({ success: false, message: "New password is required.", field: "newPassword" }, { status: 422 });
  }

  if (newPassword === currentPassword) {
    return NextResponse.json({ success: false, message: "New password must be different from the current password.", field: "newPassword" }, { status: 422 });
  }

  if (!isValidPassword(newPassword)) {
    return NextResponse.json({ success: false, message: "New password does not meet security requirements.", field: "newPassword" }, { status: 422 });
  }

  if (newPassword !== confirmPassword) {
    return NextResponse.json({ success: false, message: "Passwords do not match.", field: "confirmPassword" }, { status: 422 });
  }

  const targetUsername = newUsername.trim() || creds.username;
  if (!isValidUsername(targetUsername)) {
    return NextResponse.json({ success: false, message: "New username format is invalid.", field: "newUsername" }, { status: 422 });
  }

  writeCredentials(targetUsername, newPassword);

  return NextResponse.json({
    success: true,
    message: "Credentials updated. Please sign in with your new password.",
  });
}
