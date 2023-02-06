"""Main connector class."""
import cgi
import json
import os
import zlib
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import List

from requests import Response
from requests import Session
from requests.exceptions import HTTPError

from .base import Base
from .utils.exceptions import CZDSConnectionError
from .utils.exceptions import UnsupportedTypeError


class CZDSConnector(Base):
    """Main CZDS connection classself.

    All API Calls go through this class.
    """

    def __init__(self) -> None:
        """Creates a credential property and retrieves our access token from authenticationself."""
        self.credential: dict = {"username": Base.USERNAME, "password": Base.PASSWORD}
        self.token = self.get_token()

    def _parse_line(self, line: AnyStr) -> Dict[str, str]:
        """Parses a line from a zone file into a dictionary.

        Args:
            line (AnyStr): A line from a zone file.

        Returns:
            Dict[str, str]: A dictionary of the line.
        """
        count = 1
        zone_dict = {}
        record_data_list = []
        for item in line.split():
            if count == 1:
                zone_dict["dns_record"] = item.rstrip(".")
            elif count == 2:
                try:
                    int(item)
                    zone_dict["ttl"] = item
                except Exception as e:
                    zone_dict["record_class"] = item
            elif count == 3:
                if zone_dict.get("record_class"):
                    zone_dict["ttl"] = item
                else:
                    zone_dict["record_class"] = item
            elif count == 4:
                zone_dict["record_type"] = item
            else:
                record_data_list.append(item)
            count += 1
        zone_dict["record_data"] = " ".join(record_data_list)
        return zone_dict

    def _request(
        self,
        url: AnyStr,
        method: AnyStr = "GET",
        data: Any = None,
        headers: Dict[str, str] = None,
        stream: bool = False,
    ) -> Response:
        """Main method to make all HTTP requests.

        Args:
            url (AnyStr): The URL to send the request to.
            method (AnyStr): The HTTP method to use. Defaults to "GET".
            data (Any): The data argument provided to requests. Defaults to None.
            headers (Dict[str, str], optional): The headers to use with the request. Defaults to None.
            stream (bool): Whether or not to stream response content. Defaults to False.

        Raises:
            CZDSConnectionError: Raises when a connection error occurs.

        Returns:
            Response: The requests Response object.
        """
        response = Session().request(method=method, url=url, headers=headers, data=data, stream=stream)
        try:
            response.raise_for_status()
        except HTTPError as error:
            if error.response.status_code == 404:
                raise CZDSConnectionError(status_code=error.response.status_code, name="InvalidURL", http_error=error)
            elif error.response.status_code == 401:
                raise CZDSConnectionError(status_code=401, name="InvalidAuthentication", http_error=error)
            elif error.response.status_code == 500:
                raise CZDSConnectionError(status_code=500, name="InternalServerError", http_error=error)
            else:
                raise CZDSConnectionError(status_code=error.response.status_code, name="UnknownError", http_error=error)
        return response

    def get_token(self) -> AnyStr:
        """Authenticates and retrieves access token for all other API calls.

        Returns:
            AnyStr: An access token.
        """
        return self._request(
            method="POST", url=self.AUTH_URL, data=json.dumps(self.credential), headers=self.BASE_HEADERS
        ).json()["accessToken"]

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
        return self._request(url=url, headers=headers, stream=True)

    def _get_zone_links(self) -> List[str]:
        """Retrieves all available CZDS zone file links.

        Returns:
            List[str]: A list of available CZDS zone file links.
        """
        links_url = self.BASE_URL + "/czds/downloads/links"
        return self._get(links_url).json()

    def _output_to_disk(self, response: Response, file_path: AnyStr) -> None:
        """Writes the response content to disk.

        Args:
            response (Response): The response object to write to disk.
            file_path (AnyStr): The path to write the response content to.
        """
        with open(file_path, "wb") as f:
            for chunk in response.raw.stream(1024, decode_content=False):
                if chunk:
                    f.write(chunk)

    def _output_to_text_stream(self, response: Response, file_path: AnyStr) -> List[AnyStr]:
        """Writes the response content to stdout.

        Args:
            response (Response): The response object to write to stdout.
            file_path (AnyStr): The path to write the response content to.

        Returns:
            List[AnyStr]: A list of lines from the response content.
        """
        return_list: List[AnyStr] = []
        with open(file_path, "wb") as f:
            dec = zlib.decompressobj(32 + zlib.MAX_WBITS)
            for chunk in response.raw.stream(1024, decode_content=False):
                if chunk:
                    rv = dec.decompress(chunk)
                    data = rv.decode("utf-8", errors="ignore")
                    for line in data.split("\n"):
                        return_list.append(line)
                        print(line)
        return return_list

    def _output_to_json_stream(self, response: Response, file_path: AnyStr) -> List[Dict[str, Any]]:
        """Writes the response content to stdout.

        Args:
            response (Response): The response object to write to stdout.
            file_path (AnyStr): The path to write the response content to.

        Returns:
            List[Dict[str, Any]]: A list of lines from the response content in dictionary format.
        """
        return_list: List[Dict[str, Any]] = []
        with open(file_path, "wb") as f:
            dec = zlib.decompressobj(32 + zlib.MAX_WBITS)
            for chunk in response.raw.stream(1024, decode_content=False):
                if chunk:
                    rv = dec.decompress(chunk)
                    data = rv.decode("utf-8", errors="ignore")
                    for line in data.split("\n"):
                        parsed_dict: Dict[str, Any] = self._parse_line(line=line)
                        return_list.append(parsed_dict)
                        print(parsed_dict)
        return return_list

    def _download_single_zone_file(self, zone_file_link: AnyStr) -> AnyStr:
        """Downloas the zone file from the provided URL.

        Args:
            zone_file_link (AnyStr): A CZDS Zone file to download from.

        Raises:
            UnsupportedTypeError: Raises when the output format is not supported.

        Returns:
            AnyStr: The path that the zone file was downloaded to.
        """
        response = self._get(zone_file_link)
        zone_name = zone_file_link.rsplit("/", 1)[-1].rsplit(".")[-2]

        # Try to get the filename from the header
        _, option = cgi.parse_header(response.headers["content-disposition"])
        filename = option["filename"]

        # If could get a filename from the header, then makeup one like [tld].txt.gz
        if not filename:
            filename = zone_name + ".txt"
        path = os.path.join(Base.SAVE_PATH, filename)
        if not Base.OUTPUT_FORMAT:
            self._output_to_disk(response=response, file_path=path)
        elif Base.OUTPUT_FORMAT == "text":
            self._output_to_text_stream(response=response, file_path=path)
        elif Base.OUTPUT_FORMAT == "json":
            self._output_to_json_stream(response=response, file_path=path)
        else:
            raise UnsupportedTypeError(
                f"Unsupported output format '{Base.OUTPUT_FORMAT}'. Supported formats are 'none', 'text', or 'json'."
            )
        return path

    def download(self, zone_file_list: AnyStr or List[AnyStr]) -> AnyStr:
        """Main method used to download zone files.

        Args:
            zone_file_list (AnyStr): One or more zone file(s) to download.

        Raises:
            UnsupportedTypeError: Raised when a unsupported type is provided.

        Returns:
            AnyStr: The path that the zone file was saved to.
        """
        if Base.SAVE_PATH:
            if not os.path.exists(Base.SAVE_PATH):
                os.makedirs(Base.SAVE_PATH)
        if isinstance(zone_file_list, list):
            return [self._download_single_zone_file(zone_file_link=link) for link in zone_file_list]
        elif isinstance(zone_file_list, str):
            return self._download_single_zone_file(zone_file_link=zone_file_list)
        else:
            self.__logger.critical(
                f"Unable to download. Unknown data structure provided to this method. {zone_file_list}"
            )
            raise UnsupportedTypeError("""Unknown data type. Should be 'list' or 'str'.""")
