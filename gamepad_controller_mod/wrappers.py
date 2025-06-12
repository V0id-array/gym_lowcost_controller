"""wrappers.py

Utilidades relacionadas con wrappers de Gym/CSP.
"""

import gymnasium as gym

class NoTimeLimitWrapper(gym.Wrapper):
    """Wrapper que elimina el `TimeLimit` para permitir episodios ilimitados.

    Al envolver un entorno con *TimeLimit*, Gym marca el episodio como
    `truncated=True` cuando se supera el número máximo de pasos.  Este wrapper
    anula ese comportamiento poniendo siempre `truncated=False` y dejando
    únicamente que la lógica interna del entorno determine `terminated`.
    """

    def __init__(self, env: gym.Env):
        super().__init__(env)
        # Si el entorno original expone el atributo, lo anulamos.
        if hasattr(env, "_max_episode_steps"):
            self._max_episode_steps = None

    def step(self, action):  # type: ignore[override]
        observation, reward, terminated, truncated, info = self.env.step(action)
        # Siempre devolver truncated=False para episodios ilimitados.
        return observation, reward, terminated, False, info 