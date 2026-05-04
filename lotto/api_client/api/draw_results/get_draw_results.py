from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.draw_results_dto import DrawResultsDto
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    date_from: str | Unset = UNSET,
    date_to: str | Unset = UNSET,
    top: int | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params['dateFrom'] = date_from

    params['dateTo'] = date_to

    params['top'] = top

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        'method': 'get',
        'url': '/draw-results',
        'params': params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[DrawResultsDto] | str | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = DrawResultsDto.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 404:
        response_404 = cast('str', response.json())
        return response_404

    if response.status_code == 406:
        response_406 = ErrorResponse.from_dict(response.json())

        return response_406

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | list[DrawResultsDto] | str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    date_from: str | Unset = UNSET,
    date_to: str | Unset = UNSET,
    top: int | Unset = UNSET,
) -> Response[ErrorResponse | list[DrawResultsDto] | str]:
    """
    Args:
        date_from (str | Unset):
        date_to (str | Unset):
        top (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[DrawResultsDto] | str]
    """

    kwargs = _get_kwargs(
        date_from=date_from,
        date_to=date_to,
        top=top,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    date_from: str | Unset = UNSET,
    date_to: str | Unset = UNSET,
    top: int | Unset = UNSET,
) -> ErrorResponse | list[DrawResultsDto] | str | None:
    """
    Args:
        date_from (str | Unset):
        date_to (str | Unset):
        top (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[DrawResultsDto] | str
    """

    return sync_detailed(
        client=client,
        date_from=date_from,
        date_to=date_to,
        top=top,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    date_from: str | Unset = UNSET,
    date_to: str | Unset = UNSET,
    top: int | Unset = UNSET,
) -> Response[ErrorResponse | list[DrawResultsDto] | str]:
    """
    Args:
        date_from (str | Unset):
        date_to (str | Unset):
        top (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[DrawResultsDto] | str]
    """

    kwargs = _get_kwargs(
        date_from=date_from,
        date_to=date_to,
        top=top,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    date_from: str | Unset = UNSET,
    date_to: str | Unset = UNSET,
    top: int | Unset = UNSET,
) -> ErrorResponse | list[DrawResultsDto] | str | None:
    """
    Args:
        date_from (str | Unset):
        date_to (str | Unset):
        top (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[DrawResultsDto] | str
    """

    return (
        await asyncio_detailed(
            client=client,
            date_from=date_from,
            date_to=date_to,
            top=top,
        )
    ).parsed
