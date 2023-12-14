import pathlib
import typing
from typing import Literal

from playwright._impl._api_structures import (Cookie, Geolocation,
                                              HttpCredentials, Position,
                                              ProxySettings, SetCookieParam,
                                              StorageState, ViewportSize)
from playwright._impl._async_base import AsyncBase, AsyncContextManager

class JSHandle(AsyncBase):
    ...

class Response(AsyncBase):
    ...

class ElementHandle(JSHandle):
    async def click(
            self,
            *,
            modifiers: typing.Optional[typing.List[Literal['Alt', 'Control', 'Meta', 'Shift']]] = ...,
            position: typing.Optional[Position] = ...,
            delay: typing.Optional[float] = ...,
            button: typing.Optional[Literal['left', 'middle', 'right']] = ...,
            click_count: typing.Optional[int] = ...,
            timeout: typing.Optional[float] = ...,
            force: typing.Optional[bool] = ...,
            no_wait_after: typing.Optional[bool] = ...,
            trial: typing.Optional[bool] = ...
        ) -> None: ...

class Page(AsyncContextManager):
    async def wait_for_selector(
        self,
        selector: str,
        *,
        timeout: typing.Optional[float] = ...,
        state: typing.Optional[Literal['attached', 'detached', 'hidden', 'visible']] = ...,
        strict: typing.Optional[bool] = ...
    ) -> typing.Optional['ElementHandle']: ...
    async def goto(
        self,
        url: str,
        *,
        timeout: typing.Optional[float] = ...,
        wait_until: typing.Optional[Literal['commit', 'domcontentloaded', 'load', 'networkidle']] = ...,
        referer: typing.Optional[str] = ...
    ) -> typing.Optional['Response']: ...
    def on(
        self,
        event: Literal['response'],
        f: typing.Callable[[Response], 'typing.Union[typing.Awaitable[None], None]']
    ) -> None: ...
    async def content(self) -> str: ...



class BrowserContext(AsyncContextManager):
    async def new_page(self) -> Page: ...
    async def cookies(
        self,
        urls: typing.Optional[typing.Union[str, typing.List[str]]] = ...
    ) -> typing.List[Cookie]: ...
    async def add_cookies(self, cookies: typing.List[SetCookieParam]) -> None: ...


class Browser(AsyncContextManager):
    async def new_context(
        self,
        *,
        viewport: typing.Optional[ViewportSize] = ...,
        screen: typing.Optional[ViewportSize] = ...,
        no_viewport: typing.Optional[bool] = ...,
        ignore_https_errors: typing.Optional[bool] = ...,
        java_script_enabled: typing.Optional[bool] = ...,
        bypass_csp: typing.Optional[bool] = ...,
        user_agent: typing.Optional[str] = ...,
        locale: typing.Optional[str] = ...,
        timezone_id: typing.Optional[str] = ...,
        geolocation: typing.Optional[Geolocation] = ...,
        permissions: typing.Optional[typing.List[str]] = ...,
        extra_http_headers: typing.Optional[typing.Dict[str, str]] = ...,
        offline: typing.Optional[bool] = ...,
        http_credentials: typing.Optional[HttpCredentials] = ...,
        device_scale_factor: typing.Optional[float] = ...,
        is_mobile: typing.Optional[bool] = ...,
        has_touch: typing.Optional[bool] = ...,
        color_scheme: typing.Optional[Literal['dark', 'light', 'no-preference', 'null']] = ...,
        reduced_motion: typing.Optional[Literal['no-preference', 'null', 'reduce']] = ...,
        forced_colors: typing.Optional[Literal['active', 'none', 'null']] = ...,
        accept_downloads: typing.Optional[bool] = ...,
        default_browser_type: typing.Optional[str] = ...,
        proxy: typing.Optional[ProxySettings] = ...,
        record_har_path: typing.Optional[typing.Union[str, pathlib.Path]] = ...,
        record_har_omit_content: typing.Optional[bool] = ...,
        record_video_dir: typing.Optional[typing.Union[str, pathlib.Path]] = ...,
        record_video_size: typing.Optional[ViewportSize] = ...,
        storage_state: typing.Optional[typing.Union[StorageState, str, pathlib.Path]] = ...,
        base_url: typing.Optional[str] = ...,
        strict_selectors: typing.Optional[bool] = ...,
        service_workers: typing.Optional[Literal['allow', 'block']] = ...,
        record_har_url_filter: typing.Optional[typing.Union[str, typing.Pattern[str]]] = ...,
        record_har_mode: typing.Optional[Literal['full', 'minimal']] = ...,
        record_har_content: typing.Optional[Literal['attach', 'embed', 'omit']] = ...
    ) -> BrowserContext: ...

class BrowserType(AsyncBase):
    async def launch(
        self,
        *,
        executable_path: typing.Optional[typing.Union[str, pathlib.Path]] = ...,
        channel: typing.Optional[str] = ...,
        args: typing.Optional[typing.List[str]] = ...,
        ignore_default_args: typing.Optional[typing.Union[bool, typing.List[str]]] = ...,
        handle_sigint: typing.Optional[bool] = ...,
        handle_sigterm: typing.Optional[bool] = ...,
        handle_sighup: typing.Optional[bool] = ...,
        timeout: typing.Optional[float] = ...,
        env: typing.Optional[typing.Dict[str, typing.Union[str, float, bool]]] = ...,
        headless: typing.Optional[bool] = ...,
        devtools: typing.Optional[bool] = ...,
        proxy: typing.Optional[ProxySettings] = ...,
        downloads_path: typing.Optional[typing.Union[str, pathlib.Path]] = ...,
        slow_mo: typing.Optional[float] = ...,
        traces_dir: typing.Optional[typing.Union[str, pathlib.Path]] = ...,
        chromium_sandbox: typing.Optional[bool] = ...,
        firefox_user_prefs: typing.Optional[typing.Dict[str, typing.Union[str, float, bool]]] = ...
    ) -> Browser: ...

class Playwright(AsyncBase):
    @property
    def chromium(self) -> BrowserType: ...
    def __getitem__(self, value: str) -> BrowserType: ...