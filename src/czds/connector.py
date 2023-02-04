"""Main connector class."""
import cgi
import json
import os
from typing import AnyStr
from typing import List

import requests
from requests import Response

from .base import Base


class CZDSConnector(Base):
    """Main CZDS connection classself.

    All API Calls go through this class.
    """

    def __init__(self) -> None:
        """Creates a credential property and retrieves our access token from authenticationself."""
        self.credential: dict = {"username": Base.USERNAME, "password": Base.PASSWORD}
        self.token = self.get_token()

    def get_token(self) -> AnyStr:
        """Authenticates and retrieves access token for all other API calls.

        Returns:
            AnyStr: An access token.
        """
        response = requests.post(self.AUTH_URL, data=json.dumps(self.credential), headers=self.BASE_HEADERS)

        status_code = response.status_code

        # Return the access_token on status code 200. Otherwise, terminate the program.
        if status_code == 200:
            self.__logger.info("Status code is 200.")
            access_token = response.json()["accessToken"]
            return access_token
        elif status_code == 404:
            self.__logger.critical(f"Invalid URL '{self.AUTH_URL}'. Received a 404 status code.")
            exit(1)
        elif status_code == 401:
            self.__logger.critical("Invalid username/password. Please reset your password via web.")
            exit(1)
        elif status_code == 500:
            self.__logger.critical("Internal server error. Please try again later.")
            exit(1)
        else:
            self.__logger.critical(f"Failed to authenticate with error code {status_code}")
            exit(1)

    def _get(self, url: AnyStr) -> Response:
        """This method is used to make all calls to CZDS.

        Args:
            url (AnyStr): The URL to make the request against.

        Returns:
            Response: A requests.Response object.
        """
        headers = Base.BASE_HEADERS
        headers.update({"Authorization": f"Bearer {self.token}"})
        self.__logger.debug(f"Making request to '{url}'.")
        return requests.get(url, params=None, headers=headers, stream=True)

    def _get_zone_links(self) -> List[str]:
        """Retrieves all available CZDS zone file links.

        Returns:
            List[str]: A list of available CZDS zone file links.
        """
        links_url = self.BASE_URL + "/czds/downloads/links"
        links_response = self._get(links_url)

        status_code = links_response.status_code

        if status_code == 200:
            return links_response.json()
        elif status_code == 401:
            self.token = self.get_token()
            self._get_zone_links()
        else:
            self.__logger.critical(f"Failed to get zone links from {links_url} with error code {status_code}\n")
            return None

    def _download_single_zone_file(self, zone_file_link: AnyStr) -> AnyStr:
        """Downloas the zone file from the provided URL.

        Args:
            zone_file_link (AnyStr): A CZDS Zone file to download from.

        Returns:
            AnyStr: The path that the zone file was downloaded to.
        """
        response = self._get(zone_file_link)
        status_code = response.status_code

        if status_code == 200:
            zone_name = zone_file_link.rsplit("/", 1)[-1].rsplit(".")[-2]

            # Try to get the filename from the header
            _, option = cgi.parse_header(response.headers["content-disposition"])
            filename = option["filename"]

            # If could get a filename from the header, then makeup one like [tld].txt.gz
            if not filename:
                filename = zone_name + ".txt"
            path = os.path.join(Base.SAVE_PATH, filename)
            with open(path, "wb") as f:
                for chunk in response.raw.stream(1024, decode_content=False):
                    if chunk:
                        f.write(chunk)
            return path
        elif status_code == 401:
            self.__logger.info("The access_token has been expired. Re-authenticating.")
            self.token = self.get_token()
            return self._download_single_zone_file(zone_file_link=zone_file_link)
        elif status_code == 404:
            self.__logger.warning(f"No zone file found for '{zone_file_link}'.")
        else:
            self.__logger.critical(f"Failed to download zone from '{zone_file_link}' with code {status_code}\n")

    def download(self, zone_file_list: AnyStr or List[AnyStr]) -> AnyStr:
        """Main method used to download zone files.

        Args:
            zone_file_link (AnyStr): One or more zone file(s) to download.

        Returns:
            AnyStr or List[AnyStr]: The path that the zone file was saved to.
        """
        if Base.SAVE_PATH:
            if not os.path.exists(Base.SAVE_PATH):
                os.makedirs(Base.SAVE_PATH)
        if isinstance(zone_file_list, list):
            return [self._download_single_zone_file(zone_file_link=link) for link in zone_file_list]
        elif isinstance(zone_file_list, str):
            return self._download_single_zone_file(zone_file_link=zone_file_list)
        else:
            self.__logger.critical(f"Unable to download. Unknown data structure provided to this method. {zone_file_list}")
            raise TypeError(f"Unknown data type. Should be 'list' or 'str'.")
