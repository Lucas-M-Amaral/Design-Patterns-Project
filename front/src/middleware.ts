import NextAuth from "next-auth";
import { authConfig } from "@/auth.config";
import {
  PUBLIC_ROUTES,
  ROOT,
  UNAUTHORIZED,
} from "@/lib/routes";

const { auth } = NextAuth(authConfig);

export default auth((req) => {
  const { nextUrl, auth } = req;

  const isAuthenticated = !!req.auth;
  const isPublicRoute = PUBLIC_ROUTES.includes(nextUrl.pathname);

  if (!isAuthenticated && !isPublicRoute)
    return Response.redirect(new URL(ROOT, nextUrl));

  if (
    isAuthenticated &&
    nextUrl.pathname == "/settings" &&
    auth?.user?.role == 1
  ) {
    return Response.redirect(new URL(UNAUTHORIZED, nextUrl));
  }
});

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
