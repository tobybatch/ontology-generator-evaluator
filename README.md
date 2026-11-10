# Ontology generator evaluator

## Local configuration

Install dependencies with `uv sync`, then copy `.env.example` to `.env` in the
project root and set your key:

```dotenv
OPENAI_API_KEY=your-openai-api-key
```

Configuration is loaded automatically when `services.run_service` is imported,
including when starting the Flask app. The `.env` path is resolved relative to
the project, so it works regardless of the current working directory. Existing
environment variables take precedence over `.env` values.

The `.env` file is ignored by Git. Never commit your API key. OpenAI requests
raise an error if `OPENAI_API_KEY` is missing or empty.