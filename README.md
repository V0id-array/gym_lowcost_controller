# Grabador de demostraciones con mando para **Low-Cost Robot 6DoF**

![Python](https://img.shields.io/badge/python-%3E%3D3.9-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Este proyecto permite **controlar** un brazo robótico simulado (MuJoCo) mediante un *game-pad* (PS4, Xbox, etc.) y **grabar datasets** de demostraciones humanas para tareas de manipulación como *pick-and-place*.

Incluye dos componentes principales:

1. `gamepad_controller_mod/`  – biblioteca modular que gestiona el mando, la lógica de grabación y la persistencia de datos.
2. `gym-lowcostrobot/`        – paquete con entornos Gymnasium para el robot de 6 grados de libertad.  El entorno *PickPlaceCube* ha sido modificado para que el cubo y la zona objetivo sean más grandes, facilitando la tarea.

---
## Tabla de contenidos
1. [Características](#características)
2. [Instalación](#instalación)
3. [Uso rápido](#uso-rápido)
4. [Controles del mando](#controles-del-mando)
5. [Estructura de directorios](#estructura-de-directorios)
6. [Formato del dataset](#formato-del-dataset)
7. [Contribución](#contribución)
8. [Licencia](#licencia)

---
## Características
* ✔️ Control en tiempo real (~30 FPS) con **pygame**.
* ✔️ Grabación ilimitada de episodios con auto-guardado incremental y estadísticas.
* ✔️ Mapeo intuitivo:
  * Sticks → traslación XYZ + rotación Y
  * Cruceta → rotación X (arriba/abajo) y control de garra (izq/der)
* ✔️ Modo precisión, ajuste dinámico de velocidad y pausa.
* ✔️ Entornos Gymnasium sin límite de pasos (`NoTimeLimitWrapper`).
* ✔️ Dataset en `pickle` + resumen TXT por sesión.

---
## Instalación
### Requisitos previos
* **Python ≥ 3.9**
* **MuJoCo 3.x** – Descarga en <https://mujoco.org>
* **SDL2** (para pygame) – la mayoría de distros Linux ya lo incluyen.
* Un game-pad reconocido por el sistema.

### Pasos
```bash
# 1) Clona este repositorio
$ git clone https://github.com/V0id_array/lowcostrobot_gamepad.git
$ cd lowcostrobot_gamepad

# 2) Crea un entorno virtual
$ python -m venv venv
$ source venv/bin/activate  # Windows: venv\Scripts\activate

# 3) Instala las dependencias
$ pip install -r requirements.txt

# 4) Instala el paquete de entornos en modo editable
$ pip install -e ./gym-lowcostrobot
```
> ⚠️  Si MuJoCo no se detecta automáticamente, define la variable:
> ```bash
> export MUJOCO_GL=egl  # o "osmesa", según tu GPU/driver
> ```

---
## Uso rápido
```bash
# Lanzar el grabador
$ python -m gamepad_controller_mod
```
En la primera ejecución se mostrará un panel con los controles.  Cada sesión genera su propia carpeta en `datasets/`.

---
## Controles del mando
| Acción                              | Botón / Eje                           |
|-------------------------------------|----------------------------------------|
| **Iniciar / parar grabación**       | START / OPTIONS                       |
| **Parada de emergencia**            | X / A                                 |
| Pausa / Reanudar                    | SHARE / BACK                          |
| Reset entorno                       | Círculo / B                           |
| Modo precisión                      | Cuadrado / X                          |
| Subir velocidad                     | L1                                    |
| Bajar velocidad                     | R1                                    |
| Movimiento X/Y                      | Stick izquierdo                       |
| Movimiento Z                        | Stick derecho (vertical)              |
| Rotación Y                          | Stick derecho (horizontal)            |
| Rotación X (falange)                | Cruceta ↑ / ↓                         |
| Garra abrir / cerrar                | Cruceta ← (abrir) / → (cerrar)        |

---
## Estructura de directorios
```
project_root/
├── gamepad_controller_mod/   # Código del controlador modular
├── gym-lowcostrobot/         # Entornos Gym + assets MuJoCo
├── datasets/                 # Se crea automáticamente (demostraciones)
├── requirements.txt          # Dependencias de Python
└── README_CONTROLLER.md      # Este archivo
```

---
## Formato del dataset
Cada **episodio** se almacena como un diccionario con:
* `observations` – lista de dicts Gym.
* `actions`      – `np.ndarray` (N × 6)
* `rewards`      – lista de float.
* `dones`        – lista de bool.
* `infos`        – lista de dicts.
* `metadata`     – tiempo inicio, duración, pasos, etc.

Los ficheros se guardan en `datasets/gamepad_session_<timestamp>/`:
* `dataset_<timestamp>_final.pkl` – dataset completo.
* `progress_<timestamp>_###.pkl` – checkpoints automáticos.
* `RESUMEN_<timestamp>.txt`      – resumen legible.

---
## Contribución
¡Se agradecen *issues* y *pull requests*!
1. Crea una *branch* descriptiva.
2. Lanza `pytest` (tests por añadir) y `flake8`.
3. Envía tu PR.

Para cambios mayores, abre primero un issue explicando tu propuesta.

---
## Licencia
[MIT](LICENSE) 