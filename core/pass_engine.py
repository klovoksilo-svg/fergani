from datetime import datetime, timezone, timedelta


def find_visible_passes(
    engine,
    satellite_name,
    observer_lat,
    observer_lon,
    observer_elevation_m,
    hours_ahead=24,
    step_minutes=1
):
    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(hours=hours_ahead)
    step = timedelta(minutes=step_minutes)

    passes = []
    current_pass = []

    current_time = start_time

    while current_time <= end_time:
        try:
            result = engine.get_satellite_state(
                satellite_name=satellite_name,
                observer_lat=observer_lat,
                observer_lon=observer_lon,
                observer_elevation_m=observer_elevation_m,
                dt=current_time
            )
        except ValueError:
            return []

        if result["visible_from_observer"]:
            current_pass.append(result)
        else:
            if current_pass:
                passes.append(current_pass)
                current_pass = []

        current_time += step

    if current_pass:
        passes.append(current_pass)

    return passes


def get_best_pass(visible_passes):
    if not visible_passes:
        return None

    return max(
        visible_passes,
        key=lambda visible_pass: max(
            item["elevation_deg"] for item in visible_pass
        )
    )