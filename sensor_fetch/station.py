
def fetch():
    """
    Fetch PM2.5 station data and uvi station data

    API:
    PM2.5: http://opendata.epa.gov.tw/ws/Data/AQXSite/
    UVI: http://opendata.epa.gov.tw/ws/Data/UV/

    Returns:
        station_data: a dict contain uvi and pm25 stations
        Format:
            {
                "uvi": [
                    {
                        "Lon": 120,
                        "Lat": 25,
                        "SiteName": "SiteA"
                    },
                    ...
                ],
                "pm25" [
                    {
                        "Lon": 125,
                        "Lat": 23,
                        "SiteName": "SiteB"
                    },
                    ...
                ]
            }
    """
    pass