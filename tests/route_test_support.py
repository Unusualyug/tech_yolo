"""Import the maintained Flask app with mocked hardware/model dependencies.

This module uses ``unittest.mock`` and the standard library only. It does not
start the application server, open a camera, load detector weights, or call a
network speech service. Route tests exercise the real Flask ``test_client`` and
the real route functions; only their external I/O dependencies are stubbed.
"""
from __future__ import annotations

import ast
import copy
import importlib.util
import queue
import sys
import threading
import types
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_APP_MODULE: types.ModuleType | None = None
_INITIAL_STATE: dict[str, object] = {}


def _stub_modules() -> dict[str, types.ModuleType]:
    cv2 = types.ModuleType("cv2")
    cv2.CAP_ANY = 0
    cv2.CAP_PROP_FRAME_WIDTH = 3
    cv2.CAP_PROP_FRAME_HEIGHT = 4
    cv2.CAP_PROP_BUFFERSIZE = 38
    cv2.IMWRITE_JPEG_QUALITY = 1
    cv2.NORM_MINMAX = 32
    cv2.COLORMAP_JET = 2
    cv2.FONT_HERSHEY_SIMPLEX = 0
    cv2.LINE_AA = 16
    for name in (
        "VideoCapture",
        "addWeighted",
        "applyColorMap",
        "circle",
        "getTextSize",
        "imencode",
        "line",
        "normalize",
        "putText",
        "rectangle",
    ):
        setattr(cv2, name, mock.MagicMock(name=f"cv2.{name}"))

    numpy = types.ModuleType("numpy")
    numpy.float32 = float
    numpy.uint8 = int
    numpy.zeros = mock.MagicMock(name="numpy.zeros")
    numpy.array = mock.MagicMock(name="numpy.array")

    ultralytics = types.ModuleType("ultralytics")
    model = mock.MagicMock(name="YOLO_model")
    model.set_classes = mock.MagicMock(name="set_classes")
    ultralytics.YOLO = mock.MagicMock(name="YOLO", return_value=model)

    gtts = types.ModuleType("gtts")
    gtts.gTTS = mock.MagicMock(name="gTTS")

    return {
        "cv2": cv2,
        "numpy": numpy,
        "ultralytics": ultralytics,
        "gtts": gtts,
    }


def load_app() -> types.ModuleType:
    """Import ``app23.py`` once with all import-time side effects mocked."""
    global _APP_MODULE, _INITIAL_STATE
    if _APP_MODULE is not None:
        return _APP_MODULE

    stubs = _stub_modules()
    with mock.patch.dict(sys.modules, stubs), mock.patch.object(
        threading.Thread, "start", return_value=None
    ):
        spec = importlib.util.spec_from_file_location(
            "trinexis_app_route_test", ROOT / "app23.py"
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

    module.app.config["TESTING"] = True
    module.app.secret_key = "route-test-secret"
    _APP_MODULE = module
    _INITIAL_STATE = {
        "VOCABULARY": copy.deepcopy(module.VOCABULARY),
        "language_code_map": copy.deepcopy(module.language_code_map),
        "speech_prefixes": copy.deepcopy(module.speech_prefixes),
        "stats": copy.deepcopy(module.stats),
        "MODEL_NAME": module.MODEL_NAME,
        "ALERT_MANIFEST_OBJECTS": module.ALERT_MANIFEST_OBJECTS,
        "ALERT_MANIFEST_SHA256": module.ALERT_MANIFEST_SHA256,
    }
    return module


def new_client(module: types.ModuleType):
    """Return a fresh test client after resetting process-wide app state."""
    reset_state(module)
    return module.app.test_client()


def reset_state(module: types.ModuleType) -> None:
    """Reset mutable globals between tests so route order cannot affect results."""
    initial = _INITIAL_STATE
    module.VOCABULARY = copy.deepcopy(initial["VOCABULARY"])
    module.language_code_map = copy.deepcopy(initial["language_code_map"])
    module.speech_prefixes = copy.deepcopy(initial["speech_prefixes"])
    module.stats = copy.deepcopy(initial["stats"])
    module.MODEL_NAME = initial["MODEL_NAME"]
    module.ALERT_MANIFEST_OBJECTS = initial["ALERT_MANIFEST_OBJECTS"]
    module.ALERT_MANIFEST_SHA256 = initial["ALERT_MANIFEST_SHA256"]

    module.running = False
    module.prev = 0
    module.confidence_threshold = 0.15
    module.language = "English"
    module.detection_log = []
    module.IMG_SIZE = 640
    module.INTERVAL = 1.5
    module.current_frame = None
    module.heatmap_accumulator = None
    module.last_heatmap_update = None
    module.recent_inference_times = []
    module.alert_objects = set()
    module.speech_enabled = True
    module.last_spoken_time = 0
    module.last_face_greetings = {}
    module.SPEECH_COOLDOWN = 4.5
    module.MAX_OBJECTS_TO_SPEAK = 2
    module.API_TOKEN = ""
    module.READ_ONLY_MODE = False
    module.SINGLE_CLIENT_MODE = False
    module.SINGLE_CLIENT_TIMEOUT_S = 60.0
    module.ACTIVE_CLIENT_ID = None
    module.ACTIVE_CLIENT_LAST_SEEN = 0.0
    module.LATENCY_RECORDER.enabled = False
    module.SPEECH_EVENT_RECORDER.enabled = False

    while True:
        try:
            module.speech_queue.get_nowait()
            module.speech_queue.task_done()
        except queue.Empty:
            break


def route_inventory() -> list[tuple[str, str]]:
    """Return all ``(path, method)`` pairs declared in ``app23.py``."""
    source = (ROOT / "app23.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    routes: list[tuple[str, str]] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr == "route"
                and decorator.args
            ):
                continue
            path = ast.literal_eval(decorator.args[0])
            methods = ["GET"]
            for keyword in decorator.keywords:
                if keyword.arg == "methods":
                    methods = [str(item) for item in ast.literal_eval(keyword.value)]
            for method in methods:
                routes.append((path, method.upper()))
    return sorted(routes)
