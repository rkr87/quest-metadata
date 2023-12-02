from typing import List, Literal, Optional, TypedDict

class Cookie(TypedDict, total=False):
    name: str
    value: str
    domain: str
    path: str
    expires: float
    httpOnly: bool
    secure: bool
    sameSite: Literal['Lax', 'None', 'Strict']

class Geolocation(TypedDict, total=False):
    latitude: float
    longitude: float
    accuracy: Optional[float]

class HttpCredentials(TypedDict, total=False):
    username: str
    password: str
    origin: Optional[str]

class LocalStorageEntry(TypedDict):
    name: str
    value: str

class OriginState(TypedDict):
    origin: str
    localStorage: List[LocalStorageEntry]

class Position(TypedDict):
    x: float
    y: float

class ProxySettings(TypedDict, total=False):
    server: str
    bypass: Optional[str]
    username: Optional[str]
    password: Optional[str]

class StorageState(TypedDict, total=False):
    cookies: list[Cookie]
    origins: list[OriginState]

class ViewportSize(TypedDict):
    width: int
    height: int
