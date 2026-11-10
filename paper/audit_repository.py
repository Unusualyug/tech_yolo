#!/usr/bin/env python3
"""Static, reproducible audit of the tech_yolo source snapshot.

The audited tree is pinned to SOURCE_COMMIT, so later manuscript artifacts do
not change the source-file census. This script does not import Flask, OpenCV,
Ultralytics, gTTS, or load model weights. It uses the Python standard library
to inspect source artifacts and produce a JSON record for the manuscript.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "6a0405613171a5ed400a7339c3e0a8f6bb94b26d"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def parse_module(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path.relative_to(ROOT)))


def get_routes(tree: ast.Module) -> list[dict]:
    routes = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            func = dec.func
            if not (isinstance(func, ast.Attribute) and func.attr == "route"):
                continue
            if not dec.args or not isinstance(dec.args[0], ast.Constant):
                continue
            methods = None
            for kw in dec.keywords:
                if kw.arg == "methods":
                    try:
                        methods = ast.literal_eval(kw.value)
                    except Exception:
                        methods = None
            routes.append({
                "path": dec.args[0].value,
                "handler": node.name,
                "methods": methods or ["GET"],
                "line": node.lineno,
            })
    return sorted(routes, key=lambda x: x["line"])


def first_literal_assignment(tree: ast.Module, name: str):
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        else:
            continue
        if any(isinstance(t, ast.Name) and t.id == name for t in targets):
            try:
                return ast.literal_eval(value)
            except Exception:
                return None
    return None


def dedupe(seq):
    return list(dict.fromkeys(seq))


def predict_arguments(tree: ast.Module) -> dict:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "predict":
            out = {}
            for kw in node.keywords:
                try:
                    out[kw.arg] = ast.literal_eval(kw.value)
                except Exception:
                    out[kw.arg] = "expression"
            return out
    return {}


def frontend_endpoints() -> dict:
    js = (ROOT / "static/script.js").read_text(encoding="utf-8")
    html = (ROOT / "templates/index.html").read_text(encoding="utf-8")
    pattern = re.compile(r"['\"`](/[A-Za-z0-9_]+)(?:\?[^'\"`]*)?['\"`]")
    js_paths = sorted(set(pattern.findall(js)))
    html_paths = sorted(set(pattern.findall(html)))
    return {
        "script_js": js_paths,
        "index_html": html_paths,
        "union": sorted(set(js_paths) | set(html_paths)),
    }


def lfs_pointers() -> list[dict]:
    out = []
    for path in sorted(ROOT.rglob("*.pt")):
        text = path.read_text(encoding="utf-8", errors="replace")
        record = {"path": str(path.relative_to(ROOT)), "is_lfs_pointer": text.startswith("version https://git-lfs.github.com/spec/v1")}
        if record["is_lfs_pointer"]:
            oid = re.search(r"oid sha256:([0-9a-f]+)", text)
            size = re.search(r"size (\d+)", text)
            record["oid_sha256"] = oid.group(1) if oid else None
            record["declared_bytes"] = int(size.group(1)) if size else None
        else:
            record["file_bytes"] = path.stat().st_size
        out.append(record)
    return out


def main() -> None:
    tree_app = parse_module(ROOT / "app.py")
    tree_app23 = parse_module(ROOT / "app23.py")
    tree_camera = parse_module(ROOT / "camera_test.py")

    routes_app = get_routes(tree_app)
    routes_app23 = get_routes(tree_app23)
    endpoints = frontend_endpoints()

    vocab_raw = first_literal_assignment(tree_app23, "VOCABULARY") or []
    language_map = first_literal_assignment(tree_app23, "language_code_map") or {}
    speech_prefixes = first_literal_assignment(tree_app23, "speech_prefixes") or {}
    face_greetings = first_literal_assignment(tree_app23, "face_greetings") or {}

    def variant_summary(tree, filename: str) -> dict:
        v = first_literal_assignment(tree, "VOCABULARY") or []
        lm = first_literal_assignment(tree, "language_code_map") or {}
        main_template = first_literal_assignment(tree, "speech_prefixes") or first_literal_assignment(tree, "translations") or {}
        details = first_literal_assignment(tree, "object_detail_templates") or {}
        greetings = first_literal_assignment(tree, "face_greetings") or {}
        return {
            "file": filename,
            "lines": len((ROOT / filename).read_text(encoding="utf-8").splitlines()),
            "routes": len(get_routes(tree)),
            "vocabulary_raw": len(v),
            "vocabulary_unique": len(dedupe(v)),
            "language_code_entries": len(lm),
            "main_speech_templates": len(main_template),
            "object_detail_templates": len(details),
            "face_greeting_templates": len(greetings),
            "max_objects_to_speak": first_literal_assignment(tree, "MAX_OBJECTS_TO_SPEAK"),
            "speech_cooldown_seconds": first_literal_assignment(tree, "SPEECH_COOLDOWN"),
            "predict_arguments": predict_arguments(tree),
        }

    backend_variants = {
        "app.py": variant_summary(tree_app, "app.py"),
        "app23.py": variant_summary(tree_app23, "app23.py"),
    }

    coco_labels = [x.strip() for x in (ROOT / "utils/coco.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    tracked = git("ls-tree", "-r", "--name-only", SOURCE_COMMIT).splitlines()

    mp3s = []
    for path in sorted(ROOT.glob("*.mp3")):
        mp3s.append({"path": path.name, "bytes": path.stat().st_size})

    source_files = ["app.py", "app23.py", "camera_test.py", "static/script.js", "templates/index.html", "static/style.css", "utils/coco.txt"]
    syntax = {}
    for rel in ["app.py", "app23.py", "camera_test.py"]:
        try:
            parse_module(ROOT / rel)
            syntax[rel] = "pass"
        except SyntaxError as exc:
            syntax[rel] = f"fail: {exc}"

    app23_route_paths = {r["path"] for r in routes_app23}
    app_route_paths = {r["path"] for r in routes_app}
    frontend_union = set(endpoints["union"])

    result = {
        "audit_date": "2026-11-10",
        "repository": "Unusualyug/tech_yolo",
        "branch": git("branch", "--show-current"),
        "commit": SOURCE_COMMIT,
        "audited_tree": SOURCE_COMMIT,
        "python_ast_runtime": "CPython 3.11.2 (standard-library ast module)",
        "tracked_file_count": len(tracked),
        "tracked_files": tracked,
        "source_syntax_parse": syntax,
        "backend_variants": backend_variants,
        "python_files": {
            "app.py": {"lines": len((ROOT / "app.py").read_text(encoding="utf-8").splitlines()), "routes": len(routes_app), "top_level_functions": sum(isinstance(n, ast.FunctionDef) for n in tree_app.body)},
            "app23.py": {"lines": len((ROOT / "app23.py").read_text(encoding="utf-8").splitlines()), "routes": len(routes_app23), "top_level_functions": sum(isinstance(n, ast.FunctionDef) for n in tree_app23.body)},
            "camera_test.py": {"lines": len((ROOT / "camera_test.py").read_text(encoding="utf-8").splitlines()), "top_level_functions": sum(isinstance(n, ast.FunctionDef) for n in tree_camera.body)},
        },
        "configuration_constants_app23": {
            "model_name": first_literal_assignment(tree_app23, "MODEL_NAME"),
            "webcam_index": first_literal_assignment(tree_app23, "WEBCAM_INDEX"),
            "camera_width": first_literal_assignment(tree_app23, "CAMERA_WIDTH"),
            "camera_height": first_literal_assignment(tree_app23, "CAMERA_HEIGHT"),
            "img_size": first_literal_assignment(tree_app23, "IMG_SIZE"),
            "confidence_threshold": first_literal_assignment(tree_app23, "confidence_threshold"),
            "interval_seconds": first_literal_assignment(tree_app23, "INTERVAL"),
            "known_width": first_literal_assignment(tree_app23, "KNOWN_WIDTH"),
            "focal_length": first_literal_assignment(tree_app23, "FOCAL_LENGTH"),
            "speech_cooldown_seconds": first_literal_assignment(tree_app23, "SPEECH_COOLDOWN"),
            "max_objects_to_speak": first_literal_assignment(tree_app23, "MAX_OBJECTS_TO_SPEAK"),
            "face_greeting_cooldown_seconds": first_literal_assignment(tree_app23, "FACE_GREETING_COOLDOWN"),
        },
        "vocabulary": {
            "raw_entries": len(vocab_raw),
            "unique_entries": len(dedupe(vocab_raw)),
        },
        "language_resources": {
            "language_code_map_entries": len(language_map),
            "speech_prefix_entries": len(speech_prefixes),
            "face_greeting_entries": len(face_greetings),
        },
        "coco_label_file": {
            "nonempty_labels": len(coco_labels),
            "unique_labels": len(set(coco_labels)),
            "first": coco_labels[0] if coco_labels else None,
            "last": coco_labels[-1] if coco_labels else None,
        },
        "routes": {"app.py": routes_app, "app23.py": routes_app23},
        "frontend_endpoints": endpoints,
        "route_coverage": {
            "frontend_endpoints_count": len(frontend_union),
            "endpoints_in_app23": sorted(frontend_union & app23_route_paths),
            "endpoints_missing_from_app23": sorted(frontend_union - app23_route_paths),
            "endpoints_in_app": sorted(frontend_union & app_route_paths),
            "endpoints_missing_from_app": sorted(frontend_union - app_route_paths),
        },
        "lfs_weight_pointers": lfs_pointers(),
        "mp3_artifacts": mp3s,
        "repository_checks": {
            "readme_present": any(p.lower().startswith("readme") for p in tracked),
            "license_present": any(p.lower().startswith("license") or p.lower().startswith("copying") for p in tracked),
            "requirements_present": any("requirements" in p.lower() or p in {"pyproject.toml", "environment.yml", "Pipfile"} for p in tracked),
            "tests_present": any(p.startswith("tests/") or Path(p).name.startswith("test_") for p in tracked),
            "modules_faces_present": any(p.startswith("modules/faces") for p in tracked),
            "dataset_files_present": any(p.lower().endswith((".jpg", ".jpeg", ".png", ".json", ".yaml", ".yml", ".csv")) and not p.startswith("static/") and p != "utils/coco.txt" for p in tracked),
            "model_train_calls": sum(1 for p in [ROOT / "app.py", ROOT / "app23.py"] for n in ast.walk(parse_module(p)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "train"),
            "model_val_calls": sum(1 for p in [ROOT / "app.py", ROOT / "app23.py"] for n in ast.walk(parse_module(p)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "val"),
        },
        "source_sha256": {rel: sha256(ROOT / rel) for rel in source_files},
    }

    out = ROOT / "paper/artifacts/repository_audit.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": result["commit"],
        "syntax": result["source_syntax_parse"],
        "routes_app23": len(routes_app23),
        "routes_app": len(routes_app),
        "frontend_coverage": result["route_coverage"],
        "vocabulary": result["vocabulary"],
        "backend_variants": {k: {kk: vv for kk, vv in v.items() if kk in {"routes", "vocabulary_unique", "predict_arguments", "max_objects_to_speak"}} for k, v in backend_variants.items()},
        "languages": result["language_resources"],
        "coco": result["coco_label_file"],
        "checks": result["repository_checks"],
        "output": str(out.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
