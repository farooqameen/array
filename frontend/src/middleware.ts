import { NextRequest, NextResponse } from "next/server";

/**
 * Middleware for route protection and authentication-aware redirection.
 *
 * - If a user is authenticated (has `idToken` cookie) and tries to visit `/login`,
 *   they are redirected to the homepage (`/`).
 * - If a user is unauthenticated and attempts to access a protected route,
 *   they are redirected to `/login`.
 * - Public paths (e.g., static assets, API routes) are excluded via `config.matcher`.
 *
 * This approach ensures client security and keeps public/private routes cleanly separated.
 *
 * @param {NextRequest} req - The incoming request object provided by Next.js middleware.
 * @returns {NextResponse} - A redirect response or the unmodified request continuation.
 */
export function middleware(req: NextRequest) {
  const token = req.cookies.get("idToken")?.value;
  const { pathname } = req.nextUrl;

  const isAuthenticated = Boolean(token);
  const isLoginPage = pathname === "/login";

  // Prevent logged-in users from accessing the login page
  if (isAuthenticated && isLoginPage) {
    return NextResponse.redirect(new URL("/", req.url));
  }

  // Protect all non-login, non-static routes
  const isProtectedRoute = !isLoginPage && !pathname.startsWith("/_next");
  if (!isAuthenticated && isProtectedRoute) {
    return NextResponse.redirect(new URL("/login", req.url));
  }

  return NextResponse.next();
}

/**
 * Apply middleware to all routes except:
 * - /api
 * - static files
 * - favicon
 */
export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
