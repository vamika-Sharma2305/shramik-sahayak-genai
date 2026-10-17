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

## Deploy on Render

1. Push this repository to GitHub.
2. In Render, choose **New +** then **Blueprint**, and connect the repository.
3. Set `OPENAI_API_KEY` when prompted. Keep it secret; do not commit it to the repository.
4. Create the service. Render will build the Docker image and assign the public URL.

The deployment uses `render.yaml`; the service checks `/health` after startup.
The public URL is assigned by Render after the first successful deployment.