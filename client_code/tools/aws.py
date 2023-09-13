from anvil.js.window import AWS  # Assuming AWS is the global variable that holds the AWS SDK bundle


class AmazonAccess:
    def __init__(self, region, identity_pool_id):
        self.region = region
        self.identity_pool_id = identity_pool_id

        self.cognito_client = AWS.CognitoIdentity({ 'region': self.region })
        print(f"Initialized Cognito Client: {self.cognito_client}")

    def get_credentials(self):
        command = AWS.CognitoIdentity.GetIdCommand({
            'IdentityPoolId': self.identity_pool_id
        })

        # Assuming you have a callback to handle the credentials
        def handle_response(err, data):
            if not err:
                # Do something with the credentials
                self.cognito_id = data['IdentityId']
                print(f"Received Cognito ID: {self.cognito_id}")
            else:
                print(f"Error receiving Cognito ID: {err}")

        self.cognito_client.send(command, handle_response)


class AmazonS3:
    def __init__(self, region, bucket_name):
        self.region = region
        self.bucket_name = bucket_name
        self.s3_client = AWS.S3Client({ 'region': self.region })
        print(f"Initialized S3 Client: {self.s3_client}")

    def upload_file(self, file_body, file_name):
        command = AWS.S3Client.PutObjectCommand({
            'Bucket': self.bucket_name,
            'Key': file_name,
            'Body': file_body
        })

        # Assuming you have a callback to handle the upload result
        def handle_upload(err, data):
            if not err:
                print('Upload successful')
            else:
                print(f'Upload failed: {err}')

        self.s3_client.send(command, handle_upload)


# Initial Python code for the home page to instantiate AWS objects
def initialize_aws():
    aws_access = AmazonAccess('your-region', 'your-identity-pool-id')
    aws_access.get_credentials()

    aws_s3 = AmazonS3('your-region', 'your-bucket-name')
    print(f"Successfully initialized AWS Access and S3 objects.")
