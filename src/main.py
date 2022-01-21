#Python 3.9.5

from ratelimit import limits
from bs4 import BeautifulSoup
import requests
from requests import compat
import pandas as pd

class BoltScraper:

    def __init__(self, main_url) -> None:
        self.bolt_cities = []
        self.main_url = main_url


    @limits(calls=20,period=1) # makes sure this function can only be called 20 / second
    def _make_request(self, url):
        try:
            return requests.get(url)
        except Exception as e:
            print(e)
            

    def get_services(self,output_name):
        # Get main body
        main_body = self._make_request(self.main_url)
        main_soup = BeautifulSoup(main_body.text, 'html.parser')
        continents = main_soup.find_all("div", {"class":"mt-40 mt-md-56"})
        for continent in continents:
            continent_name = continent.find("h4").getText()
            countries = continent.find_all("div", {"mt-32 mr-16 column-section"})
            print(continent_name, len(countries))
            for country in countries:
                country_name = country.find("label").getText()
                cities = country.find_all("div", {"mt-16"})
                print(country_name, len(cities))
                for city in cities:
                    city_tag = city.find("a")
                    city_name = city_tag.getText()
                    city_url = compat.urljoin(self.main_url,city_tag.get("href")) 
                    city_body = self._make_request(city_url)
                    city_soup = BeautifulSoup(city_body.text, 'html.parser')
                    food = city_soup.find("div",{"food-delivery-block"})
                    if food:
                        bolt_food = True
                    else:
                        bolt_food = False
                    services_dict = {}
                    services_container = city_soup.find("div", {"container services-container"})
                    if services_container is not None:
                        services = services_container.find_all("div", {"service-card"})
                        service_names = []
                        for service in services:
                            service_content = service.find("div",{"card-content"})
                            service_name = service_content.find("div").getText()
                            service_names.append(service_name)
                        services_dict = {s: True for s in service_names}
                    city_info = {
                        "continent" : continent_name,
                        "country" : country_name,
                        "city" : city_name,
                        "url" : city_url,
                        "bolt_food" : bolt_food
                    }
                    self.bolt_cities.append(city_info | services_dict)
        df = pd.DataFrame(self.bolt_cities)
        df.to_csv(f"{output_name}.csv", index=False)


if __name__ == "__main__":
    bolt_cities_url = "https://bolt.eu/en/cities/"
    scraper = BoltScraper(bolt_cities_url)
    csv_output_name = "bolt_cities"
    scraper.get_services(csv_output_name)