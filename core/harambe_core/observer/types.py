from typing import Literal, TypedDict

ObservationTrigger = Literal[
    "on_save_data",
    "on_queue_url",
    "on_download",
    "on_paginate",
    "on_save_cookies",
    "on_save_local_storage",
    "on_check_and_solve_captchas",
]


class DownloadMeta(TypedDict):
    url: str
    filename: str


class HTMLMetadata(DownloadMeta):
    html: str
    text: str
