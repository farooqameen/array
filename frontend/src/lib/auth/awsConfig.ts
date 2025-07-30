/**
 * AWS Cognito and DynamoDB configuration object.
 *
 * This centralizes the environment-based configuration values used throughout the app.
 *
 * @property {string} region - AWS region where your Cognito and DynamoDB resources are hosted.
 * @property {string} userPoolId - Cognito User Pool ID used for user authentication.
 * @property {string} userPoolClientId - Cognito App Client ID tied to the user pool.
 * @property {string} identityPoolId - Cognito Identity Pool ID used for federated identity.
 * @property {string} dynamoDBTableName - Name of the DynamoDB table used for storing app data.
 */

export const awsConfig = {
  region: process.env.NEXT_PUBLIC_APP_AWS_REGION!,
  userPoolId: process.env.NEXT_PUBLIC_APP_USER_POOL_ID!,
  userPoolClientId: process.env.NEXT_PUBLIC_APP_USER_POOL_CLIENT_ID!,
  identityPoolId: process.env.NEXT_PUBLIC_APP_IDENTITY_POOL_ID!,
  dynamoDBTableName: process.env.NEXT_PUBLIC_APP_DYNAMODB_TABLE_NAME!,
};
