import requests
from cfenv import AppEnv

class CFGenAIService:
    """
    Utility to load GenAI service credentials from Cloud Foundry environment (VCAP_SERVICES)
    and interact with the model config endpoint.
    """

    def __init__(self, service_name: str):
        env = AppEnv()
        self.service = env.get_service(name=service_name)
        if not self.service:
            raise ValueError(f"Service '{service_name}' not found in VCAP_SERVICES")

        creds = self.service.credentials
        self.api_base = creds.get("api_base")
        self.api_key = creds.get("api_key")

        endpoint = creds.get("endpoint", {})
        self.config_url = endpoint.get("config_url")

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def list_models(self, insecure: bool = True):
        """
        Call the config endpoint and return advertised models.
        :param insecure: set False to validate SSL certs (default True to match curl --insecure)
        :return: list of dicts with model details
        """
        if not self.config_url:
            raise ValueError("No config_url found in service credentials")

        response = requests.get(
            self.config_url,
            headers=self.get_headers(),
            verify=not insecure
        )
        response.raise_for_status()
        data = response.json()
        return data.get("advertisedModels", [])

    def __repr__(self):
        return f"<CFGenAIService api_base={self.api_base} config_url={self.config_url}>"


# Example usage
if __name__ == "__main__":
    service_name = "gen-ai-qwen3-ultra"
    genai = CFGenAIService(service_name)

    print("Service loaded:", genai)

    models = genai.list_models()
    print("Available models:")
    for m in models:
        print(f"- {m['name']} (capabilities: {', '.join(m['capabilities'])})")