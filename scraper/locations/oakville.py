import requests
from bs4 import BeautifulSoup


URL = "https://www.oakville.ca/home-environment/building-renovations/building-permits-inspections/building-permits/"




def scrape_oakville():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    permits = []

    for section in soup.find_all(["h2", "h3"]):
        title = section.get_text(strip=True)

        permit = {
            "city": "Oakville",
            "jobType": title.lower(),
            "permitRequired": True,
            "permitName": title,
            "documents": [],
            "authority": "City of Oakville",
            "section": title,
            "url": URL
        }

        permits.append(permit)

    return permits
