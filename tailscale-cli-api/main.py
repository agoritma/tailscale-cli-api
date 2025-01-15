import os
import json
import subprocess
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(dotenv_path="tailscale-cli-api/.env")
api_domain = os.getenv("API_DOMAIN")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[api_domain],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/tailscale/info")
def get_version():
    try:
        tailscale_ip_output = (
            subprocess.check_output(["tailscale", "ip"]).decode("utf-8").split("\n")
        )

        tailscale_ip = {"ipv4": tailscale_ip_output[0], "ipv6": tailscale_ip_output[1]}

        tailscale_whois_output = (
            subprocess.check_output(["tailscale", "whois", tailscale_ip_output[0]])
            .decode("utf-8")
            .replace(" ", "")
            .split("\n")
        )

        tailscale_whois = {
            "machine": {
                "name": tailscale_whois_output[1].split(":")[1],
                "id": tailscale_whois_output[2].split(":")[1],
            },
            "user": {
                "email": tailscale_whois_output[5].split(":")[1],
                "id": tailscale_whois_output[6].split(":")[1],
            },
        }

        tailscale_version_output = json.loads(
            subprocess.check_output(["tailscale", "version", "--json"]).decode("utf-8")
        )

        return JSONResponse(
            content={
                "tailscale_whois": tailscale_whois,
                "tailscale_version": tailscale_version_output,
                "tailscale_ip_address": tailscale_ip,
            }
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/tailscale/status")
def get_status():
    try:
        tailscale_status_output = subprocess.check_output(
            ["tailscale", "status"]
        ).decode("utf-8")

        return JSONResponse(
            content={
                "status": "Tailscale is running.",
                "details": tailscale_status_output,
            }
        )
    except Exception:
        return JSONResponse(
            content={"status": "Tailscale is stopped."}, status_code=500
        )


@app.get("/api/tailscale/up")
def up():
    try:
        subprocess.check_output(["tailscale", "up"])
        return JSONResponse(content={"status": "Tailscale is running."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/tailscale/down")
def down():
    try:
        subprocess.check_output(["tailscale", "down"])
        return JSONResponse(content={"status": "Tailscale is stopped."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
