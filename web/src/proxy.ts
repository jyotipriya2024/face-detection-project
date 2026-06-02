import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const SESSION_COOKIE = "aivision_admin";
const SESSION_VALUE  = "authenticated";

// Only these paths are fully public (no session required)
const PUBLIC_PATHS = [
  "/login",
  "/api/auth/login",
  "/api/auth/logout",
];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow Next.js internals through
  if (pathname.startsWith("/_next") || pathname.startsWith("/favicon")) {
    return NextResponse.next();
  }

  // Allow explicit public paths
  if (PUBLIC_PATHS.some(p => pathname === p || pathname.startsWith(p + "/"))) {
    return NextResponse.next();
  }

  const session       = request.cookies.get(SESSION_COOKIE);
  const isAuthenticated = session?.value === SESSION_VALUE;

  // Not authenticated → redirect to login
  if (!isAuthenticated) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Already logged in trying to visit /login → send to dashboard
  if (isAuthenticated && pathname === "/login") {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
