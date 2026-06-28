import os
import json
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from core.orbit_engine import OrbitEngine
from core.tracking_engine import get_tracking_snapshot
from core.pass_engine import find_visible_passes, get_best_pass

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
SATELLITES_PATH = BASE_DIR / "data" / "satellites.json"
GITHUB_PAGES_URL = "https://klovoksilo-svg.github.io/fergani/"
CURRENT_API_PATH = BASE_DIR / "data" / "current_api.json"

app = FastAPI()

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "FERGANI_CORS_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000,https://ceyhu.github.io,https://klovoksilo-svg.github.io"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=os.getenv(
        "FERGANI_CORS_ORIGIN_REGEX",
        r"https://.*\.(trycloudflare\.com|ngrok-free\.app|ngrok\.io)"
    ),
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

engine = OrbitEngine(str(SATELLITES_PATH))


def find_cloudflared():
    executable = shutil.which("cloudflared")

    if executable:
        return executable

    candidates = [
        Path(os.getenv("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / "cloudflared.exe",
        Path(os.getenv("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages" / "Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe" / "cloudflared.exe",
        Path(os.getenv("ProgramFiles", "")) / "cloudflared" / "cloudflared.exe",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return None


def find_git():
    executable = shutil.which("git")

    if executable:
        return executable

    candidates = [
        Path(os.getenv("ProgramFiles", "")) / "Git" / "cmd" / "git.exe",
        Path(os.getenv("ProgramFiles", "")) / "Git" / "bin" / "git.exe",
        Path(os.getenv("ProgramFiles(x86)", "")) / "Git" / "cmd" / "git.exe",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return None


def publish_current_api_url(tunnel_url):
    CURRENT_API_PATH.write_text(
        json.dumps(
            {
                "api_base_url": tunnel_url,
                "updated_at_utc": datetime.now(timezone.utc).isoformat()
            },
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    git = find_git()

    if not git:
        print("Git bulunamadi; data/current_api.json GitHub'a otomatik gonderilemedi.", flush=True)
        return

    try:
        subprocess.run([git, "-C", str(BASE_DIR), "add", "data/current_api.json"], check=True)
        diff = subprocess.run(
            [git, "-C", str(BASE_DIR), "diff", "--cached", "--quiet"],
            check=False
        )

        if diff.returncode == 0:
            print("Aktif API adresi zaten GitHub dosyasiyla ayni.", flush=True)
            return

        subprocess.run(
            [git, "-C", str(BASE_DIR), "commit", "-m", "Update current public API URL"],
            check=True
        )
        subprocess.run([git, "-C", str(BASE_DIR), "push"], check=True)
        print("Aktif API adresi GitHub'a gonderildi.", flush=True)
        print("Sabit QR adresi:", flush=True)
        print(GITHUB_PAGES_URL, flush=True)
    except subprocess.CalledProcessError as error:
        print(f"Aktif API adresi GitHub'a gonderilemedi: {error}", flush=True)


def start_public_tunnel(port):
    cloudflared = find_cloudflared()

    if not cloudflared:
        print("Cloudflare Tunnel araci bulunamadi: cloudflared", flush=True)
        print("Kurulum: winget install --id Cloudflare.cloudflared", flush=True)
        return

    time.sleep(2)
    print("Cloudflare Tunnel baslatiliyor...", flush=True)

    process = subprocess.Popen(
        [cloudflared, "tunnel", "--url", f"http://127.0.0.1:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    for line in process.stdout:
        print(line, end="", flush=True)

        if "trycloudflare.com" in line:
            for part in line.replace("|", " ").split():
                if part.startswith("https://") and "trycloudflare.com" in part:
                    tunnel_url = part.strip()
                    encoded_api = urllib.parse.quote(tunnel_url, safe="")
                    public_url = f"{GITHUB_PAGES_URL}?api={encoded_api}"
                    publish_current_api_url(tunnel_url)
                    print("", flush=True)
                    print("PAYLASILACAK GITHUB LINKI:", flush=True)
                    print(public_url, flush=True)
                    print("", flush=True)
                    print("SABIT QR LINKI:", flush=True)
                    print(GITHUB_PAGES_URL, flush=True)
                    print("", flush=True)
                    print("Bu linkten QR kod uret. Bu pencere kapanirsa canli takip durur.", flush=True)
                    break


def is_local_api_running(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/satellites", timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def utc_iso_to_turkey_time_text(utc_iso_text):
    turkey_timezone = timezone(timedelta(hours=3))
    utc_time = datetime.fromisoformat(utc_iso_text)
    turkey_time = utc_time.astimezone(turkey_timezone)

    return turkey_time.strftime("%Y-%m-%d %H:%M:%S")


@app.get("/")
def home():
    return {
        "message": "Fergani API çalışıyor",
        "ui": "/ui"
    }


@app.get("/ui")
def ui():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/satellites")
def get_satellites():
    return {
        "satellites": engine.list_satellites()
    }


@app.get("/track")
def track_satellite(
    satellite_name: str = "TURKSAT 6A",
    observer_lat: float = 39.9334,
    observer_lon: float = 32.8597,
    observer_elevation_m: float = 900
):
    try:
        snapshot = get_tracking_snapshot(
            engine=engine,
            satellite_name=satellite_name,
            observer_lat=observer_lat,
            observer_lon=observer_lon,
            observer_elevation_m=observer_elevation_m
        )

        return {
            "ok": True,
            "error": None,
            "data": snapshot
        }

    except ValueError as error:
        return {
            "ok": False,
            "error": str(error),
            "data": None
        }


@app.get("/best-pass")
def best_pass(
    satellite_name: str = "TURKSAT 6A",
    observer_lat: float = 39.9334,
    observer_lon: float = 32.8597,
    observer_elevation_m: float = 900
):
    passes = find_visible_passes(
        engine=engine,
        satellite_name=satellite_name,
        observer_lat=observer_lat,
        observer_lon=observer_lon,
        observer_elevation_m=observer_elevation_m,
        hours_ahead=24,
        step_minutes=1
    )

    selected_pass = get_best_pass(passes)

    if selected_pass is None:
        return {
            "ok": True,
            "satellite": satellite_name,
            "visible_pass_found": False,
            "message": "Önümüzdeki 24 saat içinde görünür geçiş bulunamadı veya TLE verisi yok."
        }

    first = selected_pass[0]
    last = selected_pass[-1]
    max_point = max(selected_pass, key=lambda item: item["elevation_deg"])

    return {
        "ok": True,
        "satellite": satellite_name,
        "visible_pass_found": True,
        "pass_count": len(passes),

        "observer_lat": observer_lat,
        "observer_lon": observer_lon,
        "observer_elevation_m": observer_elevation_m,

        "start_utc": first["datetime_utc"],
        "end_utc": last["datetime_utc"],
        "max_elevation_utc": max_point["datetime_utc"],

        "start_tr": utc_iso_to_turkey_time_text(first["datetime_utc"]),
        "end_tr": utc_iso_to_turkey_time_text(last["datetime_utc"]),
        "max_elevation_tr": utc_iso_to_turkey_time_text(max_point["datetime_utc"]),

        "duration_minutes": len(selected_pass),
        "max_elevation_deg": round(max_point["elevation_deg"], 2),
        "start_azimuth_deg": round(first["azimuth_deg"], 2),
        "end_azimuth_deg": round(last["azimuth_deg"], 2)
    }


if __name__ == "__main__":
    public_mode = "--public" in sys.argv or os.getenv("FERGANI_PUBLIC", "false").lower() == "true"
    host = os.getenv("FERGANI_HOST", "127.0.0.1")
    port = int(os.getenv("FERGANI_PORT", "8000"))
    reload_enabled = os.getenv("FERGANI_RELOAD", "true").lower() == "true"

    if public_mode:
        host = "127.0.0.1"
        reload_enabled = False

        if is_local_api_running(port):
            print("Fergani API zaten calisiyor; mevcut API uzerinden tunel aciliyor.", flush=True)
            print(f"Yerel adres: http://127.0.0.1:{port}/ui", flush=True)
            start_public_tunnel(port)
            sys.exit(0)

        tunnel_thread = threading.Thread(target=start_public_tunnel, args=(port,), daemon=True)
        tunnel_thread.start()

        print("Fergani genel paylasim modu basliyor.", flush=True)
        print(f"Yerel adres: http://127.0.0.1:{port}/ui", flush=True)

    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=reload_enabled
    )
