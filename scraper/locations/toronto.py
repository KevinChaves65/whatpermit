import requests
from bs4 import BeautifulSoup

URL = "https://www.toronto.ca/services-payments/building-construction/apply-for-a-building-permit/"

def scrape_toronto():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    permits = []

    for section in soup.find_all(["h2", "h3"]):
        title = section.get_text(strip=True)

        permit = {
            "city": "Toronto",
            "jobType": title.lower(),
            "permitRequired": True,
            "permitName": title,
            "documents": [],
            "authority": "City of Toronto",
            "section": title,
            "url": URL
        }

        permits.append(permit)

    return permits
