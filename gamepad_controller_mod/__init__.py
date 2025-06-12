"""Package *gamepad_controller_mod*

Versión modular del script de control y grabación de demostraciones con un
mando de videojuegos para entornos Gymnasium.
"""

__all__ = ["wrappers", "input_handler", "dataset_utils", "controller"]

from .controller import run_cli as _run_cli  # noqa: F401 