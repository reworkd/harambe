import abc
from datetime import datetime
from time import perf_counter
from typing import Callable, TypedDict, NotRequired, Type, Any, Awaitable, Self

import wrapt


class FunctionCall(TypedDict):
    timestamp: float
    method: str
    args: list[str]
    kwargs: dict[str, str]
    execution_time: NotRequired[float]
    result: NotRequired[str]


Exporter = Callable[[FunctionCall], Awaitable[None]]


class InMemoryExporter:
    def __init__(self):
        self.events = []

    async def export(self, events: FunctionCall) -> None:
        self.events.append(events)


class HarambeInstrumentation(abc.ABC):
    __WRAPPED_FUNCTIONS = dict()

    PLAYWRIGHT_METHODS_TO_INSTRUMENT = [
        "click",
        "goto",
        "query_selector",
        "query_selector_all",
        "wait_for_selector",
        "wait_for_load_state",
        "wait_for_timeout",
        "screenshot",
        "evaluate",
    ]

    SOUP_METHODS_TO_INSTRUMENT = [
        "goto",
        "query_selector",
        "query_selector_all",
    ]

    SDK_METHODS_TO_INSTRUMENT = [
        "enqueue",
        "save_data",
        "save_cookies",
        "save_local_storage",
        "capture_pdf",
        "capture_url",
        "capture_html",
        "capture_download",
    ]

    def __init__(self):
        self._exporters = []

    def add_exporter(self, exporter: Exporter) -> Self:
        self._exporters.append(exporter)
        return self

    async def export(self, event: FunctionCall) -> None:
        for exporter in self._exporters:
            await exporter(event)

    def instrument(self) -> Self:
        from playwright.async_api import Page
        from harambe.contrib.soup.impl import SoupPage
        from harambe import SDK

        for method_name in self.PLAYWRIGHT_METHODS_TO_INSTRUMENT:
            self._wrap_function(Page, method_name)

        for method_name in self.SOUP_METHODS_TO_INSTRUMENT:
            self._wrap_function(SoupPage, method_name)

        for method_name in self.SDK_METHODS_TO_INSTRUMENT:
            self._wrap_function(SDK, method_name)

        return self

    @staticmethod
    def un_instrument() -> None:
        for (
            target,
            method_name,
        ), func in HarambeInstrumentation.__WRAPPED_FUNCTIONS.items():
            setattr(target, method_name, func)

        HarambeInstrumentation.__WRAPPED_FUNCTIONS = dict()

    def _wrap_function(self, target: Type[Any], method_name: str):
        target_name = target.__name__

        if HarambeInstrumentation.__WRAPPED_FUNCTIONS.get((target, method_name)):
            print("Already instrumented: ", target_name + "." + method_name)
            return

        HarambeInstrumentation.__WRAPPED_FUNCTIONS[(target, method_name)] = getattr(
            target, method_name
        )

        async def _wrapper(func, _instance, args, kwargs):
            event: FunctionCall = {
                "timestamp": datetime.now().timestamp(),
                "method": f"{target_name}.{method_name}",
                "args": [str(a) for a in args],
                "kwargs": {k: repr(v) for k, v in kwargs.items()},
            }

            exc, result = None, None
            start = perf_counter()

            try:
                result = await func(*args, **kwargs)
                event["result"] = repr(result)

            except Exception as e:
                event["result"] = repr(e)
                exc = e

            event["execution_time"] = perf_counter() - start
            await self.export(event)

            if exc:
                raise exc
            return result

        wrapt.wrap_function_wrapper(target, method_name, _wrapper)
