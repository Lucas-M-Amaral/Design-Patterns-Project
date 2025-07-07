import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

declare const window: {
  __ENV?: any;
};

export const getEnv = (key: string, defaultValue?: string) => {
  if (typeof window !== "undefined")
    return window.__ENV ? (window.__ENV[key] ?? defaultValue) : undefined;
  if (typeof process === "undefined") return undefined;
  return process.env[key] ?? defaultValue;
};

const baseEnv = {
  client: {
    NEXT_PUBLIC_APP_VERSION: z.string(),
  },
  runtimeEnv: {
    NEXT_PUBLIC_APP_VERSION: getEnv("NEXT_PUBLIC_APP_VERSION"),
  },
  server: {
    BACKEND_API_URL: z.string().url(),
  },
};

const nextAuthEnv = {
  server: {
    AUTH_SECRET: z.string().min(1),
    AUTH_TRUST_HOST: z.string().transform((s) => s !== "false" && s !== "0"),
    AUTH_DEBUG: z.string().transform((s) => s !== "false" && s !== "0"),
  },
};

export const env = createEnv({
  client: {
    ...baseEnv.client,
  },
  server: {
    ...nextAuthEnv.server,
    ...baseEnv.server,
  },
  experimental__runtimeEnv: {
    ...baseEnv.runtimeEnv,
  },
  skipValidation:
    process.env.SKIP_ENV_CHECK === "true" ||
    (typeof window !== "undefined" && window.__ENV === undefined),
  onValidationError(error) {
    console.error("❌ Invalid environment variables:", error);
    throw new Error(`Invalid environment variables: ${JSON.stringify(error)}`);
  },
  onInvalidAccess: (variable: string) => {
    throw new Error(
      `❌ Attempted to access a server-side environment variable on the client: ${variable}`,
    );
  },
});

export default env;
