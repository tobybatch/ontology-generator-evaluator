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

On the dashboard, **Update** saves the form. **Start** reads the saved run's
UTF-8 text input sources, saves the current form and queues an ontology job.
PDF, DOCX and other binary document formats are not supported.

Start a worker in another terminal before submitting a run:

```bash
uv run python -m ontology_generator_evaluator.services.worker
```

The worker claims jobs from `storage/jobs.sqlite3`; it can be stopped and
restarted. A worker heartbeat permits abandoned jobs to be reclaimed after the
lease expires. A failed job displays its error; start the run again to retry.
For a single queued job, use `--once`. The run page shows progress when
refreshed and offers downloads only for the latest completed job whose inputs
and configuration have not changed.

Select an Ollama or OpenAI generation model and enter a separate embedding model
available from that provider (for example, `nomic-embed-text` for Ollama or
`text-embedding-3-small` for OpenAI). Pull the Ollama embedding model locally
before use. OpenAI requires `OPENAI_API_KEY`; Ollama must be running locally.
Enter an HTTP(S) base IRI ending in `/` or `#`; the default
`https://example.org/ontology/` is a placeholder and should be replaced for
published ontologies.

Every chunk is embedded and used as an anchor for generation, with up to two
similar chunks as additional context. The model is asked to use consistent
IRIs across fragments; RDF triples with identical terms are merged, but semantic
duplicates with different IRIs are not automatically reconciled. Model output
is parsed as Turtle; invalid or empty fragments fail the job rather than
producing a partial ontology. Generated ontologies should be reviewed by a
domain expert.

Each completed job stores its chunks, vectors, `ontology.ttl` and `graph.json`
under `storage/job_results/<job id>/<attempt id>/`. The SQLite job snapshot
contains the source text and run configuration. Data sent to OpenAI leaves the
local machine and may incur provider charges; Ollama processes it locally.
Storage and remote provider access should be protected appropriately.

`graph.json` version 1 represents the same RDF graph as the Turtle file:
`nodes` contain resource identifiers and literal `attributes` (each with a
predicate and value); `edges` contain resource-to-resource triples with
`source`, `predicate` and `target`. Each term has a `type` (`iri`, `blank` or
`literal`) and `value`; literals also include `datatype` or `language` when
present. Blank node identifiers are canonicalized for stable output.

Run tests with 

```bash
uv run pytest -q
```

Run e2e tests with 

```bash
npm run test:e2e
```