# Shramik Sahayak GenAI

FastAPI service for the Shramik Sahayak worker-assistance pipeline.

## Run locally

Install the dependencies, set `OPENAI_API_KEY`, then start the server:

```sh
python -m pip install -r requirements.txt
export OPENAI_API_KEY=your-key
uvicorn app.agent_pipeline:app --reload
```

The health endpoint is available at `http://localhost:8000/health` and the API
documentation at `http://localhost:8000/docs`.

## Deploy on Vercel

1. Open the [Vercel import page](https://vercel.com/new/import?repository-name=shramik-sahayak-genai&s=https%3A%2F%2Fgithub.com%2Fvamika-Sharma2305%2Fshramik-sahayak-genai&teamSlug=vamika-sharma) and import this repository.
2. Add `OPENAI_API_KEY` under the project's Environment Variables. Keep it secret; do not commit it to the repository.
3. Deploy. Vercel will provide the public deployment URL; the API docs are at `/docs` and the health endpoint is at `/health`.

The Vercel function entry point is `api/index.py`, with routing configured in `vercel.json`.

## Deploy on Render

1. Push this repository to GitHub.
2. In Render, choose **New +** then **Blueprint**, and connect the repository.
3. Set `OPENAI_API_KEY` when prompted. Keep it secret; do not commit it to the repository.
4. Create the service. Render will build the Docker image and assign the public URL.

The deployment uses `render.yaml`; the service checks `/health` after startup.
The public URL is assigned by Render after the first successful deployment.