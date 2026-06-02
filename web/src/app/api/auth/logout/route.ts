import { NextResponse } from "next/server";

export async function POST() {
  const res = NextResponse.json({ success: true });
  res.cookies.set("aivision_admin", "", {
    httpOnly: true,
    sameSite: "strict",
    path:     "/",
    maxAge:   0,  // expire immediately
  });
  return res;
}
