import hashlib
import json
from typing import Any, Optional, Iterable, List

from pydantic import BaseModel

from harambe.types import URL, Context, Options, Cookie, LocalStorage


class PageInfo(BaseModel):
    page: int
    total_rows: int
    duplicated_rows: int


class DuplicateHandler:
    def __init__(self) -> None:
        self._saved_data: set[bytes] = set()
        self.current_page: int = 1
        self.page_info_map: dict[int, PageInfo] = {}

    def on_save_data(self, data: dict[str, Any]) -> bool:
        """
        Save data and check if it is duplicated
        :param data: data to be saved
        :return: bool indicating if the data is duplicated, true if it is duplicated
        """

        return self._add_data(data)

    def on_save_cookies(self, cookies: List[Cookie]) -> bool:
        """
        Save cookies and check if they are duplicated
        :param cookies: cookies to be saved
        :return: bool indicating if the cookies are duplicated, true if it is duplicated
        """
        return self._add_data(cookies)

    def on_save_local_storage(self, local_storage: List[LocalStorage]) -> bool:
        """
        Save local storage and check if they are duplicated
        :param local_storage: local storage to be saved
        :return: bool indicating if the local storage is duplicated, true if it is duplicated
        """
        return self._add_data(local_storage)

    def on_queue_url(
        self, url: URL, _: Optional[Context], __: Optional[Options]
    ) -> bool:
        """
        Save url and check if it is duplicated
        :param url: url to be saved
        :param _: context unused
        :param __: options unused
        :return: bool indicating if the url is duplicated, true if it is duplicated
        """
        return self._add_data(url)

    # noinspection PyTypeChecker
    def on_download(self, download_url: str, filename: str, content: bytes) -> bool:
        return self._add_data((download_url, filename))

    def should_continue(self, strict: bool = False) -> bool:
        """
        Check if the current page should be continued to be processed
        :param strict: if strict is True, it will only return True if any rows on the page are duplicated,
        otherwise it will return True if and only iff all rows are duplicated
        :return: bool indicating if pagination should continued
        """

        if strict:
            return self.get_current_page_info().duplicated_rows == 0

        return (
            self.get_current_page_info().total_rows > 0
            and self.get_current_page_info().total_rows
            == self.get_current_page_info().duplicated_rows
        )

    def on_paginate(self, next_url: str) -> bool:
        if self.should_continue():
            raise StopAsyncIteration()

        self.current_page += 1
        return False

    def _add_data(self, data: Any) -> bool:
        """
        :return: bool indicating whether the data is duplicated or not
        """
        self.get_current_page_info().total_rows += 1

        hash_value = self.compute_hash(data)
        if hash_value in self._saved_data:
            self.get_current_page_info().duplicated_rows += 1
            return True
        else:
            self._saved_data.add(hash_value)
            return False

    def get_number_of_pages(self) -> int:
        return self.current_page

    def get_current_page_info(self) -> PageInfo:
        if self.current_page not in self.page_info_map:
            self.page_info_map[self.current_page] = PageInfo(
                page=self.current_page, total_rows=0, duplicated_rows=0
            )

        return self.page_info_map[self.current_page]

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
