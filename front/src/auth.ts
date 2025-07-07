import NextAuth, { DefaultSession } from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { authConfig } from "./auth.config";
import { JWT } from "next-auth/jwt";
import { authUser } from "./service/auth";

declare module "next-auth/jwt" {
  interface JWT {
    role?: number;
  }
}

declare module "next-auth" {
  interface Session {
    user: {
      role?: number;
    } & DefaultSession["user"];
  }
  interface User {
    role?: number;
  }
}

async function getUser(document: string, password: string): Promise<any> {
  return authUser(document, password);
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  ...authConfig,
  providers: [
    Credentials({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials, req) {
        const user = await getUser(
          credentials.username as string,
          credentials.password as string,
        );

        return user ?? null;
      },
    }),
  ],
});
