from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar('T', bound='DrawResultsDto')


@_attrs_define
class DrawResultsDto:
    """
    Attributes:
        draw_date (str | Unset):
        lotto_numbers (list[int] | Unset):
        plus_numbers (list[int] | Unset):
    """

    draw_date: str | Unset = UNSET
    lotto_numbers: list[int] | Unset = UNSET
    plus_numbers: list[int] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        draw_date = self.draw_date

        lotto_numbers: list[int] | Unset = UNSET
        if not isinstance(self.lotto_numbers, Unset):
            lotto_numbers = self.lotto_numbers

        plus_numbers: list[int] | Unset = UNSET
        if not isinstance(self.plus_numbers, Unset):
            plus_numbers = self.plus_numbers

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if draw_date is not UNSET:
            field_dict['drawDate'] = draw_date
        if lotto_numbers is not UNSET:
            field_dict['lottoNumbers'] = lotto_numbers
        if plus_numbers is not UNSET:
            field_dict['plusNumbers'] = plus_numbers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        draw_date = d.pop('drawDate', UNSET)

        lotto_numbers = cast('list[int]', d.pop('lottoNumbers', UNSET))

        plus_numbers = cast('list[int]', d.pop('plusNumbers', UNSET))

        draw_results_dto = cls(
            draw_date=draw_date,
            lotto_numbers=lotto_numbers,
            plus_numbers=plus_numbers,
        )

        draw_results_dto.additional_properties = d
        return draw_results_dto

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
