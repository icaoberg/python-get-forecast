from pathlib import Path
from geopy.geocoders import Nominatim
import requests
import pandas as pd


def get_forecast(city="Pittsburgh"):
    """
    Retrieves the weather forecast for a specified city.

    This function uses the Nominatim geocoding service to obtain the latitude and longitude
    coordinates of the specified city. It then constructs a URL to access the weather forecast
    data using the National Weather Service (NWS) API. The API response is processed to extract
    the forecast periods, and the forecast for the "Tonight" period is returned.

    :param city: The name of the city for which to retrieve the weather forecast (default: Pittsburgh).
    :type city: str
    :return: A dictionary containing the weather forecast for the "Tonight" period.
    :rtype: dict
    """

    geolocator = Nominatim(user_agent="ModernProgramming")
    location = geolocator.geocode(city)
    URL = f"https://api.weather.gov/points/{location.latitude},{location.longitude}"
    response = requests.get(URL)
    response = requests.get(response.json()["properties"]["forecast"])
    periods = response.json()["properties"]["periods"]
    for period in periods:
        if period["name"] == "Tonight":
            break

    return period


def main():
    """
    Retrieves the weather forecast for a specified city and updates a DataFrame and README file.

    This function calls the `get_forecast` function to retrieve the weather forecast for a city
    (defaulting to Pittsburgh). It then updates a DataFrame containing forecast information. If
    a DataFrame file named "weather.pkl" exists, it loads the DataFrame; otherwise, it initializes
    a new DataFrame. The retrieved forecast information is appended to the DataFrame, and duplicate
    entries are removed. The updated DataFrame is saved back to the "weather.pkl" file.

    Additionally, this function generates a README markdown file for a GitHub repository. It includes
    badges indicating the status of repository workflows and presents the nightly forecast for Pittsburgh.
    The forecast information is formatted using the DataFrame's `to_markdown` method. Finally, a copyright
    notice is added to the README file.

    :return: None
    """

    period = get_forecast()
    file = "weather.pkl"

    if Path(file).exists():
        df = pd.read_pickle(file)
    else:
        df = pd.DataFrame(columns=["Start Date", "End Date", "Forecast"])

    datum = {
        "Start Date": period["startTime"],
        "End Date": period["endTime"],
        "Forecast": period["detailedForecast"],
    }
    df = pd.concat([df, pd.DataFrame([datum])], ignore_index=True)

    df = df.drop_duplicates()
    df.to_pickle(file)

    # sort repositories
    file = open("README.md", "w")
    file.write(
        "![Status](https://github.com/icaoberg/"
        + "python-get-forecast/actions/workflows/build.yml/badge.svg)\n"
    )
    #file.write(
    #    "![Status](https://github.com/icaoberg/"
    #    + "python-get-forecast/actions/workflows/pretty.yml/badge.svg)\n"
    #)
    file.write("# Pittsburgh Nightly Forecast\n\n")
    file.write(df.to_markdown(tablefmt="github"))
    file.write(
        "\n\n---\nCopyright © 2022-2024 Pittsburgh Supercomputing "
        + "Center. All Rights Reserved."
    )
    file.close()


if __name__ == "__main__":
    main()
