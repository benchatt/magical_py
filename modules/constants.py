class World:
    LOC_API = "https://ipinfo.io/loc"

    def sunset_api_call(latitude, longitude) -> str:
        return f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}"

    def navy_season_api_call(year) -> str:
        return f"https://aa.usno.navy.mil/api/seasons?year={year}"

    def moon_phase_api_call(latitude, longitude) -> str:
        return f"https://moon-phase.p.rapidapi.com/basic?lat={latitude}&lon={longitude}"
