# Ontology generator evaluator

## Local configuration

Install Ollama

Goto https://ollama.com/download and choose the manual download option
Install it, remember to escalate permission if necessary

```bash
ollama pull llama3.2:latest # compact 2GB model
ollama ls
ollama serve
```

You want to pick a model that matches hw much ram you have. Macs use unified ram, so it's a trade off between system usage and model size. Running the system, slack, chrome with webmail, miro, and a few other apps, will use about 10 - 14 GB of RAM. Pick a model that will fit in the remaining RAM. On Windows/Linux machine you will want to target the amount if video ram you have on your graphics card, less a little for overhead. e.g. on a 6gb card, aim for a 4-5gb model. 

The following table shows sample models with different RAM sizes:

| Model name                 | Size   |
|----------------------------|--------|  
| qwen3-coder:30b            | 18 GB  |  
| Mistral-Small:24B          | 14 GB  |       
| qwen2.5:14b                | 9.0 GB |       
| qwen3:8b                   | 5.2 GB |    
| mistral:latest             | 4.4 GB |     
| llama3.2:latest            | 2.0 GB |  


Install the JavaScript and Python dependencies and Git hooks with:

```bash
npm install
```

The npm `postinstall` script runs `uv run pre-commit install`, which syncs the
Python environment and installs the hooks. It requires `uv` and a Git
checkout. If npm lifecycle scripts are disabled, or you only need the Python
environment, install the hooks separately:

```bash
uv sync
uv run pre-commit install
```

`uv sync` does not install Git hooks automatically. The hooks run Ruff on
staged files and validate commit messages with Commitizen. Use a message such as
`feat: add a provider` or `fix(api): handle errors`; the supported types are
`feat`, `fix`, `refactor`, `docs`, `tests`, `chore`, and `build`.
Commitizen also permits its default merge, revert, and fixup prefixes.

Copy `.env.example` to `.env` in the project root and set your key:

```dotenv
OPENAI_API_KEY=your-openai-api-key
```

Configuration is loaded automatically when `services.run_service` is imported,
including when starting the Flask app. The `.env` path is resolved relative to
the project, so it works regardless of the current working directory. Existing
environment variables take precedence over `.env` values.

The `.env` file is ignored by Git. Never commit your API key. OpenAI requests
raise an error if `OPENAI_API_KEY` is missing or empty.

Run it with 

```bash
uv run flask run --debug
```

On the dashboard, **Update** saves the form using the existing dashboard handler.
**Start** calls the new `start_run` placeholder, which also saves the form and
displays a message that run execution is not implemented yet.

Run tests with 

```bash
uv run pytest -q
```

Run e2e tests with 

```bash
npm run test:e2e
```