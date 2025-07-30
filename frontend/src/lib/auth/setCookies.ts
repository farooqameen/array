import { setCookie } from "cookies-next";

/**
 * Stores authentication tokens in secure cookies.
 *
 * This function sets the `idToken` as a secure cookie for identifying the user session.
 * If the user opts for "Remember Me" and a `refreshToken` is provided,
 * it also stores the `refreshToken` in an HTTP-only cookie with a longer lifespan.
 *
 * @param {string} idToken - The ID token received from Cognito upon successful authentication.
 * @param {string | null} refreshToken - The refresh token to allow session renewal (optional).
 * @param {boolean} rememberMe - Whether to persist the session using a refresh token.
 *
 * @example
 * storeSessionCookies(idToken, refreshToken, true);
 */
export const storeSessionCookies = (
  idToken: string,
  refreshToken: string | null,
  rememberMe: boolean
) => {
  // Always store ID token (used for session verification in middleware)
  setCookie("idToken", idToken, {
    maxAge: 60 * 60, // 1 hour
    path: "/",
    secure: true,
    sameSite: "lax",
  });

  // Store refresh token only if user opts to be remembered
  if (rememberMe && refreshToken) {
    setCookie("refreshToken", refreshToken, {
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: "/",
      httpOnly: true,
      secure: true,
      sameSite: "lax",
    });
  }
};
