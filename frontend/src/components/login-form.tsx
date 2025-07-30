"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { motion } from "framer-motion";
import { useState } from "react";
import { signIn } from "@/lib/auth/auth";
import { useAuth } from "@/lib/auth/authStore";
import { storeSessionCookies } from "@/lib/auth/setCookies";
import { useRouter } from "next/navigation";

/**
 * LoginForm Component
 *
 * Renders a login form with email, password, and "Remember Me" support.
 * Handles input validation, authentication via AWS Cognito, session persistence,
 * secure cookie storage, and protected route redirection.
 *
 * @component
 * @example
 * return <LoginForm />;
 *
 * @param {React.ComponentProps<"div">} props - Additional props passed to the wrapper div.
 */
export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [rememberMe, setRememberMe] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  /**
   * Validates the login form inputs.
   *
   * @returns {boolean} True if the form is valid, otherwise false.
   */
  const validateForm = (): boolean => {
    let isValid = true;
    setError(null);

    if (!email) {
      setError("Email is required.");
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setError("Please enter a valid email address.");
      isValid = false;
    }

    if (!password) {
      setError((prev) =>
        prev ? prev + " Password is required." : "Password is required."
      );
      isValid = false;
    } else if (password.length < 8) {
      setError((prev) =>
        prev
          ? prev + " Password must be at least 8 characters."
          : "Password must be at least 8 characters."
      );
      isValid = false;
    }

    return isValid;
  };

  /**
   * Handles login form submission.
   * Authenticates with Cognito, updates Zustand auth state,
   * stores cookies, and redirects to the home page.
   *
   * @param {React.FormEvent<HTMLFormElement>} e - The form submit event.
   */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    if (!validateForm()) {
      setIsLoading(false);
      return;
    }

    try {
      const { idToken, accessToken, refreshToken } = await signIn(
        email,
        password
      );

      // Set auth state in Zustand
      useAuth.getState().setSession({ idToken, accessToken, refreshToken });

      // Store tokens in cookies (optionally refreshToken based on "rememberMe")
      storeSessionCookies(idToken, refreshToken, rememberMe);

      // Redirect to dashboard or homepage
      router.push("/");
    } catch (err: any) {
      console.error("Login error:", err);
      setError(err.message || "An unexpected error occurred during login.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="flex flex-col items-center gap-4 space-y-3 w-full "
    >
      <div className={cn("flex flex-col gap-6 w-full ", className)} {...props}>
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Welcome back</CardTitle>
            <CardDescription>Login to Your Account</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-6 w-full">
              <div className="grid gap-6">
                <div className="grid gap-3">
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
                <div className="grid gap-3">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="**************"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    id="rememberMe"
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <Label htmlFor="rememberMe">Remember Me</Label>
                </div>
                {error && (
                  <p className="text-red-500 text-sm text-center">{error}</p>
                )}
                <Button
                  type="submit"
                  className="w-full bg-primary color-primary cursor-pointer"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className="flex items-center">
                      <svg
                        className="animate-spin -ml-1 mr-3 h-5 w-5 text-current"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Logging in...
                    </span>
                  ) : (
                    "Login"
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
