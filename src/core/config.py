import os
from dotenv import load_dotenv

from .aws_utils import AwsUtils


class Config:
    @staticmethod
    def _load_secrets(chamber_of_secrets, region):
        # NOTE: keys are read from AWS Secrets Manager SecretString JSON
        return {
            "env": chamber_of_secrets.get("ENV"),
            "region": chamber_of_secrets.get("REGION", region),
            "aws_endpoint": chamber_of_secrets.get("AWS_ENDPOINT"),
            "bedrock_model_id": chamber_of_secrets.get("BEDROCK_MODEL_ID"),
            "bedrock_mock": chamber_of_secrets.get("BEDROCK_MOCK"),

            # Cognito -> Bedrock (non-dev)
            "user_pool_id": chamber_of_secrets.get("USER_POOL_ID"),
            "client_id": chamber_of_secrets.get("CLIENT_ID"),
            "client_secret": chamber_of_secrets.get("CLIENT_SECRET"),
            "identity_pool_id": chamber_of_secrets.get("IDENTITY_POOL_ID"),
            "cognito_username": chamber_of_secrets.get("COGNITO_USERNAME"),
            "cognito_password": chamber_of_secrets.get("COGNITO_PASSWORD"),

            # Optional: protect endpoints (e.g., recommendation)
            "api_key": chamber_of_secrets.get("API_KEY"),
        }

    @staticmethod
    def _load_env_vars():
        return {
            "env": os.getenv("ENV", None),
            "region": os.getenv("REGION", None),
            "aws_endpoint": os.getenv("AWS_ENDPOINT", None),
            "bedrock_model_id": os.getenv("BEDROCK_MODEL_ID", None),
            "bedrock_mock": os.getenv("BEDROCK_MOCK", None),

            # Cognito -> Bedrock (non-dev)
            "user_pool_id": os.getenv("USER_POOL_ID", None),
            "client_id": os.getenv("CLIENT_ID", None),
            "client_secret": os.getenv("CLIENT_SECRET", None),
            "identity_pool_id": os.getenv("IDENTITY_POOL_ID", None),
            "cognito_username": os.getenv("COGNITO_USERNAME", None),
            "cognito_password": os.getenv("COGNITO_PASSWORD", None),

            # Optional endpoint protection
            "api_key": os.getenv("API_KEY", None),
        }

    @staticmethod
    def load_config():
        load_dotenv(dotenv_path=".env", override=True)

        SECRET_NAME = os.environ.get("SECRET_NAME", None)
        REGION = os.environ.get("REGION", None)
        AWS_ENDPOINT = os.environ.get("AWS_ENDPOINT", None)

        aws_utils = AwsUtils(region_name=REGION, aws_endpoint_url=AWS_ENDPOINT)
        print(f"Attempting to load secrets: {SECRET_NAME} from Secrets Manager in region {REGION}, using aws endpoint: {AWS_ENDPOINT}")
        try:
            chamber_of_secrets = aws_utils.get_secrets(SECRET_NAME)
            print(f"Loaded secrets: {SECRET_NAME} from Secrets Manager, using aws endpoint: {AWS_ENDPOINT}")
            return Config._load_secrets(chamber_of_secrets, REGION)
        except Exception as e:
            print(f"Error accessing secrets. Falling back to env vars. {e}")
            return Config._load_env_vars()
