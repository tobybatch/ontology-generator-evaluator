import boto3
from mypy_boto3_bedrock import BedrockClient
from mypy_boto3_bedrock.type_defs import FoundationModelSummaryTypeDef

from config import load_config, AWS_REGION

load_config()


class BedrockProvider:
    client: BedrockClient

    def __init__(self):
        self.client = boto3.client("bedrock", region_name=AWS_REGION)

    def get_models(self) -> list[FoundationModelSummaryTypeDef]:
        response = self.client.list_foundation_models()
        models = response.get("modelSummaries", [])

        print(f"Found {len(models)} models available in {AWS_REGION}:\n")
        print(f"{'MODEL ID':<50} | {'PROVIDER':<15} | {'INFERENCE TYPES'}")
        print("-" * 90)

        for model in models:
            model_id = model.get("modelId")
            provider = model.get("providerName")
            inference_types = ", ".join(model.get("inferenceTypesSupported", []))

            print(f"{model_id:<50} | {provider:<15} | {inference_types}")

        return models

    def generate(self, prompt: str) -> str: ...

