"""
Hardware Intelligence Dashboard — FastAPI Backend
Serves hardware data via REST API on http://127.0.0.1:7890
"""
from __future__ import annotations
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import psutil

from providers.cpu_provider import get_cpu_data
from providers.memory_provider import get_memory_data
from providers.mainboard_provider import get_mainboard_data
from providers.gpu_provider import get_gpu_data
from providers.system_provider import get_system_data

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Hardware Intelligence Dashboard API",
    description="Modern CPU-Z inspired hardware information API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:7890", "http://localhost:7890"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Serve frontend
_FRONTEND = Path(__file__).parent.parent / "frontend"
if _FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=str(_FRONTEND)), name="static")

# ── Cache ─────────────────────────────────────────────────────────────────────
_CACHE: dict[str, Any] = {}
_CACHE_TTL = 30  # seconds for dynamic fields; static fields cached longer

_STATIC_TTL = 3600   # 1 hour for static hw info
_DYNAMIC_TTL = 5     # 5 seconds for live readings

def _cached(key: str, fn, ttl: int = _STATIC_TTL) -> Any:
    now = time.monotonic()
    if key in _CACHE:
        data, ts = _CACHE[key]
        if now - ts < ttl:
            return data
    data = fn()
    _CACHE[key] = (data, now)
    return data


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    index = _FRONTEND / "index.html"
    if index.exists():
        return HTMLResponse(content=index.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Hardware Intelligence Dashboard</h1><p>Frontend not found.</p>")


@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat(), "version": "1.0.0"}


@app.get("/api/overview")
async def overview():
    """System overview combining key fields from all sections."""
    try:
        cpu = _cached("cpu", get_cpu_data, _STATIC_TTL)
        mem = _cached("mem", get_memory_data, _STATIC_TTL)
        board = _cached("board", get_mainboard_data, _STATIC_TTL)
        gpus = _cached("gpu", get_gpu_data, _STATIC_TTL)
        sys = _cached("sys", get_system_data, _STATIC_TTL)

        # Live CPU usage
        live_cpu_pct = psutil.cpu_percent(interval=0.1)
        vm = psutil.virtual_memory()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "name": cpu["name"],
                "generation": cpu["generation"],
                "microarchitecture": cpu["microarchitecture"],
                "cores": cpu["cores"],
                "threads": cpu["threads"],
                "base_clock_mhz": cpu["base_clock_mhz"],
                "max_turbo_mhz": cpu["max_turbo_mhz"],
                "l3_cache_kb": cpu["l3_cache_kb"],
                "usage_pct": live_cpu_pct,
            },
            "memory": {
                "total_gb": mem["total_gb"],
                "available_gb": mem["available_gb"],
                "used_pct": vm.percent,
                "memory_type": mem["memory_type"],
                "speed_mts": mem["speed_mts"],
                "channel_config": mem["channel_config"],
                "module_count": len(mem["modules"]),
            },
            "board": {
                "manufacturer": board["board"].get("manufacturer"),
                "product": board["board"].get("product"),
                "bios_version": board["bios"].get("version"),
                "bios_date": board["bios"].get("release_date"),
            },
            "gpu": [{"name": g["name"], "vram": g["adapter_ram_str"], "driver": g["driver_version"]} for g in gpus],
            "os": {
                "name": sys["os"].get("name"),
                "version": sys["os"].get("version"),
                "build": sys["os"].get("build"),
                "architecture": sys["os"].get("architecture"),
            },
            "battery": sys.get("battery") or sys.get("psutil_battery"),
        }
    except Exception as e:
        log.exception("overview error")
        raise HTTPException(500, str(e))


@app.get("/api/cpu")
async def cpu():
    try:
        return _cached("cpu", get_cpu_data, _STATIC_TTL)
    except Exception as e:
        log.exception("cpu error")
        raise HTTPException(500, str(e))


@app.get("/api/cpu/live")
async def cpu_live():
    """Live per-core utilization and clock frequency."""
    try:
        per_core_pct = psutil.cpu_percent(interval=0.1, percpu=True)
        freq = psutil.cpu_freq(percpu=True)
        overall = psutil.cpu_percent(interval=None)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_pct": overall,
            "per_core_pct": per_core_pct,
            "per_core_freq_mhz": [f.current for f in freq] if freq else [],
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/memory")
async def memory():
    try:
        data = _cached("mem", get_memory_data, _STATIC_TTL)
        # Merge live usage
        vm = psutil.virtual_memory()
        data["live"] = {
            "used_pct": vm.percent,
            "available_gb": round(vm.available / (1024 ** 3), 2),
            "used_gb": round(vm.used / (1024 ** 3), 2),
        }
        return data
    except Exception as e:
        log.exception("memory error")
        raise HTTPException(500, str(e))


@app.get("/api/mainboard")
async def mainboard():
    try:
        return _cached("board", get_mainboard_data, _STATIC_TTL)
    except Exception as e:
        log.exception("mainboard error")
        raise HTTPException(500, str(e))


@app.get("/api/gpu")
async def gpu():
    try:
        return _cached("gpu", get_gpu_data, _STATIC_TTL)
    except Exception as e:
        log.exception("gpu error")
        raise HTTPException(500, str(e))


@app.get("/api/system")
async def system():
    try:
        data = _cached("sys", get_system_data, _STATIC_TTL)
        # Add live stats
        vm = psutil.virtual_memory()
        data["live"] = {
            "cpu_pct": psutil.cpu_percent(interval=0.1),
            "mem_pct": vm.percent,
        }
        return data
    except Exception as e:
        log.exception("system error")
        raise HTTPException(500, str(e))


@app.get("/api/export/json")
async def export_json():
    """Export full hardware snapshot as JSON."""
    try:
        payload = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "cpu": _cached("cpu", get_cpu_data, _STATIC_TTL),
            "memory": _cached("mem", get_memory_data, _STATIC_TTL),
            "mainboard": _cached("board", get_mainboard_data, _STATIC_TTL),
            "gpu": _cached("gpu", get_gpu_data, _STATIC_TTL),
            "system": _cached("sys", get_system_data, _STATIC_TTL),
        }
        return JSONResponse(content=payload, headers={"Content-Disposition": "attachment; filename=hw_export.json"})
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/export/csv")
async def export_csv():
    """Export key hardware fields as CSV."""
    import io, csv as csv_mod
    try:
        cpu = _cached("cpu", get_cpu_data, _STATIC_TTL)
        mem = _cached("mem", get_memory_data, _STATIC_TTL)
        board = _cached("board", get_mainboard_data, _STATIC_TTL)
        gpus = _cached("gpu", get_gpu_data, _STATIC_TTL)
        sys = _cached("sys", get_system_data, _STATIC_TTL)

        rows = [
            ["Section", "Field", "Value", "Unit", "Source"],
            ["CPU", "Name", cpu["name"], "", "WMI"],
            ["CPU", "Microarchitecture", cpu["microarchitecture"], "", "Inferred"],
            ["CPU", "Cores", cpu["cores"], "", "WMI"],
            ["CPU", "Threads", cpu["threads"], "", "WMI"],
            ["CPU", "Base Clock", cpu["base_clock_mhz"], "MHz", "WMI"],
            ["CPU", "Max Turbo", cpu["max_turbo_mhz"], "MHz", "WMI"],
            ["CPU", "L2 Cache", cpu["l2_cache_kb"], "KB", "WMI"],
            ["CPU", "L3 Cache", cpu["l3_cache_kb"], "KB", "WMI"],
            ["Memory", "Total", mem["total_gb"], "GB", "psutil"],
            ["Memory", "Type", mem["memory_type"], "", "WMI/SMBIOS"],
            ["Memory", "Speed", mem["speed_mts"], "MT/s", "WMI"],
            ["Memory", "Channels", mem["channel_config"], "", "Inferred"],
            ["Mainboard", "Manufacturer", board["board"].get("manufacturer"), "", "WMI"],
            ["Mainboard", "Model", board["board"].get("product"), "", "WMI"],
            ["Mainboard", "BIOS Version", board["bios"].get("version"), "", "WMI"],
            ["Mainboard", "BIOS Date", board["bios"].get("release_date"), "", "WMI"],
            ["GPU", "Name", gpus[0]["name"] if gpus else "N/A", "", "WMI"],
            ["GPU", "VRAM", gpus[0]["adapter_ram_str"] if gpus else "N/A", "", "WMI"],
            ["GPU", "Driver", gpus[0]["driver_version"] if gpus else "N/A", "", "WMI"],
            ["OS", "Name", sys["os"].get("name"), "", "WMI"],
            ["OS", "Build", sys["os"].get("build"), "", "WMI"],
            ["OS", "Architecture", sys["os"].get("architecture"), "", "WMI"],
        ]

        buf = io.StringIO()
        w = csv_mod.writer(buf)
        w.writerows(rows)
        return HTMLResponse(
            content=buf.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=hw_export.csv"},
        )
    except Exception as e:
        raise HTTPException(500, str(e))
