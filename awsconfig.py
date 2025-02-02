import boto3


class Myaws:
    # def __init__(self, aws_access_key, aws_secret_key):
    #     self.aws_access_key = aws_access_key
    #     self.aws_secret_key = aws_secret_key
    #     self.region = 'us-east-1'

    def get_connection_to_aws(self, service_type, aws_access_key, aws_secret_key):
        try:
            get_service_connection = boto3.client(service_type, aws_access_key_id = aws_access_key, aws_secret_access_key = aws_secret_key, region_name='eu-north-1')
            return get_service_connection
        except Exception as e:
            print(e)
            return None