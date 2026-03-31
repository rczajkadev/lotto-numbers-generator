from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="SyncDto")



@_attrs_define
class SyncDto:
    """ 
        Attributes:
            latest_sync_date (str | Unset):
            latest_draw_date (str | Unset):
            is_up_to_date (bool | Unset):
     """

    latest_sync_date: str | Unset = UNSET
    latest_draw_date: str | Unset = UNSET
    is_up_to_date: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        latest_sync_date = self.latest_sync_date

        latest_draw_date = self.latest_draw_date

        is_up_to_date = self.is_up_to_date


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if latest_sync_date is not UNSET:
            field_dict["latestSyncDate"] = latest_sync_date
        if latest_draw_date is not UNSET:
            field_dict["latestDrawDate"] = latest_draw_date
        if is_up_to_date is not UNSET:
            field_dict["isUpToDate"] = is_up_to_date

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        latest_sync_date = d.pop("latestSyncDate", UNSET)

        latest_draw_date = d.pop("latestDrawDate", UNSET)

        is_up_to_date = d.pop("isUpToDate", UNSET)

        sync_dto = cls(
            latest_sync_date=latest_sync_date,
            latest_draw_date=latest_draw_date,
            is_up_to_date=is_up_to_date,
        )


        sync_dto.additional_properties = d
        return sync_dto

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
