"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { exchangeOAuthCode } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";

const STORAGE_PREFIX = "flowtab_oauth_state:";

type Provider = "google" | "github" | "facebook";

function isProvider(v: string | null): v is Provider {
  return v === "google" || v === "github" || v === "facebook";
}

export default function OAuthCallbackClient() {
  const router = useRouter();
  const params = useSearchParams();
  const { completeLogin } = useAuth();

  useEffect(() => {
    const code = params.get("code");
    const state = params.get("state");
    const provider = params.get("provider");

    if (!code || !state || !isProvider(provider)) {
      toast.error("Invalid OAuth callback.");
      router.replace("/login");
      return;
    }

    const key = `${STORAGE_PREFIX}${state}`;
    const raw = sessionStorage.getItem(key);
    if (!raw) {
      toast.error("OAuth state expired. Please try again.");
      router.replace("/login");
      return;
    }

    sessionStorage.removeItem(key);

    let stored: { redirect_uri: string; code_verifier: string };
    try {
      stored = JSON.parse(raw);
    } catch {
      toast.error("OAuth state invalid. Please try again.");
      router.replace("/login");
      return;
    }

    (async () => {
      try {
        const res = await exchangeOAuthCode(provider, {
          code,
          state,
          redirect_uri: stored.redirect_uri,
          code_verifier: stored.code_verifier,
        });

        await completeLogin(res.access_token);
        toast.success("Logged in successfully");
        router.replace("/library");
        router.refresh();
      } catch (e) {
        console.error(e);
        toast.error("OAuth login failed.");
        router.replace("/login");
      }
    })();
  }, [completeLogin, params, router]);

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] px-4">
      <div className="text-sm text-muted-foreground">Completing sign-in...</div>
    </div>
  );
}
