"""czds.base.

This Base class inherits from our LoggingBase metaclass and gives us
shared logging across any class inheriting from Base.
"""

import inspect
import os
from typing import Any
from typing import AnyStr
from typing import List

from .logger import LoggingBase


class Base(metaclass=LoggingBase):
    """Base class to all other classes within this project."""

    BASE_URL: AnyStr = "https://czds-api.icann.org"
    AUTH_URL: AnyStr = "https://account-api.icann.org/api/authenticate"
    BASE_HEADERS: dict = {"Content-Type": "application/json", "Accept": "application/json"}
    THREAD_COUNT: int = os.cpu_count() * 5
    USERNAME: AnyStr = None
    PASSWORD: AnyStr = None
    SAVE_PATH: AnyStr = None
    OUTPUT_FORMAT: AnyStr = None

    # We create a Connector object and set it to this class property in czds.py
    connection = None

    def _chunk(self, items: List[AnyStr], chunk_size: int) -> List[List[AnyStr]]:
        chunk_size = max(1, chunk_size)
        return (items[i : i + chunk_size] for i in range(0, len(items), chunk_size))

    def run_threaded(self, method: Any, list_data: List) -> List[str]:
        """This method accepts a method and a list of data to run multi-threaded.

        The provided list_data will be chunked into equal part lists per thread.

        TODO: Add ability to configure number of threads by environmental variable and
              via input paramater.

        The current configuration for how many threads are used is based on the following
            `os.cpu_count() * 5`

        We use the value from the above multiplication by calculating the value to chunk
        the list data by.

        This means, that we take the total count of items in the provided list and divide
        it by the value from `os.cpu_count() * 5` which equates to 60 on my system.

        For example, using a MacBook Pro 2018 15-inch with 2.6 GHz 6-Core Intel Core i7 and
        16 GB 2400 MHz DDR4 results in 60 threads being created.

        Args:
            method (Any): The method to pass each chunk. This method should accept a List (but a smaller list).
            list_data (List): The list data to chunk. Each chunk is passed to the provided method in it's own thread.

        Returns:
            List[str]: A list of results.
        """
        from concurrent.futures import ThreadPoolExecutor
        from concurrent.futures import as_completed

        threads = []
        return_list = []
        self.__logger.info(f"Chunking data and running {self.THREAD_COUNT} threads.")
        zone_chunks = self._chunk(list_data, int(len(list_data) / self.THREAD_COUNT))
        with ThreadPoolExecutor(max_workers=self.THREAD_COUNT) as executor:
            for chunk in zone_chunks:
                threads.append(executor.submit(method, chunk))
            count = 0
            for task in as_completed(threads):
                return_list.append(task.result())
                count += 1
                self.__logger.info(f"Retrieved results from {count} threads.")
        return return_list

    def log(self, message: AnyStr, level: AnyStr = "info") -> None:
        """Used to centralize logging across components.

        We identify the source of the logging class by inspecting the calling stack.

        Args:
            message (AnyStr): The log value string to output.
            level (AnyStr): The log level. Defaults to "info".
        """
        component = None
        parent = inspect.stack()[1][0].f_locals.get("self", None)
        component = parent.__class__.__name__
        try:
            getattr(getattr(parent, f"_{component}__logger"), level)(message)
        except AttributeError as ae:
            getattr(self.__logger, level)(message + ae)
