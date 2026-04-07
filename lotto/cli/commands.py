from typing import Annotated

import typer

from .. import services
from ..visualisation import visualise_results
from . import inputs, rendering, service_calls


def register_commands(app: typer.Typer) -> None:
    app.callback()(_run_default_command)
    app.command(name='simulate')(_run_simulation)
    app.command(name='strategies')(_list_strategies)


def _run_default_command(
    ctx: typer.Context,
    strategy_name: Annotated[str | None, typer.Option('--strategy', '-s')] = None,
    params: Annotated[list[str] | None, typer.Option('--param', '-p')] = None,
    date_from: Annotated[str | None, typer.Option('--date-from')] = None,
    date_to: Annotated[str | None, typer.Option('--date-to')] = None,
    top: Annotated[int, typer.Option('--top', min=1)] = 100,
) -> None:
    if ctx.invoked_subcommand is not None:
        return

    if strategy_name is None:
        if inputs.has_default_generate_inputs(params, date_from, date_to, top):
            rendering.show_root_help_and_exit(ctx)

        raise typer.BadParameter('Option --strategy is required in default generate mode.', param_hint='--strategy')

    inputs.validate_date_options(date_from, date_to)
    params_dict = inputs.parse_params(params)
    generation = _prepare_generation(strategy_name, params_dict, date_from, date_to, top)

    if generation.numbers is None:
        rendering.show_no_draw_results()
        return

    rendering.render_generated_numbers(strategy_name, generation.numbers)


def _run_simulation(
    strategy_name: Annotated[str, typer.Option('--strategy', '-s')],
    params: Annotated[list[str] | None, typer.Option('--param', '-p')] = None,
    date_from: Annotated[str | None, typer.Option('--date-from')] = None,
    date_to: Annotated[str | None, typer.Option('--date-to')] = None,
    top: Annotated[int | None, typer.Option('--top', min=1)] = None,
) -> None:
    inputs.validate_date_options(date_from, date_to)
    params_dict = inputs.parse_params(params)

    with rendering.fetching_status():
        prepared_simulation = service_calls.prepare_simulation(strategy_name, params_dict, date_from, date_to, top)

    if not prepared_simulation.data:
        rendering.show_no_draw_results()
        return

    with rendering.backtest_progress(prepared_simulation.total_games) as advance:
        results, summary = service_calls.run_backtest(prepared_simulation, on_result=advance)

    rendering.render_simulation_summary(summary)
    visualise_results(results, prepared_simulation.strategy_name)


def _list_strategies() -> None:
    rendering.render_strategy_list(service_calls.list_strategies())


### helpers ###


def _prepare_generation(
    strategy_name: str,
    params: dict[str, str],
    date_from: str | None,
    date_to: str | None,
    top: int,
) -> services.PreparedGeneration:
    requires_data = service_calls.get_strategy_requires_data(strategy_name)

    if requires_data:
        with rendering.fetching_status():
            return service_calls.generate_numbers(strategy_name, params, date_from, date_to, top)

    return service_calls.generate_numbers(strategy_name, params, date_from, date_to, top)
