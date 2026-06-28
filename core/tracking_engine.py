from core.servo_mapper import make_servo_command, make_serial_command


def get_tracking_snapshot(
    engine,
    satellite_name,
    observer_lat,
    observer_lon,
    observer_elevation_m
):
    result = engine.get_satellite_state(
        satellite_name=satellite_name,
        observer_lat=observer_lat,
        observer_lon=observer_lon,
        observer_elevation_m=observer_elevation_m
    )

    servo_command = make_servo_command(
        azimuth_deg=result["azimuth_deg"],
        elevation_deg=result["elevation_deg"]
    )

    serial_command = make_serial_command(
        azimuth_deg=result["azimuth_deg"],
        elevation_deg=result["elevation_deg"]
    )

    return {
        "satellite_state": result,
        "servo_command": servo_command,
        "serial_command": serial_command
    }