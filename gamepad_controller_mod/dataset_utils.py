"""dataset_utils.py

Funciones auxiliares para gestionar la persistencia de episodios grabados y
estadísticas básicas del dataset.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import pickle
from typing import List, Dict, Any

import numpy as np

# ---------------------------------------------------------------------------
#  Funciones de ruta y guardado
# ---------------------------------------------------------------------------

def create_session_path(session_id: str, base_dir: str | Path = "./datasets") -> Path:
    """Crea (si no existe) el directorio donde se almacenará la sesión."""
    p = Path(base_dir) / f"gamepad_session_{session_id}"
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_progress(episodes: List[Dict[str, Any]], session_path: Path, count: int, session_id: str) -> Path:
    """Guarda un snapshot intermedio cada *count* episodios."""
    filename = f"progress_{session_id}_{count:03d}.pkl"
    filepath = session_path / filename
    data = {
        "episodes": episodes,
        "count": count,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
    }
    with open(filepath, "wb") as f:
        pickle.dump(data, f)
    return filepath


def save_final_dataset(episodes: List[Dict[str, Any]], session_path: Path, session_id: str) -> Path:
    """Guarda el dataset final y una versión resumida con nombre compacto."""
    main_name = f"dataset_{session_id}_final.pkl"
    main_path = session_path / main_name

    summary_name = f"dataset_{len(episodes)}eps_{datetime.now().strftime('%m%d_%H%M')}.pkl"
    summary_path = session_path / summary_name

    dataset = {
        "episodes": episodes,
        "session_info": {
            "session_id": session_id,
            "total_episodes": len(episodes),
            "creation_time": datetime.now().isoformat(),
        },
        "statistics": calculate_stats(episodes),
    }
    for path in (main_path, summary_path):
        with open(path, "wb") as f:
            pickle.dump(dataset, f)
    return main_path

# ---------------------------------------------------------------------------
#  Estadísticas
# ---------------------------------------------------------------------------

def calculate_stats(episodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not episodes:
        return {}
    lengths = [len(ep["actions"]) for ep in episodes]
    rewards = [sum(ep["rewards"]) for ep in episodes]
    durations = [ep["metadata"].get("duration", 0) for ep in episodes]

    return {
        "total_episodes": len(episodes),
        "avg_steps": float(np.mean(lengths)),
        "avg_reward": float(np.mean(rewards)),
        "best_reward": float(np.max(rewards)),
        "worst_reward": float(np.min(rewards)),
        "avg_duration": float(np.mean(durations)),
        "total_duration": float(np.sum(durations)),
        "episode_lengths": lengths,
        "rewards": rewards,
    }

# ---------------------------------------------------------------------------


def list_existing_sessions(base_dir: str | Path = "./datasets") -> None:
    base = Path(base_dir)
    if not base.exists():
        print("📁 No hay datasets previos")
        return
    print("📚 DATASETS EXISTENTES:")
    for session_dir in sorted(base.glob("gamepad_session_*")):
        session_id = session_dir.name.replace("gamepad_session_", "")
        files = list(session_dir.glob("*.pkl"))
        print(f"   📂 Sesión {session_id}:")
        for f in sorted(files):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"      📄 {f.name} ({size_mb:.1f} MB)") 