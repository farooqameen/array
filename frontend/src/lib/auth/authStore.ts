import { create } from "zustand";
/**
 * Represents a set of authentication tokens returned after login.
 */
type Session = {
  idToken: string; // JWT token containing user identity claims
  accessToken: string; // Token used to authorize API requests
  refreshToken: string; // Token to obtain new access and ID tokens
};

/**
 * Zustand store state for authentication tokens and related actions.
 */
type AuthState = {
  idToken: string | null; // Current ID token or null if not set
  accessToken: string | null; // Current access token or null if not set
  refreshToken: string | null; // Current refresh token or null if not set
  /**
   * Updates the store with new session tokens.
   * @param tokens - Object containing idToken, accessToken, and refreshToken
   */
  setSession: (tokens: Session) => void;

  /**
   * Clears all tokens from the store.
   */
  clear: () => void;
};

/**
 * Zustand store for authentication tokens.
 * @type {AuthState}
 * @example
 * const { idToken, accessToken, refreshToken, setSession, clear } = useAuth();
 */
export const useAuth = create<AuthState>((set) => ({
  idToken: null,
  accessToken: null,
  refreshToken: null,
  /**
   * Updates Zustand store with session tokens
   */
  setSession: ({ idToken, accessToken, refreshToken }) =>
    set({ idToken, accessToken, refreshToken }),

  /**
   * Clears all tokens from the Zustand store
   */
  clear: () => set({ idToken: null, accessToken: null, refreshToken: null }),
}));
