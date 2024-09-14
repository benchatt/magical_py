class World:
    LOC_API = "https://ipinfo.io/loc"

    def navy_season_api_call(year) -> str:
        return f"https://aa.usno.navy.mil/api/seasons?year={year}"

    def navy_sun_moon_api_call(date: str, latitude: float, longitude: float, tz: int, dst: bool) -> str:
        return f"https://aa.usno.navy.mil/api/rstt/oneday?date={date}&coords={latitude},{longitude}&tz={tz}&dst={str(dst).lower()}"
