from pathlib import Path
from geopy.geocoders import Nominatim
import requests
import pandas as pd

def get_forecast( city='Pittsburgh' ):
    '''
    '''

    geolocator = Nominatim(user_agent='ModernProgramming')
    location = geolocator.geocode(city)
    URL = f'https://api.weather.gov/points/{location.latitude},{location.longitude}'
    response = requests.get(URL)
    response = requests.get(response.json()['properties']['forecast'])
    periods = response.json()['properties']['periods']
    
    for period in periods:
      if period['name'] == 'Tonight':
        break

    return period

def main():
    period = get_forecast()

    file = 'weather.pkl'

    if Path(file).exists():
        df = pd.read_pickle( file )
    else:
        df = pd.DataFrame(columns=['Start Date', 'End Date', 'Forecast'])

    df = df.append({'Start Date': period['startTime'], 'End Date': period['endTime'], 'Forecast': period['detailedForecast']}, ignore_index=True)
    df = df.drop_duplicates()
    df.to_pickle(file)

    #sort repositories
    file = open("README.md", "w")
    file.write('# Pittsburgh Nightly Forecast\n\n')
    file.write(df.to_markdown(tablefmt='github'))
    file.write('\n\n---\nCopyright © 2022 Pittsburgh Supercomputing Center. All Rights Reserved.\n\nThe [Biomedical Applications Group](https://www.psc.edu/biomedical-applications/) at the [Pittsburgh Supercomputing Center](http://www.psc.edu) in the [Mellon College of Science](https://www.cmu.edu/mcs/) at [Carnegie Mellon University](http://www.cmu.edu).')
    file.close()

if __name__ == "__main__":
    main()
