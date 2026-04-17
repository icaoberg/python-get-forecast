import sys
from pathlib import Path
from geopy.geocoders import Nominatim
import requests
import pandas as pd

CITY = "Pittsburgh"
DATA_FILE = "weather.parquet"
GITHUB_USER = "icaoberg"
REPO_NAME = "python-get-forecast"


def get_forecast(city=CITY):
    """
    Retrieves the nightly weather forecast for a specified city.

    Uses the Nominatim geocoding service to obtain coordinates, then queries
    the National Weather Service (NWS) API for the "Tonight" forecast period.

    :param city: The name of the city for which to retrieve the forecast.
    :type city: str
    :return: A dictionary containing the weather forecast for "Tonight".
    :rtype: dict
    :raises ValueError: If the city cannot be geocoded or Tonight forecast
        is unavailable.
    :raises requests.RequestException: If any API request fails.
    """
    geolocator = Nominatim(user_agent="ModernProgramming")
    location = geolocator.geocode(city)
    if location is None:
        raise ValueError(f"Could not geocode city: '{city}'")

    url = (
        f"https://api.weather.gov/points/"
        f"{location.latitude},{location.longitude}"
    )
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    forecast_url = response.json()["properties"]["forecast"]
    response = requests.get(forecast_url, timeout=10)
    response.raise_for_status()

    periods = response.json()["properties"]["periods"]
    if not periods:
        raise ValueError("NWS API returned no forecast periods.")

    for period in periods:
        if period["name"] == "Tonight":
            return period

    raise ValueError(
        f"No 'Tonight' forecast period available for '{city}'."
    )


def main():
    """
    Retrieves the nightly forecast and updates the data file and README.

    Calls get_forecast(), appends the result to the historical DataFrame
    stored in DATA_FILE, deduplicates, and regenerates README.md.

    :return: None
    """
    try:
        period = get_forecast()
    except (ValueError, requests.RequestException) as e:
        print(f"Error fetching forecast: {e}", file=sys.stderr)
        sys.exit(1)

    if Path(DATA_FILE).exists():
        df = pd.read_parquet(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["Start Date", "End Date", "Forecast"])

    datum = {
        "Start Date": period["startTime"],
        "End Date": period["endTime"],
        "Forecast": period["detailedForecast"],
    }
    df = pd.concat([df, pd.DataFrame([datum])], ignore_index=True)
    df = df.drop_duplicates()
    df.to_parquet(DATA_FILE, compression="zstd")

    badge_url = (
        f"https://github.com/{GITHUB_USER}/{REPO_NAME}"
        "/actions/workflows/build.yml/badge.svg"
    )
    with open("README.md", "w") as file:
        file.write(f"![Status]({badge_url})\n")
        file.write(f"# {CITY} Nightly Forecast\n\n")
        file.write(df.to_markdown(tablefmt="github"))
        file.write(
            "\n\n---\nCopyright © 2022-2026 Pittsburgh Supercomputing "
            "Center. All Rights Reserved."
        )


if __name__ == "__main__":
    main()
