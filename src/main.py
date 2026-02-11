from fastapi import FastAPI, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader

from core.config import Config
from core.bedrock_client_cognito import BedrockClient as CognitoBedrockClient
from local.bedrock_client import BedrockClient as LocalBedrockClient

from inference.recommendation import (
    recommend_objective,
    SimpleObjectiveRequest,
    SimpleRecommendResponse,
)

config = Config.load_config()

if config.get("env") == "local":
    bedrock_client = LocalBedrockClient(region_name=config["region"], endpoint_url=config.get("aws_endpoint"))
else:
    bedrock_client = CognitoBedrockClient(
        region_name=config["region"],
        config=config,
        endpoint_url=config.get("aws_endpoint"),
    )

app = FastAPI(title="Cyara Recommendation Engine", version="1.0.0")


# --- API key (shows in Swagger nicely) ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str | None = Depends(api_key_header)):
    expected = config.get("api_key")
    # If no API key configured, allow requests (backwards compatible)
    if not expected:
        return
    if not api_key or api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.post(
    f"/{config['env']}/recommendation",
    response_model=SimpleRecommendResponse,
    summary="Recommend clearer defining objective",
    description="Takes a vague objective and optional context and returns a clearer, testable defining objective.",
)
async def handle_recommendation(
    req: SimpleObjectiveRequest,
    _: None = Depends(verify_api_key),
):
    model_id = config.get("bedrock_model_id")
    result = recommend_objective(req, bedrock_client=bedrock_client, model_id=model_id)
    return result

