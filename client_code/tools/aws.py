import anvil.js
from anvil.js.window import AWS  # Assuming AWS is the global variable that holds the AWS SDK bundle


class AmazonAccess:
    def __init__(self, region, identity_pool_id):
        self.region = region
        self.identity_pool_id = identity_pool_id
        self.cognito_client = AWS.CognitoIdentity.CognitoIdentityClient({'region': self.region})
        self.credentials = AWS.CognitoIdentityPool.fromCognitoIdentityPool({
            'client': self.cognito_client,
            'clientConfig': {'region': self.region},
            'identityPoolId': self.identity_pool_id,
        })()
        print(f"Initialized Cognito Credentials: {self.credentials.accessKeyId}, {self.credentials.secretAccessKey}")


class AmazonS3:
    def __init__(self, region, credentials, bucket_name):
        self.region = region
        self.bucket_name = bucket_name
        self.s3_client = anvil.js.new(
            AWS.S3.S3Client,
            {
                'region': self.region,
                'credentials': credentials,
            },
        )
        self.response = None
        print(f"Initialized S3 Client: {self.s3_client}")

    def upload_file(self, file_name, file_body):
        command = AWS.S3.PutObjectCommand({
            'Bucket': self.bucket_name,
            'Key': file_name,
            'Body': file_body
        })
        self.response = self.s3_client.send(command)
        return self.response['$metadata'].httpStatusCode == 200

    def download_file(self, file_name):
        command = AWS.S3.GetObjectCommand({
            'Bucket': self.bucket_name,
            'Key': file_name,
        })
        self.response = self.s3_client.send(command)
        if self.response['$metadata'].httpStatusCode == 200:
            return self.response['Body']
        else:
            return None

    def get_presigned_url(self, file_name, expires_in=3600):
        command = AWS.S3.GetObjectCommand({
            'Bucket': self.bucket_name,
            'Key': file_name,
        })
        url = AWS.SignedUrl.getSignedUrl(self.s3_client, command, {'expiresIn': expires_in})
        return url
