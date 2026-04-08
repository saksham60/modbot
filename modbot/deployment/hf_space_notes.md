# Hugging Face Spaces Notes

- Runtime: Docker Space
- Exposed port: `7860`
- Startup command: `bash modbot/deployment/start.sh`
- Primary UI entrypoint: `python -m modbot.app.ui.app`
- Optional secrets: `HF_TOKEN`, `MODEL_BACKEND`, `MODEL_NAME`, `MODEL_BASE_URL`, `MODEL_API_KEY`

Local build:

```bash
docker build -f modbot/deployment/Dockerfile -t modbot .
docker run --rm -p 7860:7860 modbot
```
