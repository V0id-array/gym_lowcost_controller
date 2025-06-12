"""input_handler.py

Encapsula la interacción con un game-pad usando *pygame* y expone métodos
alto nivel para:

1. Obtener el vector de acción continua normalizado para el robot.
2. Detectar eventos *edge-triggered* de botones (presión única).
3. Gestionar modos de precisión y multiplicadores de velocidad.

De esta forma se desacopla la lectura de hardware de la lógica de grabación.
"""

from __future__ import annotations

import pygame
import numpy as np
from typing import Dict, Optional


class GamepadInputHandler:
    """Gestiona un mando de videojuegos y traduce sus entradas a acciones."""

    # Mapeo de botones por nombre para evitar números mágicos.
    DEFAULT_BUTTON_MAPPING = {
        "record_toggle": 9,   # START/OPTIONS
        "reset": 1,          # Círculo/B
        "precision": 2,      # Cuadrado/X
        "quit": 3,           # Triángulo/Y
        "speed_up": 4,       # L1
        "speed_down": 5,     # R1
        "pause": 8,          # SHARE/BACK
        "emergency_stop": 0, # X/A
        "gripper_toggle": 6  # L2
    }

    def __init__(
        self,
        speed_multiplier: float = 0.2,
        dead_zone: float = 0.15,
        button_mapping: Optional[Dict[str, int]] = None,
    ) -> None:
        # ── Inicialización de pygame ────────────────────────────────────────
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No se detectó ningún game-pad conectado")

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        # ── Configuración interna ───────────────────────────────────────────
        self.speed_multiplier = speed_multiplier
        self.dead_zone = dead_zone
        self.precision_mode = False

        # Mapeo de botones (permite sobreescribir)
        self.button_mapping: Dict[str, int] = (
            button_mapping if button_mapping is not None else self.DEFAULT_BUTTON_MAPPING
        )
        # Estados anteriores de botones para *edge detection*
        self._prev_button_states: Dict[str, bool] = {name: False for name in self.button_mapping}

    # ---------------------------------------------------------------------
    #  Métodos públicos
    # ---------------------------------------------------------------------
    def read_action(self) -> np.ndarray:
        """Devuelve un vector de 6 DOF adaptado al *robot env*.

        Orden de componentes: \(x, y, z, r_x, r_y, r_z\).

        Mapeo actual de controles:
            • Sticks analógicos:  desplazamiento X/Y/Z y rotación Y.
            • Cruceta (D-pad):
                  – Arriba / Abajo  → r_x  (tercer eje / falange)
                  – Izquierda / Derecha → r_z  (garra abrir/cerrar)
        """
        pygame.event.pump()  # Actualizar estado interno de *pygame*

        # Trasladar sticks analógicos a ejes cartesianos.
        x = self._axis_value(0)
        y = -self._axis_value(1)  # convención: arriba es positivo
        z = -self._axis_value(4)  # stick derecho vertical

        # ------------------------------------------------------------------
        #  Cruceta (HAT) → nuevo mapeo solicitado
        #    • Izquierda / Derecha  → Control de garra (rz)
        #    • Arriba / Abajo      → Rotación X / tercer eje (rx)
        # ------------------------------------------------------------------
        hat_x = hat_y = 0
        if self.joystick.get_numhats() > 0:
            hat_x, hat_y = self.joystick.get_hat(0)  # valores -1, 0, 1

        # Rotación X (tercer eje) controlada por arriba/abajo de la cruceta
        rx = float(hat_y)  # +1 arriba, -1 abajo

        # Rotación Y se mantiene con el stick derecho horizontal
        ry = self._axis_value(3)

        # Garra controlada por izquierda/derecha de la cruceta
        # Izquierda (−1) ⇒ abrir  (rz = -1)
        # Derecha  (+1) ⇒ cerrar (rz =  1)
        rz = float(hat_x)

        speed = self.speed_multiplier * (0.3 if self.precision_mode else 1.0)
        return np.array([
            x * speed,
            y * speed,
            z * speed,
            rx * speed,       # Ganancia completa para r_x (cruceta arriba/abajo)
            ry * speed * 0.5, # Se mantiene 0.5 para rotación Y con stick
            rz * speed,       # Ganancia completa para r_z (cruceta izq/der)
        ])

    def button_pressed(self, name: str) -> bool:
        """Devuelve True *solo* en el *flanco de subida* del botón."""
        btn_id = self.button_mapping.get(name)
        if btn_id is None or btn_id >= self.joystick.get_numbuttons():
            return False
        current_state = self.joystick.get_button(btn_id)
        prev_state = self._prev_button_states[name]
        self._prev_button_states[name] = bool(current_state)
        return bool(current_state and not prev_state)

    # ------------------------------------------------------------------
    #  Métodos auxiliares privados
    # ------------------------------------------------------------------
    def _axis_value(self, axis_id: int) -> float:
        """Aplica zona muerta a un eje."""
        if axis_id >= self.joystick.get_numaxes():
            return 0.0
        val = self.joystick.get_axis(axis_id)
        return val if abs(val) > self.dead_zone else 0.0 