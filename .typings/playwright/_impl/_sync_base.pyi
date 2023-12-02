from typing import Generic, TypeVar

from playwright._impl._impl_to_api_mapping import ImplToApiMapping, ImplWrapper

mapping: ImplToApiMapping
T = TypeVar('T')

class EventContextManager(Generic[T]):
    ...

class SyncBase(ImplWrapper):
    ...

class SyncContextManager(SyncBase):
    ...
