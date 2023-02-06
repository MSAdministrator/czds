"""Main entrypoint for czds."""
from typing import AnyStr
from typing import Dict
from typing import List

from .base import Base
from .connector import CZDSConnector
from .utils.exceptions import CZDSConnectionError


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

    def list_links(self) -> List[str]:
        """Returns a list of all CZDS Zone Link urls.

        Raises:
            CZDSConnectionError: Raises connection errors.

        Returns:
            List[str]: A list CZDS Zone Link urls.
        """
        try:
            self.connection = CZDSConnector()
        except CZDSConnectionError as cze:
            raise cze
        if not self.links:
            self.links = self.connection._get_zone_links()
        return self.links

    def get_zone(
        self, link: AnyStr = None, threaded: bool = False, output_format: AnyStr = None
    ) -> AnyStr or List[Dict[str, str]]:
        """Retrieves all or a single CZDS Zone File.

        If you DO NOT provide a link, we will retrieve all available link files from your account and return them.

        Args:
            link (AnyStr): A CZDS Zone Link URL. Defaults to None.
            threaded (bool): Whether or not to run multi-threaded.
            output_format (AnyStr): The output format for the parsed zone file.
                                    Accepts 'none','text' and 'json' at this time. Defaults to None.

        Raises:
            CZDSConnectionError: Raises connection errors.

        Returns:
            AnyStr or List[Dict[str, str]]: _description_
        """
        Base.OUTPUT_FORMAT = output_format
        return_list: List[Dict[str, str]] = []
        try:
            self.connection = CZDSConnector()
        except CZDSConnectionError as cze:
            raise cze
        if link:
            return_list.append(self.connection._get(url=link))
        else:
            if threaded:
                return self.run_threaded(method=self.connection.download, list_data=self.list_links())
            else:
                for link in self.list_links():
                    self.__logger.info(f"Downloading zone file from '{link}'.")
                    return_list.append(self.connection.download(zone_file_list=link))
        return return_list
