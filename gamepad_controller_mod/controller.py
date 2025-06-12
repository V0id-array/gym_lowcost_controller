"""controller.py

Combina *input_handler*, *dataset_utils* y *wrappers* para la interacción en
vivo con el entorno y la grabación de demostraciones.
"""

from __future__ import annotations

import time
from datetime import datetime

import gymnasium as gym
import numpy as np
import pygame
import gym_lowcostrobot  # Asegura el registro de entornos personalizados

from .input_handler import GamepadInputHandler
from .wrappers import NoTimeLimitWrapper
from . import dataset_utils as du


class DemoRecorder:
    """Gestiona el ciclo de grabación de episodios con un mando."""

    def __init__(self, env_name: str = "PickPlaceCube-v0", max_episodes: int = 10) -> None:
        self.input = GamepadInputHandler()
        self.env_name = env_name
        self.max_episodes = max_episodes
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Ruta
        self.session_path = du.create_session_path(self.session_id)

        # Entorno sin límite de tiempo
        base_env = gym.make(env_name, render_mode="human")
        self.env = NoTimeLimitWrapper(base_env)

        # Almacenes
        self.episodes: list[dict] = []
        self.recording = False

        # Consola de bienvenida
        self._print_controls()

    # ------------------------------------------------------------------
    def run(self) -> None:
        observation, info = self.env.reset()
        clock = pygame.time.Clock()
        step_count = 0
        recording_start = 0.0
        current_ep: dict | None = None
        paused = False

        try:
            while len(self.episodes) < self.max_episodes:
                now = time.time()

                # Leer entradas
                action = self.input.read_action()

                # ── Gestión de botones ────────────────────────────────────
                if self.input.button_pressed("record_toggle"):
                    if not self.recording:
                        # Iniciar grabación
                        self.recording = True
                        recording_start = now
                        step_count = 0
                        current_ep = {
                            "observations": [observation.copy()],
                            "actions": [],
                            "rewards": [],
                            "dones": [],
                            "infos": [info.copy() if isinstance(info, dict) else info],
                            "metadata": {"start_time": now},
                        }
                        print(f"\n🔴 GRABANDO episodio {len(self.episodes) + 1}")
                    else:
                        # Detener grabación
                        self.recording = False
                        if current_ep and len(current_ep["actions"]) > 10:
                            dur = now - recording_start
                            current_ep["metadata"].update(
                                duration=dur, total_steps=len(current_ep["actions"])
                            )
                            self.episodes.append(current_ep)
                            print(
                                f"✅ Episodio {len(self.episodes)} guardado: "
                                f"{len(current_ep['actions'])} pasos, {dur:.1f}s"
                            )
                            if len(self.episodes) % 3 == 0:
                                du.save_progress(
                                    self.episodes, self.session_path, len(self.episodes), self.session_id
                                )
                        else:
                            print("❌ Episodio demasiado corto; descartado")
                        current_ep = None

                if self.input.button_pressed("precision"):
                    self.input.precision_mode = not self.input.precision_mode
                    estado = "ON" if self.input.precision_mode else "OFF"
                    print(f"🎯 Modo precisión: {estado}")

                if self.input.button_pressed("speed_up"):
                    self.input.speed_multiplier = min(0.8, self.input.speed_multiplier + 0.05)
                    print(f"⬆️  Velocidad: {self.input.speed_multiplier:.2f}")
                if self.input.button_pressed("speed_down"):
                    self.input.speed_multiplier = max(0.05, self.input.speed_multiplier - 0.05)
                    print(f"⬇️  Velocidad: {self.input.speed_multiplier:.2f}")

                if self.input.button_pressed("pause"):
                    paused = not paused
                    print("⏸️  Pausado" if paused else "▶️  Reanudado")

                if self.input.button_pressed("reset"):
                    observation, info = self.env.reset()
                    step_count = 0
                    print("🔄 Reset del entorno")

                if self.input.button_pressed("quit"):
                    print("🚪 Saliendo...")
                    break

                # ── Avance del entorno ───────────────────────────────────
                if not paused and np.any(np.abs(action) > 0.01):
                    observation, reward, terminated, truncated, info = self.env.step(action)
                    step_count += 1
                    if self.recording and current_ep is not None:
                        current_ep["observations"].append(observation.copy())
                        current_ep["actions"].append(action.copy())
                        current_ep["rewards"].append(reward)
                        current_ep["dones"].append(terminated or truncated)
                        current_ep["infos"].append(info.copy() if isinstance(info, dict) else info)
                    if terminated:
                        observation, info = self.env.reset()
                        step_count = 0
                        print("🏁 Episodio terminado por condición interna del entorno")

                if self.recording and step_count % 150 == 0 and step_count > 0:
                    print(f"🔴 Grabando: {step_count} pasos, {now - recording_start:.1f}s")

                clock.tick(30)

        except KeyboardInterrupt:
            print("\nInterrumpido por el usuario")
        finally:
            self._finalize()

    # ------------------------------------------------------------------
    def _finalize(self) -> None:
        if self.episodes:
            du.save_final_dataset(self.episodes, self.session_path, self.session_id)
        self.env.close()
        pygame.quit()
        print("👋 Sesión finalizada")

    # ------------------------------------------------------------------
    def _print_controls(self) -> None:
        print("=" * 60)
        print("🎮 Grabador modular de demostraciones")
        print("Presiona START para comenzar/terminar una grabación.")
        print("Triángulo/Y para salir. Cuadrado/X cambia modo precisión.")
        print("=" * 60)


def run_cli() -> None:
    """Punto de entrada simple: `python -m gamepad_controller_mod`"""
    rec = DemoRecorder()
    rec.run()


if __name__ == "__main__":
    run_cli() 