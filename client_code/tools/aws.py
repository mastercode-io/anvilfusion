from anvil import js
from anvil.js.window import AWS


class AmazonAccess:
    def __init__(
            self,
            region=None,
            identity_pool_id=None
    ):
        self.region = region
        self.identity_pool_id = identity_pool_id
        self.cognito_id = None

        self.cognito_client = js.new(AWS.CognitoIdentity.CognitoIdentityClient, {'region': self.region})
        print(f"Initialized Cognito Client: {self.cognito_client}")

    def refresh(self):
        command = AWS.CognitoIdentity.GetIdCommand({
            'IdentityPoolId': self.identity_pool_id
        })

        def resolve(error, data):
            if not error:
                self.cognito_id = data['IdentityId']
                print(f"Received Cognito ID: {self.cognito_id}")
            else:
                print(f"Error receiving Cognito ID: {error}")

        self.cognito_client.send(command, resolve)


class AmazonS3:
    def __init__(
            self,
            region=None,
            bucket_name=None,
    ):
        self.region = region
        self.bucket_name = bucket_name
        self.s3_client = js.new(AWS.S3Client.S3Client, {'region': self.region})
        print(f"Initialized S3 Client: {self.s3_client}")

    def upload_file(self, file_body, file_name):
        command = AWS.S3Client.PutObjectCommand({
            'Bucket': self.bucket_name,
            'Key': file_name,
            'Body': file_body
        })

        def resolve(error, data):
            if not error:
                print(f"Upload successful: {data}")
            else:
                print(f"Upload failed: {error}")

        self.s3_client.send(command, resolve)
