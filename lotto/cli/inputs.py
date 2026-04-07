from datetime import datetime

import typer

from ..settings import config


def is_date_str_valid(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, config.app.date_format)
        return True
    except ValueError:
        return False


def validate_date_options(date_from: str | None, date_to: str | None) -> None:
    if date_from and not is_date_str_valid(date_from):
        raise typer.BadParameter(f'Invalid date format for --date-from. Expected format: {config.app.date_format}')
    if date_to and not is_date_str_valid(date_to):
        raise typer.BadParameter(f'Invalid date format for --date-to. Expected format: {config.app.date_format}')


def parse_params(params: list[str] | None) -> dict[str, str]:
    if params is None:
        return {}

    parsed_params: dict[str, str] = {}

    for param_item in params:
        name, separator, value = param_item.partition('=')

        if separator != '=' or not name:
            raise typer.BadParameter('Parameters must use the format name=value.', param_hint='--param')

        if name in parsed_params:
            raise typer.BadParameter(f'Duplicate parameter: {name}', param_hint='--param')

        parsed_params[name] = value

    return parsed_params


def has_default_generate_inputs(
    params: list[str] | None,
    date_from: str | None,
    date_to: str | None,
    top: int,
) -> bool:
    return params is None and date_from is None and date_to is None and top == 100
