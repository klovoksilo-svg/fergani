from pathlib import Path
from datetime import datetime, timezone, timedelta

from core.orbit_engine import OrbitEngine
from core.pass_engine import find_visible_passes, get_best_pass


def utc_iso_to_turkey_time_text(utc_iso_text):
    turkey_timezone = timezone(timedelta(hours=3))
    utc_time = datetime.fromisoformat(utc_iso_text)
    turkey_time = utc_time.astimezone(turkey_timezone)

    return turkey_time.strftime("%Y-%m-%d %H:%M:%S")


def main():
    engine = OrbitEngine("data/satellites.json")

    satellite_name = "ISS TEST"

    observer_lat = 39.9334
    observer_lon = 32.8597
    observer_elevation_m = 900

    passes = find_visible_passes(
        engine=engine,
        satellite_name=satellite_name,
        observer_lat=observer_lat,
        observer_lon=observer_lon,
        observer_elevation_m=observer_elevation_m,
        hours_ahead=24,
        step_minutes=1
    )

    best_pass = get_best_pass(passes)

    print("=== GEÇİŞ ARAMA TESTİ ===")
    print(f"Uydu: {satellite_name}")
    print("Aralık: Önümüzdeki 24 saat")
    print("Kontrol aralığı: 1 dakika")
    print()

    if best_pass is None:
        print("Önümüzdeki 24 saat içinde görünür geçiş bulunamadı.")
        return

    print(f"Bulunan görünür geçiş sayısı: {len(passes)}")
    print()

    first = best_pass[0]
    last = best_pass[-1]
    max_point = max(best_pass, key=lambda item: item["elevation_deg"])

    start_tr = utc_iso_to_turkey_time_text(first["datetime_utc"])
    end_tr = utc_iso_to_turkey_time_text(last["datetime_utc"])
    max_tr = utc_iso_to_turkey_time_text(max_point["datetime_utc"])

    print("--- En iyi geçiş ---")
    print(f"Başlangıç TR  : {start_tr}")
    print(f"Bitiş TR      : {end_tr}")
    print(f"Süre          : yaklaşık {len(best_pass)} dakika")
    print(f"Maks. elevasyon: {max_point['elevation_deg']:.2f} derece")
    print(f"Maks. elevasyon zamanı TR: {max_tr}")
    print(f"Başlangıç azimut: {first['azimuth_deg']:.2f}")
    print(f"Bitiş azimut    : {last['azimuth_deg']:.2f}")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    pass_file = output_dir / "best_pass.txt"

    pass_text = (
        f"Uydu: {satellite_name}\n"
        f"Başlangıç TR: {start_tr}\n"
        f"Bitiş TR: {end_tr}\n"
        f"Süre: yaklaşık {len(best_pass)} dakika\n"
        f"Maksimum elevasyon: {max_point['elevation_deg']:.2f} derece\n"
        f"Maksimum elevasyon zamanı TR: {max_tr}\n"
        f"Başlangıç azimut: {first['azimuth_deg']:.2f}\n"
        f"Bitiş azimut: {last['azimuth_deg']:.2f}\n"
    )

    pass_file.write_text(pass_text, encoding="utf-8")

    print()
    print("En iyi geçiş dosyaya yazıldı:")
    print(pass_file)


if __name__ == "__main__":
    main()