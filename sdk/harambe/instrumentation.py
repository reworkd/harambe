import abc

from datetime import datetime
from time import perf_counter

import functools

import types
from typing import Callable, Coroutine, Any, TypedDict, NotRequired, TYPE_CHECKING

if TYPE_CHECKING:
    from harambe import SDK


class SdkCall(TypedDict):
    timestamp: float
    method: str
    args: list[str]
    kwargs: dict[str, str]
    execution_time: NotRequired[float]
    result: NotRequired[str]


class HarambeInstrumentation(abc.ABC):

    def instrument(self, sdk: "SDK") -> None:
        self._instrument_function(sdk.enqueue)
        self._instrument_function(sdk.save_data)
        self._instrument_function(sdk.save_cookies)
        self._instrument_function(sdk.save_local_storage)
        self._instrument_function(sdk.capture_pdf)
        self._instrument_function(sdk.capture_url)
        self._instrument_function(sdk.capture_html)
        self._instrument_function(sdk.capture_download)

    @abc.abstractmethod
    def sink(self, event: SdkCall) -> None:
        raise NotImplementedError()

    def _instrument_function(self, func: Callable[..., Coroutine[Any, Any, Any]]):
        sdk = func.__self__
        method_name = func.__name__

        @functools.wraps(func)
        async def wrapped(_func_self: "SDK", *args, **kwargs):
            event: SdkCall = {
                "timestamp": datetime.now().timestamp(),
                "method": method_name,
                "args": [repr(a) for a in args],
                "kwargs": {k: repr(v) for k, v in kwargs.items()},
            }

            exc, result = None, None
            start = perf_counter()
            try:
                result = await func(*args, **kwargs)  # Don't pass self as it's already bound
                event["result"] = repr(result)
            except Exception as e:
                event["result"], exc = repr(e), e

            event["execution_time"] = perf_counter() - start
            self.sink(event)

            if exc:
                raise exc
            return result

        # bind the wrapper back onto the *instance* so it gets self properly
        setattr(sdk, method_name, types.MethodType(wrapped, sdk))
