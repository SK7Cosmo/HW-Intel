"""
GPU / Graphics Provider
Gathers graphics adapter information from WMI.
"""
from __future__ import annotations

def _get_wmi():
    try:
        import wmi
        return wmi.WMI()
    except Exception:
        return None


def _parse_vram(adapter_ram: int | None) -> str | None:
    if not adapter_ram:
        return None
    gb = adapter_ram / (1024 ** 3)
    mb = adapter_ram / (1024 ** 2)
    if gb >= 1:
        return f"{gb:.1f} GB"
    return f"{mb:.0f} MB"


def get_gpu_data() -> list[dict]:
    """Return list of graphics adapters."""
    gpus = []
    w = _get_wmi()

    if w:
        try:
            for g in w.Win32_VideoController():
                vram_raw = g.AdapterRAM
                # Windows caps AdapterRAM at 4GB for 32-bit field, clip unrealistic values
                if vram_raw and vram_raw > 32 * 1024 ** 3:
                    vram_raw = None
                gpus.append({
                    "name": (g.Name or "").strip(),
                    "device_id": (g.PNPDeviceID or "").strip(),
                    "adapter_ram_bytes": vram_raw,
                    "adapter_ram_str": _parse_vram(vram_raw),
                    "driver_version": (g.DriverVersion or "").strip(),
                    "driver_date": str(g.DriverDate or "")[:8] or None,
                    "video_mode": (g.VideoModeDescription or "").strip(),
                    "current_refresh_hz": g.CurrentRefreshRate,
                    "bits_per_pixel": g.CurrentBitsPerPixel,
                    "current_h_res": g.CurrentHorizontalResolution,
                    "current_v_res": g.CurrentVerticalResolution,
                    "status": (g.Status or "").strip(),
                    "video_processor": (g.VideoProcessor or "").strip(),
                    "caption": (g.Caption or "").strip(),
                })
        except Exception:
            pass

    return gpus
