import importlib
import pkgutil

from lotto.cli import run_typer_app


def run_modules_discovery(package: str) -> None:
    package = importlib.import_module(package)

    for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        importlib.import_module(module_name)


if __name__ == '__main__':
    run_modules_discovery('lotto.strategies')
    run_typer_app()
