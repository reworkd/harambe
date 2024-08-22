import hashlib
import json
from typing import Any, Optional, Iterable

from harambe.types import URL, Context, Options


class DuplicateHandler:
    def __init__(self) -> None:
        self._saved_data: set[bytes] = set()
        self.rows_on_page = 0
        self.previously_saved_rows_on_page = 0

    def on_save_data(self, data: dict[str, Any]) -> bool:
        """
        Save data and check if it is duplicated
        :param data: data to be saved
        :return: bool indicating if the data is duplicated, true if it is duplicated
        """

        return self._add_data(data)

    def on_queue_url(
        self, url: URL, _: Optional[Context], __: Optional[Options]
    ) -> bool:
        return self._add_data(url)

    # noinspection PyTypeChecker
    def on_download(self, download_url: str, filename: str, content: bytes) -> bool:
        return self._add_data((download_url, filename))

    def should_continue(self, strict: bool = False) -> bool:
        """
        Check if the current page should be continued to be processed
        :param strict: if strict is True, it will only return True if all rows on the page are duplicated,
        otherwise it will return True if there are any duplicated rows
        :return: bool indicating if the page should be continued
        """

        if strict:
            return self.previously_saved_rows_on_page == 0

        return self.rows_on_page == self.previously_saved_rows_on_page

    def on_paginate(self, next_url: str) -> bool:
        if self.should_continue():
            raise StopAsyncIteration()

        self.rows_on_page = 0
        self.previously_saved_rows_on_page = 0
        return False

    def _add_data(self, data: Any) -> bool:
        self.rows_on_page += 1

        hash_value = self.compute_hash(data)
        if hash_value in self._saved_data:
            self.previously_saved_rows_on_page += 1
            return True  # return True if data is duplicated
        else:
            self._saved_data.add(hash_value)
            return False

    @staticmethod
    def compute_hash(data: Any) -> bytes:
        if isinstance(data, dict):
            data = {k: v for k, v in data.items() if not k.startswith("__")}

        data_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return hashlib.md5(data_str.encode()).digest()


class PaginatedList(list[Any]):
    def __init__(self) -> None:
        super().__init__()
        self._handler = DuplicateHandler()

    def append(self, item: Any) -> None:
        if not self._handler.on_save_data(item):
            super().append(item)

    def extend(self, items: Iterable[Any]) -> None:
        for item in items:
            self.append(item)

    def should_continue(self) -> bool:
        return self._handler.should_continue(strict=True)
