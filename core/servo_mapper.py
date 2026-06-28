def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def azimuth_to_pan_angle(azimuth_deg):
    return azimuth_deg % 360


def elevation_to_tilt_angle(elevation_deg):
    return clamp(elevation_deg, 0, 90)


def make_servo_command(azimuth_deg, elevation_deg):
    pan = azimuth_to_pan_angle(azimuth_deg)
    tilt = elevation_to_tilt_angle(elevation_deg)

    return {
        "pan_deg": round(pan, 2),
        "tilt_deg": round(tilt, 2)
    }


def make_serial_command(azimuth_deg, elevation_deg):
    servo_command = make_servo_command(azimuth_deg, elevation_deg)

    pan = servo_command["pan_deg"]
    tilt = servo_command["tilt_deg"]

    return f"PAN:{pan},TILT:{tilt}"