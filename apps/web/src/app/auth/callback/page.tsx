import { Suspense } from "react";

import OAuthCallbackClient from "./OAuthCallbackClient";

export default function OAuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] px-4">
          <div className="text-sm text-muted-foreground">Completing sign-in...</div>
        </div>
      }
    >
      <OAuthCallbackClient />
    </Suspense>
  );
}
