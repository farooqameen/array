import {
  AuthenticationDetails,
  CognitoUser,
  CognitoUserPool,
} from "amazon-cognito-identity-js";
import { awsConfig } from "./awsConfig";
import { deleteCookie } from "cookies-next";
import { useAuth } from "@/lib/auth/authStore";

// Create a Cognito user pool instance
const userPool = new CognitoUserPool({
  UserPoolId: awsConfig.userPoolId,
  ClientId: awsConfig.userPoolClientId,
});

/**
 * Authenticates a user with email and password via Cognito User Pool.
 *
 * @param {string} email - The user's email address (username).
 * @param {string} password - The user's password.
 * @returns {Promise<{ idToken: string; accessToken: string; refreshToken: string }>}
 *          Resolves with the user's Cognito tokens on successful authentication.
 *          Rejects with an error if authentication fails.
 */
export const signIn = (
  email: string,
  password: string
): Promise<{ idToken: string; accessToken: string; refreshToken: string }> => {
  const user = new CognitoUser({ Username: email, Pool: userPool });
  const authDetails = new AuthenticationDetails({
    Username: email,
    Password: password,
  });

  return new Promise((resolve, reject) => {
    user.authenticateUser(authDetails, {
      onSuccess: (session) => {
        const idToken = session.getIdToken().getJwtToken();
        const accessToken = session.getAccessToken().getJwtToken();
        const refreshToken = session.getRefreshToken().getToken();

        resolve({ idToken, accessToken, refreshToken });
      },
      onFailure: (err) => reject(err),
    });
  });
};

/**
 * Logs out the user by clearing authentication cookies and resetting auth state.
 */
export const logout = () => {
  deleteCookie("idToken");
  deleteCookie("refreshToken");
  useAuth.getState().clear();
};
