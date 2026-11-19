"""Diagnóstico sin dependencias externas ni lectura de credenciales.

No crea contenedores, instala software ni conecta con Snowflake.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import platform
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def command(args):
    if not shutil.which(args[0]):
        return {"status": "no_instalado"}
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=20)
        if result.returncode:
            # No guardar stderr: puede contener rutas o configuración local.
            return {"status": "no_disponible", "returncode": result.returncode}
        return {"status": "ok", "value": result.stdout.strip()}
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "datasets")
    parser.add_argument("--skip-docker-engine", action="store_true")
    args = parser.parse_args()
    disk = shutil.disk_usage(ROOT)
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "machine": {"os": platform.system(), "architecture": platform.machine(),
                    "python": platform.python_version(), "disk_free_gib": round(disk.free / 2**30, 1)},
        "docker_client": command(["docker", "--version"]),
        "compose": command(["docker", "compose", "version"]),
        "docker_engine": {"status": "no_consultado"} if args.skip_docker_engine else command([
            "docker", "info", "--format",
            '{{json .ServerVersion}} {{json .OSType}} {{json .Architecture}} {{json .NCPU}} {{json .MemTotal}}']),
        "data": {},
        "scope": "Solo diagnóstico local. Sin servicios desplegados ni conexión Snowflake."
    }
    manifest = json.loads((ROOT / "datasets/manifest.json").read_text())
    for name, meta in manifest["files"].items():
        path = args.data_dir / name
        if not path.is_file():
            report["data"][name] = {"status": "falta"}
            continue
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                digest.update(chunk)
        report["data"][name] = {
            "status": "ok" if digest.hexdigest() == meta["sha256"] and path.stat().st_size == meta["bytes"] else "difiere_manifiesto",
            "bytes": path.stat().st_size,
        }
    report["ready_for_local_infrastructure"] = (
        report["docker_engine"]["status"] == "ok"
        and report["compose"]["status"] == "ok"
        and all(v["status"] == "ok" for v in report["data"].values())
    )
    content = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content)
    print(content, end="")
    return 0 if report["ready_for_local_infrastructure"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
