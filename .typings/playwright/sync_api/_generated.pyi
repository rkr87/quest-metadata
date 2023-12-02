import pathlib
from typing import Literal, Optional, Pattern, Union

from playwright._impl._api_structures import (Cookie, Geolocation,
                                              HttpCredentials, Position,
                                              ProxySettings, StorageState,
                                              ViewportSize)
from playwright._impl._sync_base import SyncBase, SyncContextManager

class JSHandle(SyncBase):
    ...

class Response(SyncBase):
    ...

class ElementHandle(JSHandle):
    def click(
        self,
        *,
        modifiers: Optional[list[Literal['Alt', 'Control', 'Meta', 'Shift']]] = ...,
        position: Optional[Position] = ...,
        delay: Optional[float] = ...,
        button: Optional[Literal['left', 'middle', 'right']] = ...,
        click_count: Optional[int] = ...,
        timeout: Optional[float] = ...,
        force: Optional[bool] = ...,
        no_wait_after: Optional[bool] = ...,
        trial: Optional[bool] = ...
    ) -> None:
        ...

class Page(SyncContextManager):
    def wait_for_selector(
        self,
        selector: str,
        *,
        timeout: Optional[float] = ...,
        state: Optional[Literal['attached', 'detached', 'hidden', 'visible']] = ...,
        strict: Optional[bool] = ...
    ) -> Optional['ElementHandle']:
        ...
    def goto(
        self,
        url: str,
        *,
        timeout: Optional[float] = ...,
        wait_until: Optional[Literal['commit', 'domcontentloaded', 'load', 'networkidle']] = ...,
        referer: Optional[str] = ...
    ) -> Optional['Response']:
        ...

class BrowserContext(SyncContextManager):
    def new_page(self) -> Page: 
        ...
    def cookies(self,
        urls: Optional[Union[str, list[str]]] = ...
    ) -> list[Cookie]:
        ...

class Browser(SyncContextManager):
    def new_context(
        self,
        *,viewport: Optional[ViewportSize] = ...,
        screen: Optional[ViewportSize] = ...,
        no_viewport: Optional[bool] = ...,
        ignore_https_errors: Optional[bool] = ...,
        java_script_enabled: Optional[bool] = ...,
        bypass_csp: Optional[bool] = ...,
        user_agent: Optional[str] = ...,
        locale: Optional[str] = ...,
        timezone_id: Optional[str] = ...,
        geolocation: Optional[Geolocation] = ...,
        permissions: Optional[list[str]] = ...,
        extra_http_headers: Optional[dict[str, str]] = ...,
        offline: Optional[bool] = ...,
        http_credentials: Optional[HttpCredentials] = ...,
        device_scale_factor: Optional[float] = ...,
        is_mobile: Optional[bool] = ...,
        has_touch: Optional[bool] = ...,
        color_scheme: Optional[Literal['dark', 'light', 'no-preference', 'null']] = ...,
        reduced_motion: Optional[Literal['no-preference', 'null', 'reduce']] = ...,
        forced_colors: Optional[Literal['active', 'none', 'null']] = ...,
        accept_downloads: Optional[bool] = ...,
        default_browser_type: Optional[str] = ...,
        proxy: Optional[ProxySettings] = ...,
        record_har_path: Optional[Union[str, pathlib.Path]] = ...,
        record_har_omit_content: Optional[bool] = ...,
        record_video_dir: Optional[Union[str, pathlib.Path]] = ...,
        record_video_size: Optional[ViewportSize] = ...,
        storage_state: Optional[Union[StorageState, str, pathlib.Path]] = ...,
        base_url: Optional[str] = ...,
        strict_selectors: Optional[bool] = ...,
        service_workers: Optional[Literal['allow', 'block']] = ...,
        record_har_url_filter: Optional[Union[str, Pattern[str]]] = ...,
        record_har_mode: Optional[Literal['full', 'minimal']] = ...,
        record_har_content: Optional[Literal['attach', 'embed', 'omit']] = ...
    ) -> BrowserContext:
        ...

class BrowserType(SyncBase):
    def launch(
        self,
        *,
        executable_path: Optional[Union[str, pathlib.Path]] = ...,
        channel: Optional[str] = ...,
        args: Optional[list[str]] = ...,
        ignore_default_args: Optional[Union[bool, list[str]]] = ...,
        handle_sigint: Optional[bool] = ...,
        handle_sigterm: Optional[bool] = ...,
        handle_sighup: Optional[bool] = ...,
        timeout: Optional[float] = ...,
        env: Optional[dict[str, Union[str, float, bool]]] = ...,
        headless: Optional[bool] = ...,
        devtools: Optional[bool] = ...,
        proxy: Optional[ProxySettings] = ...,
        downloads_path: Optional[Union[str, pathlib.Path]] = ...,
        slow_mo: Optional[float] = ...,
        traces_dir: Optional[Union[str, pathlib.Path]] = ...,
        chromium_sandbox: Optional[bool] = ...,
        firefox_user_prefs: Optional[dict[str, Union[str, float, bool]]] = ...
    ) -> Browser:
        ...

class Playwright(SyncBase):
    @property
    def chromium(self) -> BrowserType: 
        ...
    def __getitem__(self, value: str) -> BrowserType: 
        ...
