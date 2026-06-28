import os
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

app = FastAPI()

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "FERGANI_CORS_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000,https://ceyhu.github.io"
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
    host = os.getenv("FERGANI_HOST", "127.0.0.1")
    port = int(os.getenv("FERGANI_PORT", "8000"))
    reload_enabled = os.getenv("FERGANI_RELOAD", "true").lower() == "true"

    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=reload_enabled
    )
