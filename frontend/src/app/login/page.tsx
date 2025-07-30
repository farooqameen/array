import { GalleryVerticalEnd } from "lucide-react";

import { LoginForm } from "@/components/login-form";
import WaveLogo from "@/components/ui/array-logo";

export default function LoginPage() {
  return (
    <div className="bg-muted flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="flex w-full max-w-sm flex-col gap-20">
        <div className="flex items-center gap-2 self-center font-medium">
          <WaveLogo width={200} height={200} />
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
