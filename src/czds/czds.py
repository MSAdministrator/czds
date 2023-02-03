"""Main entrypoint for czds."""
from typing import AnyStr
from typing import Dict
from typing import List

from .base import Base
from .connector import CZDSConnector


class CZDS(Base):
    """Main class for ICAAN CZDS."""

    links: List[str] = []

    def __init__(self, username: AnyStr, password: AnyStr, save_directory: AnyStr) -> None:
        """Sets the username and password for API authentication.

        Args:
            username (AnyStr): The username to access CZDS.
            password (AnyStr): The password to access CZDS.
            save_directory (AnyStr): The directory to save zone files to.
        """
        Base.USERNAME = username
        Base.PASSWORD = password
        Base.SAVE_PATH = save_directory
        self.connection = CZDSConnector()

    def list_links(self) -> List[str]:
        """Returns a list of all CZDS Zone Link urls.

        Returns:
            List[str]: A list CZDS Zone Link urls.
        """
        if not self.links:
            self.links = self.connection._get_zone_links()
        return self.links

    def get_zone(self, link: AnyStr = None) -> AnyStr or List[Dict[str, str]]:
        """Retrieves all or a single CZDS Zone File.

        If you DO NOT provide a link, we will retrieve all available link files from your account and return them.

        Args:
            link (AnyStr): A CZDS Zone Link URL. Defaults to None.

        Returns:
            AnyStr or List[Dict[str, str]]: _description_
        """
        return_list: List[Dict[str, str]] = []
        if link:
            return_list.append(self.connection._get(url=link))
        else:
            for link in self.list_links():
                self.__logger.info(f"Downloading zone file from '{link}'.")
                return_list.append(self.connection.download(zone_file_link=link))
        return return_list
