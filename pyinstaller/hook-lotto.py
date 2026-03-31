from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['lotto.strategies', *collect_submodules('lotto.strategies')]
module_collection_mode = {'lotto.strategies': 'pyz+py'}
