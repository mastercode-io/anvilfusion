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
    def __init__(self, region, credentials, bucket):
        self.region = region
        self.bucket = bucket
        self.s3_client = anvil.js.new(
            AWS.S3.S3Client,
            {
                'region': self.region,
                'credentials': credentials,
            },
        )
        print(f"Initialized S3 Client: {self.s3_client}")

    def upload_file(self, file_key, file_body, bucket=None):
        command = AWS.S3.PutObjectCommand({
            'Bucket': bucket or self.bucket,
            'Key': file_key,
            'Body': file_body
        })
        response = self.s3_client.send(command)
        return response['$metadata'].httpStatusCode == 200

    def download_file(self, file_key, bucket=None):
        command = AWS.S3.GetObjectCommand({
            'Bucket': bucket or self.bucket,
            'Key': file_key,
        })
        response = self.s3_client.send(command)
        if response['$metadata'].httpStatusCode == 200:
            return response['Body']
        else:
            return None

    def move_file(self, file_key, new_file_key, bucket=None):
        copy_command = AWS.S3.CopyObjectCommand({
            'Bucket': bucket or self.bucket,
            'CopySource': f"{bucket or self.bucket}/{file_key}",
            'Key': new_file_key,
        })
        response = self.s3_client.send(copy_command)
        if response['$metadata'].httpStatusCode == 200:
            delete_command = AWS.S3.DeleteObjectCommand({
                'Bucket': bucket or self.bucket,
                'Key': file_key,
            })
            response = self.s3_client.send(delete_command)
            return response['$metadata'].httpStatusCode == 204
        else:
            return False

    def delete_files(self, file_keys, bucket=None):
        command = AWS.S3.DeleteObjectsCommand({
            'Bucket': bucket or self.bucket,
            'Delete': {
                'Objects': [{'Key': file_key} for file_key in file_keys],
                'Quiet': True,
            },
        })
        response = self.s3_client.send(command)
        if response:
            print(response)
            return response

    def get_presigned_url(self, file_key, bucket=None, expires_in=3600):
        command = AWS.S3.GetObjectCommand({
            'Bucket': bucket or self.bucket,
            'Key': file_key,
        })
        url = AWS.SignedUrl.getSignedUrl(self.s3_client, command, {'expiresIn': expires_in})
        return url
