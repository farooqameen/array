import { CognitoIdentityClient } from "@aws-sdk/client-cognito-identity";
import { fromCognitoIdentityPool } from "@aws-sdk/credential-provider-cognito-identity";
import { awsConfig } from "./awsConfig";

/**
 * Returns AWS temporary credentials using a Cognito identity pool and a valid ID token.
 *
 * This is used to authenticate the user with AWS services (e.g., DynamoDB, S3)
 * after they've signed in through Cognito User Pools. It links the user identity
 * from the User Pool to the Identity Pool to fetch temporary AWS credentials.
 *
 * @param idToken - A valid ID token obtained from Cognito User Pools.
 * @returns {Promise<import("@aws-sdk/types").AwsCredentialIdentity>} A promise resolving to temporary AWS credentials.
 *
 * @example
 * const credentials = await getAWSCredentials(idToken);
 * const client = new DynamoDBClient({ credentials });
 */
export const getAWSCredentials = (idToken: string) => {
  return fromCognitoIdentityPool({
    client: new CognitoIdentityClient({ region: awsConfig.region }),
    identityPoolId: awsConfig.identityPoolId,
    logins: {
      [`cognito-idp.${awsConfig.region}.amazonaws.com/${awsConfig.userPoolId}`]:
        idToken,
    },
  });
};
