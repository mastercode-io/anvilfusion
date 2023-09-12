# from anvil.js.window import CognitoIdentity, S3Client
from anvil.js.window import AWS


class AmazonAccess:
    def __init__(self, region, identity_pool_id):
        self.region = region
        self.identity_pool_id = identity_pool_id
        self.access_key = None
        self.secret_key = None
        self.session_token = None

        self.cognito_identity = AWS.CognitoIdentityCredentials({
            'IdentityPoolId': self.identity_pool_id
        })
        AWS.config.update(
            {
                'credentials': self.cognito_identity,
                'region': self.region}
        )


    def get_credentials(self):
        AWS.config.credentials.get()


    def set_credentials(self, error):
        if not error:
            self.access_key = AWS.config.credentials.accessKeyId
            self.secret_key = AWS.config.credentials.secretAccessKey
            self.session_token = AWS.config.credentials.sessionToken


class AmazonS3:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = AWS.S3()


def get_temporary_credentials(callback):
    AWS.config.update({'region': 'your-region'})

    cognito_identity = AWS.CognitoIdentityCredentials({
        'IdentityPoolId': 'your-identity-pool-id'
    })

    AWS.config.update({'credentials': cognito_identity})

    def on_get(err):
        if err:
            print(f"Error: {err}")
            callback(None)
        else:
            access_key = AWS.config.credentials.accessKeyId
            secret_key = AWS.config.credentials.secretAccessKey
            session_token = AWS.config.credentials.sessionToken
            callback((access_key, secret_key, session_token))

    AWS.config.credentials.get(on_get)


def s3_upload(access_key, secret_key, session_token):
    params = {
        'Bucket': 'your-bucket-name',
        'Key': 'your-key',
        'Body': 'your-file-body',
        'ContentType': 'your-content-type',
        'ACL': 'private'
    }

    AWS.config.update({
        'region': 'your-region',
        'accessKeyId': access_key,
        'secretAccessKey': secret_key,
        'sessionToken': session_token
    })

    s3 = AWS.S3()

    def s3_result(err, data):
        if err:
            print(f"Error uploading: {err}")
        else:
            print(f"Successfully uploaded: {data}")

    s3.upload(params, s3_result)


# Example usage
def start_upload():
    def on_credentials_received(credentials):
        if credentials:
            access_key, secret_key, session_token = credentials
            s3_upload(access_key, secret_key, session_token)

    get_temporary_credentials(on_credentials_received)


def generate_presigned_url(bucket_name, object_key):
    AWS.config.update({
        'region': 'your-region',  # replace with your region
        # Add other AWS config if needed
    })

    s3 = AWS.S3()

    def presigned_url_result(err, url):
        if err:
            print(f"Error generating presigned URL: {err}")
        else:
            print(f"Generated presigned URL: {url}")
            # Here you can use the URL to initiate a download from the client,
            # for example by setting window.location.href = url or similar.

    params = {
        'Bucket': bucket_name,
        'Key': object_key,
        'Expires': 60  # The URL will expire in 60 seconds
    }

    s3.getSignedUrl('getObject', params, presigned_url_result)


# Example usage
generate_presigned_url('your-bucket-name', 'your-object-key')
