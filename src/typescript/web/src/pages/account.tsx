import { SignedIn, useAuth, UserProfile } from "@clerk/nextjs";
import path from "constants/path";
import { useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import { useEffect } from "react";

export default function AccountPage() {
  const { isSignedIn, isLoaded } = useAuth();
  const { replace } = useRouter();
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      replace(path.SEARCH);
    }
  }, [isSignedIn, isLoaded, replace]);

  return (
    <div className="container grid max-w-6xl grid-cols-1 pt-0 m-auto md:py-16">
      <SignedIn>
        <UserProfile
          path={path.ACCOUNT}
          appearance={{
            variables: {
              fontSize: isMobile ? "1rem" : "1.334rem",
            },
          }}
        />
      </SignedIn>
    </div>
  );
}
