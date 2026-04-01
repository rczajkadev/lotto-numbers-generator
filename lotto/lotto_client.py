from datetime import datetime
from json import JSONDecodeError

import httpx

from .api_client.api.draw_results import get_draw_results as get_draw_results_operation
from .api_client.client import AuthenticatedClient
from .api_client.models.draw_results_dto import DrawResultsDto
from .api_client.models.error_response import ErrorResponse
from .api_client.types import UNSET
from .core import LottoDrawRecord
from .settings import config


def get_draw_results(date_from: str | None, date_to: str | None, top: int | None) -> list[LottoDrawRecord]:
    client = _create_authenticated_client()

    try:
        response = get_draw_results_operation.sync(
            client=client,
            date_from=date_from if date_from is not None else UNSET,
            date_to=date_to if date_to is not None else UNSET,
            top=top if top is not None else UNSET,
        )
    except JSONDecodeError:
        raw_response = _get_raw_draw_results_response(client, date_from, date_to, top)

        if raw_response.status_code == 404:
            return []

        raw_response.raise_for_status()
        raise RuntimeError(raw_response.text) from None

    if response is None:
        raise RuntimeError('The API returned an undocumented response.')

    if isinstance(response, ErrorResponse):
        raise RuntimeError(response.error if isinstance(response.error, str) else 'The API returned an error response.')

    if isinstance(response, str):
        raise RuntimeError(response)

    records = [_map_record(record) for record in response]
    return sorted(records, key=lambda record: record.draw_date)


def _map_record(record: DrawResultsDto) -> LottoDrawRecord:
    if not isinstance(record.draw_date, str):
        raise ValueError('Missing draw date in API response.')

    if not isinstance(record.lotto_numbers, list):
        raise ValueError('Missing lotto numbers in API response.')

    if not isinstance(record.plus_numbers, list):
        raise ValueError('Missing plus numbers in API response.')

    return LottoDrawRecord(
        draw_date=datetime.strptime(record.draw_date, config.app.date_format).date(),
        lotto_numbers=record.lotto_numbers,
        plus_numbers=record.plus_numbers,
    )


def _get_raw_draw_results_response(
    client: AuthenticatedClient,
    date_from: str | None,
    date_to: str | None,
    top: int | None,
) -> httpx.Response:
    params = {'dateFrom': date_from, 'dateTo': date_to, 'top': top}
    params = {key: value for key, value in params.items() if value is not None}

    return client.get_httpx_client().request('get', '/draw-results', params=params)


def _create_authenticated_client() -> AuthenticatedClient:
    return AuthenticatedClient(
        base_url=_build_api_base_url(),
        token=config.api.api_key,
        prefix='',
        auth_header_name='x-functions-key',
        timeout=config.api.timeout,
        raise_on_unexpected_status=True,
    )


def _build_api_base_url() -> str:
    url = config.api.base_url
    url = url[:-1] if url.endswith('/') else url
    return url if url.endswith('/api') else f'{url}/api'
