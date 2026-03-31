import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .core import GameRecord, GameType

BACKGROUND_COLOR = '#111111'
DEFAULT_CONFIG = {'displaylogo': False}
JAVASCRIPT = f'''document.body.style.backgroundColor = "{BACKGROUND_COLOR}"; document.title = "Lotto Results";'''
TEMPLATE = 'plotly_dark'


def visualise_results(history: list[GameRecord], strategy_name: str) -> None:
    if not history:
        return

    fig = make_subplots(rows=2, shared_xaxes=True)

    fig.update_layout(
        hovermode='x unified',
        title=f'<b>Lotto & Lotto Plus draw results - {strategy_name}</b>',
        legend={'groupclick': 'toggleitem'},
        xaxis2_title='draw date',
        yaxis1_title='lotto matches',
        yaxis2_title='lotto plus matches',
        yaxis1_range=[0, 6],
        yaxis2_range=[0, 6],
        template=TEMPLATE,
        paper_bgcolor=BACKGROUND_COLOR,
        showlegend=False,
    )

    lotto_history = [record for record in history if record.game_type == GameType.LOTTO]
    plus_history = [record for record in history if record.game_type == GameType.LOTTO_PLUS]

    fig.add_trace(
        go.Bar(
            x=[record.draw_date for record in lotto_history],
            y=[record.matches for record in lotto_history],
            name='lotto matches',
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=[record.draw_date for record in plus_history],
            y=[record.matches for record in plus_history],
            name='plus matches',
        ),
        row=2,
        col=1,
    )

    day_as_ms = 86400000
    min_date = min([record.draw_date for record in history])
    max_date = max([record.draw_date for record in history])
    years_range = max_date.year - min_date.year

    if years_range > 2:
        fig.update_traces(width=day_as_ms * years_range / 2)

    fig.show(config=DEFAULT_CONFIG, post_script=[JAVASCRIPT])
