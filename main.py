from pathlib import Path
from time import sleep

from core.orbit_engine import OrbitEngine
from core.tracking_engine import get_tracking_snapshot


def main():
    engine = OrbitEngine("data/satellites.json")

    satellite_name = "ISS TEST"

    observer_lat = 39.9334
    observer_lon = 32.8597
    observer_elevation_m = 900

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    command_file = output_dir / "last_command.txt"

    print("=== CANLI UYDU TAKİP TESTİ ===")
    print("10 saniye boyunca her saniye yeni konum hesaplanacak.")
    print()

    for i in range(10):
        snapshot = get_tracking_snapshot(
            engine=engine,
            satellite_name=satellite_name,
            observer_lat=observer_lat,
            observer_lon=observer_lon,
            observer_elevation_m=observer_elevation_m
        )

        result = snapshot["satellite_state"]
        servo_command = snapshot["servo_command"]
        serial_command = snapshot["serial_command"]

        command_file.write_text(serial_command, encoding="utf-8")

        print(f"[{i + 1}/10]")
        print(f"Uydu izdüşümü: {result['subsatellite_lat_deg']:.4f}, {result['subsatellite_lon_deg']:.4f}")
        print(f"Azimut: {result['azimuth_deg']:.2f} | Elevasyon: {result['elevation_deg']:.2f}")
        print(f"PAN: {servo_command['pan_deg']} | TILT: {servo_command['tilt_deg']}")
        print(f"Komut: {serial_command}")

        if result["visible_from_observer"]:
            print("Durum: GÖRÜNÜR")
        else:
            print("Durum: GÖRÜNMEZ / ufkun altında")

        print("-" * 40)

        sleep(1)


if __name__ == "__main__":
    main()