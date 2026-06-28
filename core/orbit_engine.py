import json
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta

from skyfield.api import EarthSatellite, load, wgs84


class OrbitEngine:
    def __init__(self, satellites_json_path: str):
        self.ts = load.timescale()
        satellites_path = Path(satellites_json_path)
        self.cache_path = satellites_path.parent / "tle_cache.json"
        self.cache_max_age = timedelta(hours=6)
        self.satellites = self._load_satellites(str(satellites_path))

    def _load_cache(self):
        if not self.cache_path.exists():
            return {}

        try:
            with open(self.cache_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {}

    def _save_cache(self, cache):
        self.cache_path.parent.mkdir(exist_ok=True)

        with open(self.cache_path, "w", encoding="utf-8") as file:
            json.dump(cache, file, indent=2, ensure_ascii=False)

    def _is_cache_valid(self, cached_item):
        if not cached_item:
            return False

        fetched_at_text = cached_item.get("fetched_at_utc")

        if not fetched_at_text:
            return False

        try:
            fetched_at = datetime.fromisoformat(fetched_at_text)
        except ValueError:
            return False

        age = datetime.now(timezone.utc) - fetched_at
        return age < self.cache_max_age

    def _fetch_tle_from_celestrak(self, norad_id):
        url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=TLE"

        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                text = response.read().decode("utf-8").strip()
        except Exception:
            return "", ""

        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if len(lines) < 2:
            return "", ""

        line1 = ""
        line2 = ""

        for index, line in enumerate(lines):
            if line.startswith("1 ") and index + 1 < len(lines):
                candidate_line2 = lines[index + 1]
                if candidate_line2.startswith("2 "):
                    line1 = line
                    line2 = candidate_line2
                    break

        if not line1 or not line2:
            return "", ""

        return line1, line2

    def _get_tle(self, norad_id):
        if not norad_id:
            return "", ""

        cache = self._load_cache()
        key = str(norad_id)
        cached_item = cache.get(key)

        if self._is_cache_valid(cached_item):
            return cached_item.get("line1", ""), cached_item.get("line2", "")

        line1, line2 = self._fetch_tle_from_celestrak(norad_id)

        if line1 and line2:
            cache[key] = {
                "norad_id": norad_id,
                "line1": line1,
                "line2": line2,
                "fetched_at_utc": datetime.now(timezone.utc).isoformat()
            }
            self._save_cache(cache)
            return line1, line2

        if cached_item:
            return cached_item.get("line1", ""), cached_item.get("line2", "")

        return "", ""

    def _load_satellites(self, path: str):
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Uydu dosyası bulunamadı: {path}")

        with open(path, "r", encoding="utf-8") as file:
            raw_satellites = json.load(file)

        satellites = {}

        for item in raw_satellites:
            name = item["name"]
            norad_id = item.get("norad_id")

            line1, line2 = self._get_tle(norad_id)

            satellite = None

            if line1 and line2:
                try:
                    satellite = EarthSatellite(line1, line2, name, self.ts)
                except Exception:
                    satellite = None
                    line1 = ""
                    line2 = ""

            satellites[name] = {
                "name": name,
                "display_name": item.get("display_name", name),
                "type": item.get("type", "UNKNOWN"),
                "country": item.get("country", "UNKNOWN"),
                "mission": item.get("mission", ""),
                "norad_id": norad_id,
                "line1": line1,
                "line2": line2,
                "tle_available": bool(satellite),
                "satellite": satellite
            }

        return satellites

    def list_satellites(self):
        return [
            {
                "name": item["name"],
                "display_name": item["display_name"],
                "type": item["type"],
                "country": item["country"],
                "mission": item["mission"],
                "norad_id": item["norad_id"],
                "tle_available": item["tle_available"]
            }
            for item in self.satellites.values()
        ]

    def get_satellite_state(
        self,
        satellite_name: str,
        observer_lat: float,
        observer_lon: float,
        observer_elevation_m: float = 0.0,
        dt: datetime | None = None
    ):
        if satellite_name not in self.satellites:
            raise ValueError(f"Uydu bulunamadı: {satellite_name}")

        satellite_data = self.satellites[satellite_name]

        if not satellite_data["tle_available"]:
            raise ValueError(f"Bu uydu için TLE verisi yok: {satellite_name}")

        if dt is None:
            dt = datetime.now(timezone.utc)

        if dt.tzinfo is None:
            raise ValueError("datetime timezone içermeli. UTC kullan.")

        t = self.ts.from_datetime(dt)
        satellite = satellite_data["satellite"]

        geocentric = satellite.at(t)
        subpoint = wgs84.subpoint(geocentric)

        observer = wgs84.latlon(
            observer_lat,
            observer_lon,
            elevation_m=observer_elevation_m
        )

        topocentric = (satellite - observer).at(t)
        altitude, azimuth, distance = topocentric.altaz()

        return {
            "satellite": satellite_name,
            "display_name": satellite_data["display_name"],
            "type": satellite_data["type"],
            "country": satellite_data["country"],
            "mission": satellite_data["mission"],
            "norad_id": satellite_data["norad_id"],
            "datetime_utc": dt.isoformat(),

            "subsatellite_lat_deg": float(subpoint.latitude.degrees),
            "subsatellite_lon_deg": float(subpoint.longitude.degrees),
            "subsatellite_elevation_km": float(subpoint.elevation.km),

            "observer_lat_deg": float(observer_lat),
            "observer_lon_deg": float(observer_lon),
            "observer_elevation_m": float(observer_elevation_m),

            "azimuth_deg": float(azimuth.degrees),
            "elevation_deg": float(altitude.degrees),
            "range_km": float(distance.km),

            "visible_from_observer": bool(altitude.degrees > 0)
        }
