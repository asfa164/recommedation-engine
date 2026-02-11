from fastapi import FastAPI, Request, HTTPException
from core.config import Config
from core.bedrock_client_cognito import BedrockClient as CognitoBedrockClient
from local.bedrock_client import BedrockClient as LocalBedrockClient
from inference.recommendation import recommend_objective

config = Config.load_config()

# Choose Bedrock client by environment:
# - dev -> local mock
# - others -> cognito-authenticated real bedrock
if config.get("env") == "dev":
    print("Using LOCAL Bedrock client (dev)")
    bedrock_client = LocalBedrockClient(
        region_name=config["region"],
        endpoint_url=config.get("aws_endpoint"),
    )
else:
    print("Using COGNITO Bedrock client (non-dev)")
    bedrock_client = CognitoBedrockClient(
        region_name=config["region"],
        config=config,
        endpoint_url=config.get("aws_endpoint"),
    )

app = FastAPI(title="Cyara Recommendation Engine", version="1.0.0")


def _verify_api_key(request: Request):
    expected = config.get("api_key")
    if not expected:
        return
    provided = request.headers.get("X-API-Key")
    if not provided or provided != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.post(f"/{config['env']}/recommendation")
async def handle_recommendation(request: Request):
    _verify_api_key(request)
    try:
        body = await request.json()
        model_id = config.get("bedrock_model_id")
        result = recommend_objective(body, bedrock_client=bedrock_client, model_id=model_id)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
