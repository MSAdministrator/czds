"""Contains data models around CZDS."""
from typing import AnyStr

from attrs import define


@define
class ZoneData:
    """Data model for each zone data element."""

    zone_name: AnyStr
    dns_record: AnyStr
    ttl: AnyStr
    record_class: AnyStr
    record_type: AnyStr
    record_data: AnyStr
