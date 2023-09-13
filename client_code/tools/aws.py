import anvil.js
from anvil.js.window import AWS  # Assuming AWS is the global variable that holds the AWS SDK bundle


class AmazonAccess:
    def __init__(
            self,
            region=None,
            identity_pool_id=None
    ):
        self.region = region
        self.identity_pool_id = identity_pool_id
        self.cognito_id = None

        self.cognito_client = anvil.js.new(AWS.CognitoIdentity.CognitoIdentityClient, {'region': self.region})
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
        self.s3_client = anvil.js.new(AWS.S3Client.S3Client, {'region': self.region})
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


# Initial Python code for the home page to instantiate AWS objects
def initialize_aws(
    region=None,
    identity_pool_id=None,
    bucket_name=None,
):
    aws_access = AmazonAccess(region=region, identity_pool_id=identity_pool_id)
    aws_access.refresh()

    aws_s3 = AmazonS3(region=region, bucket_name=bucket_name)
    print(f"Successfully initialized AWS Access and S3 objects.")
