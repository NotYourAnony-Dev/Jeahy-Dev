# loader.py
import importlib
import os
from utils.logger import LOGGER

PLUGINS_DIR = os.path.join(os.path.dirname(__file__), "plugins")

def load_plugins(app):
    loaded = []
    failed = []
    for fname in sorted(os.listdir(PLUGINS_DIR)):
        if fname.endswith(".py") and not fname.startswith("_"):
            name = fname[:-3]
            try:
                module = importlib.import_module(f"plugins.{name}")
                if hasattr(module, "register"):
                    module.register(app)
                    loaded.append(name)
                else:
                    LOGGER.warning(f"Plugin '{name}' has no register() — skipped.")
            except Exception as e:
                LOGGER.error(f"Failed to load plugin '{name}': {e}")
                failed.append(name)

    LOGGER.info(f"Loaded plugins: {', '.join(loaded)}")
    if failed:
        LOGGER.warning(f"Failed plugins: {', '.join(failed)}")
