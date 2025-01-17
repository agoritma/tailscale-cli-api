import os
import json
import subprocess
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv

load_dotenv(dotenv_path="tailscale-cli-api/.env")
API_DOMAIN = os.getenv("API_DOMAIN")
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "access_token"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[API_DOMAIN],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized"
        )


@app.get("/api/tailscale/status")
async def get_status(api_key: str = Depends(api_key_header)):
    get_api_key(api_key)
    try:
        tailscale_status_output = json.loads(
            subprocess.check_output(["tailscale", "status", "--json"]).decode("utf-8")
        )

        return JSONResponse(content=tailscale_status_output)
    except Exception:
        return JSONResponse(
            content={"status": "Tailscale is stopped."}, status_code=500
        )


@app.get("/api/tailscale/up")
async def up(api_key: str = Depends(api_key_header)):
    get_api_key(api_key)
    try:
        subprocess.check_output(["tailscale", "up"])
        return JSONResponse(content={"status": "Tailscale is running."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/tailscale/down")
async def down(api_key: str = Depends(api_key_header)):
    get_api_key(api_key)
    try:
        subprocess.check_output(["tailscale", "down"])
        return JSONResponse(content={"status": "Tailscale is stopped."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", reload=True, host="0.0.0.0")
