import requests
from datetime import datetime, timezone, timedelta
from subprocess import check_output
from .constants import World

DAYTIME_FMT = "%I:%M:%S %p"
GOOD_FMT = "%H:%M:%S"
FULL_DATE_FMT = "%Y-%m-%d %H:%M:%S"

def convert_tz(dt):
    raw_offset = check_output(["date", "+%z"]).strip().decode()
    minutes = int(raw_offset[-2:])
    hours = int(raw_offset[:-2])
    sign = -1 if hours < 0 else 1
    delta = timedelta(hours=hours, minutes=(minutes * sign))
    return dt + delta

def convert_navy_phenom(dct: dict):
    (hour, minute) = dct.get("time").split(":")
    return datetime(
        int(dct.get("year")),
        int(dct.get("month")),
        int(dct.get("day")),
        hour=int(hour),
        minute=int(minute)
    )

class Day:
    def __init__(self):
        # Get location, then sunrise API response
        loc = requests.get(World.LOC_API).content.strip().decode()
        (self.latitude, self.longitude) = loc.split(',')
        sun_rs = requests.get(World.sunset_api_call(self.latitude, self.longitude))
        sunjson = sun_rs.json().get("results")

        # Parse API response into displayable times
        sunrise_obj = datetime.strptime(sunjson.get("sunrise"), DAYTIME_FMT)
        self.sunrise = convert_tz(sunrise_obj).strftime(GOOD_FMT)
        sunset_obj = datetime.strptime(sunjson.get("sunset"), DAYTIME_FMT)
        self.sunset = convert_tz(sunset_obj).strftime(GOOD_FMT)
        noon_obj = datetime.strptime(sunjson.get("solar_noon"), DAYTIME_FMT)
        self.noon = convert_tz(noon_obj).strftime(GOOD_FMT)
        self.daylight = sunjson.get("day_length")

    def __repr__(self):
        output_str = ""
        output_str = output_str + f"Current location: {self.latitude}, {self.longitude}\n"
        output_str = output_str + f"Current date & time: {datetime.now().strftime(FULL_DATE_FMT)}\n"
        output_str = output_str + f"Sunrise: {self.sunrise}\n"
        output_str = output_str + f"Noon   : {self.noon}\n"
        output_str = output_str + f"Sunset : {self.sunset}\n"
        output_str = output_str + f"Daylight Hours : {self.daylight}\n"
        return output_str

class Year:
    def __init__(self):
        # Get current date and time, get Navy seasons API response
        now = datetime.utcnow()
        year = now.year
        phenoms = requests.get(World.navy_season_api_call(year)).json()

        # Parse API response into Equinoxes and Solstices
        equinoxes = [entry for entry in phenoms.get("data") if entry.get("phenom") == "Equinox"]
        solstices = [entry for entry in phenoms.get("data") if entry.get("phenom") == "Solstice"]
        (march_equinox_dt, sept_equinox_dt) = [convert_navy_phenom(e) for e in equinoxes]
        (june_solstice_dt, dec_solstice_dt) = [convert_navy_phenom(s) for s in solstices]

        # If before march equinox or dec solstice, we care about season events from other years
        if now >= dec_solstice_dt:
            phenoms = requests.get(World.navy_season_api_call(year+1)).json()
            next_march_eq = [p for p in phenoms if p.get("month") == 3 and p.get("phenom") == "Equinox"][0]
            march_equinox_dt = convert_navy_phenom(next_march_eq)
        elif now < march_equinox_dt:
            phenoms = requests.get(World.navy_season_api_call(year-1)).json()
            past_dec_sol = [p for p in phenoms if p.get("month") == 12 and p.get("phenom") == "Solstice"][0]
            dec_solstice_dt = convert_navy_phenom(past_dec_sol)

        # Get hemisphere
        loc = requests.get(World.LOC_API).content.strip().decode()
        (latitude, _) = loc.split(',')
        southern_hem = float(latitude) < 0

        # Get season
        seasons = ["Spring", "Summer", "Autumn", "Winter"]
        if march_equinox_dt <= now < june_solstice_dt:
            index = 0
            last_event = march_equinox_dt
            next_event = june_solstice_dt
        elif june_solstice_dt <= now < sept_equinox_dt:
            index = 1
            last_event = june_solstice_dt
            next_event = sept_equinox_dt
        elif sept_equinox_dt <= now < dec_solstice_dt:
            index = 2
            last_event = sept_equinox_dt
            next_event = dec_solstice_dt
        elif dec_solstice_dt <= now < march_equinox_dt:
            index = 3
            last_event = dec_solstice_dt
            next_event = march_equinox_dt

        # Find days since and days until
        last_td = now - last_event
        next_td = next_event - now
        self.days_since_last_event = last_td.days
        self.days_until_next_event = next_td.days

        if southern_hem:
            index = 3 - index

        if index == 0:
            self.last_season = seasons[3]
        else:
            self.last_season = seasons[index-1]

        if index == 3:
            self.next_season = seasons[0]
        else:
            self.next_season = seasons[index+1]

        self.season = seasons[index]

    def __repr__(self):
        output_str = ""
        output_str = output_str + f"Current season is {self.season}\n"
        output_str = output_str + f"{self.days_since_last_event} days since end of {self.last_season}.\n"
        output_str = output_str + f"{self.days_until_next_event} days until start of {self.next_season}.\n"
        return output_str

class Moon:
    def __init__(self, latitude, longitude):
