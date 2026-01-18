"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { toast } from "sonner";
import { startOAuth, type OAuthProvider } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isOAuthLoading, setIsOAuthLoading] = useState<OAuthProvider | null>(null);
  const { login } = useAuth();

  const startProviderOAuth = async (provider: OAuthProvider) => {
    if (isOAuthLoading) return;

    try {
      setIsOAuthLoading(provider);

      const redirectUri = `${window.location.origin}/auth/callback?provider=${provider}`;
      const res = await startOAuth(provider, redirectUri);

      const key = `flowtab_oauth_state:${res.state}`;
      sessionStorage.setItem(
        key,
        JSON.stringify({ redirect_uri: redirectUri, code_verifier: res.code_verifier })
      );

      window.location.href = res.authorize_url;
    } catch (e) {
      console.error(e);
      toast.error("Failed to start OAuth login.");
    } finally {
      setIsOAuthLoading(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      toast.success("Logged in successfully");
    } catch (error) {
      toast.error("Failed to login. Please check your credentials.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] px-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Login</CardTitle>
          <CardDescription>
            Enter your email below to login to your account
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="grid gap-4">
            <div className="grid gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => startProviderOAuth("google")}
                disabled={isOAuthLoading !== null}
              >
                {isOAuthLoading === "google" ? "Connecting..." : "Continue with Google"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => startProviderOAuth("github")}
                disabled={isOAuthLoading !== null}
              >
                {isOAuthLoading === "github" ? "Connecting..." : "Continue with GitHub"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => startProviderOAuth("facebook")}
                disabled={isOAuthLoading !== null}
              >
                {isOAuthLoading === "facebook" ? "Connecting..." : "Continue with Facebook"}
              </Button>
            </div>

            <div className="flex items-center gap-3">
              <div className="h-px flex-1 bg-border" />
              <div className="text-xs text-muted-foreground">or</div>
              <div className="h-px flex-1 bg-border" />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <div className="flex items-center">
                <Label htmlFor="password">Password</Label>
              </div>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-4">
            <Button className="w-full" type="submit" disabled={isLoading}>
              {isLoading ? "Logging in..." : "Login"}
            </Button>
            <div className="text-center text-sm text-muted-foreground">
              Don&apos;t have an account?{" "}
              <Link href="/register" className="underline underline-offset-4 hover:text-primary">
                Sign up
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
