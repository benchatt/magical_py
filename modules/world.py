import requests
from datetime import datetime, timezone, timedelta
import time
from subprocess import check_output
from .constants import World

DAYTIME_FMT = "%I:%M:%S %p"
GOOD_FMT = "%H:%M:%S"
FULL_DATE_FMT = "%A %Y-%m-%d %H:%M:%S"
UTC_OFFSET_STANDARD = -(time.timezone / 3600)
DAYLIGHT_SAVING = time.daylight

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
        self.date_time = datetime.now().strftime(FULL_DATE_FMT)
        # Following breaks if day of week has space
        (day_of_week, date_, time_) = self.date_time.split(" ")
        (self.latitude, self.longitude) = loc.split(',')
        day_rs = requests.get(World.navy_sun_moon_api_call(date_, self.latitude, self.longitude, UTC_OFFSET_STANDARD, DAYLIGHT_SAVING == 1))
        sun_moon_json = day_rs.json().get("properties").get("data")

        # Parse API response into displayable times
        sundata = sun_moon_json.get("sundata")
        self.sunrise = next(p for p in sundata if p.get("phen") == "Rise").get("time").split(" ")[0]
        self.sunset = next(p for p in sundata if p.get("phen") == "Set").get("time").split(" ")[0]
        self.noon = next(p for p in sundata if p.get("phen") == "Upper Transit").get("time").split(" ")[0]

        closestphase = sun_moon_json.get("closestphase")
        self.closest_phase_name = closestphase.get("phase")
        cphase_time = closestphase.get("time").split(" ")[0]
        closest_phase_dt = datetime(
            year=closestphase.get("year"),
            month=closestphase.get("month"),
            day=closestphase.get("day"),
            hour=int(cphase_time.split(":")[0]),
            minute=int(cphase_time.split(":")[1])
        )
        self.closest_phase_stamp = closest_phase_dt.strftime(FULL_DATE_FMT)
        self.current_phase = sun_moon_json.get("curphase") + f" ({sun_moon_json.get('fracillum')})"

        moondata = sun_moon_json.get("moondata")
        self.moonrise = next(p for p in moondata if p.get("phen") == "Rise").get("time").split(" ")[0]
        self.moonset = next(p for p in moondata if p.get("phen") == "Set").get("time").split(" ")[0]

    def __repr__(self):
        output_str = ""
        output_str = output_str + f"Current location: {self.latitude}, {self.longitude}\n"
        output_str = output_str + f"Current date & time: {self.date_time}\n"
        output_str = output_str + f"Sunrise: {self.sunrise}\n"
        output_str = output_str + f"Noon   : {self.noon}\n"
        output_str = output_str + f"Sunset : {self.sunset}\n"
        # output_str = output_str + f"Daylight Hours : {self.daylight}\n"

        output_str = output_str + "\nMoon\n"
        output_str = output_str + f"Current Phase: {self.current_phase}\n"
        output_str = output_str + f"Closest Phase: {self.closest_phase_name}\n"
        output_str = output_str + f"         Time: {self.closest_phase_stamp}\n\n"

        if self.moonset < self.moonrise:
            output_str = output_str + f"Moonset : {self.moonset}\n"
            output_str = output_str + f"Moonrise: {self.moonrise}\n"
        else:
            output_str = output_str + f"Moonrise: {self.moonrise}\n"
            output_str = output_str + f"Moonset : {self.moonset}\n"
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
        lengthening = self.season.lower() == "winter" or self.season.lower() == "spring"
        first_half = self.days_since_last_event <= self.days_until_next_event
        quickly = (
            first_half and (self.season.lower() == "autumn" or self.season.lower() == "spring")
            or (not first_half) and (self.season.lower() == "summer" or self.season.lower == "winter")
        )
        length_word = "lengthening" if lengthening else "shortening"
        quick_word = "quickly" if quickly else "slowly"
        output_str = output_str + f"Days are {length_word} {quick_word}."
        return output_str
