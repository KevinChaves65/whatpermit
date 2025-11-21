import requests
from bs4 import BeautifulSoup


URL = "https://www.mississauga.ca/services-and-programs/building-and-renovating/building-permits/"

def scrape_mississauga():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    permits = []

    for section in soup.find_all(["h2", "h3"]):
        title = section.get_text(strip=True)

        permit = {
            "city": "Mississauga",
            "jobType": title.lower(),
            "permitRequired": True,
            "permitName": title,
            "documents": [],
            "authority": "City of Mississauga",
            "section": title,
            "url": URL
        }

        permits.append(permit)

    return permits
