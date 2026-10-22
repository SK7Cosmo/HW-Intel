"""
Memory Hardware Provider
Gathers memory module information from WMI, including SMBIOS type decoding.
"""
from __future__ import annotations
import psutil

def _get_wmi():
    """Lazy WMI connection — avoids import-time failures."""
    try:
        import wmi
        return wmi.WMI()
    except Exception:
        return None

# SMBIOS 3.x Memory Type Table
_SMBIOS_MEMORY_TYPES = {
    0:  "Unknown",
    1:  "Other",
    2:  "DRAM",
    3:  "Synchronous DRAM",
    4:  "Cache DRAM",
    5:  "EDO",
    6:  "EDRAM",
    7:  "VRAM",
    8:  "SRAM",
    9:  "RAM",
    10: "ROM",
    11: "Flash",
    12: "EEPROM",
    13: "FEPROM",
    14: "EPROM",
    15: "CDRAM",
    16: "3DRAM",
    17: "SDRAM",
    18: "SGRAM",
    19: "RDRAM",
    20: "DDR",
    21: "DDR2",
    22: "DDR2 FB-DIMM",
    24: "DDR3",
    26: "DDR4",
    27: "LPDDR",
    28: "LPDDR2",
    29: "LPDDR3",
    30: "LPDDR4",
    34: "LPDDR5",
    35: "LPDDR5X",
    36: "DDR5",
    37: "LPDDR5",
}


def _decode_memory_type(smbios_type: int) -> str:
    return _SMBIOS_MEMORY_TYPES.get(smbios_type, f"Unknown ({smbios_type})")


def _infer_channel_config(modules: list[dict]) -> str:
    """Infer channel configuration from SMBIOS DeviceLocator data."""
    if not modules:
        return "Unknown"
    slots = [m.get("slot", "") for m in modules]
    # LPDDR5 on Lenovo: Controller0-ChannelA / Controller1-ChannelA = dual channel
    controllers = set()
    for s in slots:
        if "Controller" in s:
            import re
            m = re.search(r"Controller(\d+)", s)
            if m:
                controllers.add(int(m.group(1)))
    if len(controllers) > 1:
        return f"Dual-Channel ({len(modules)} modules across {len(controllers)} controllers)"
    if len(modules) == 2:
        return "Dual-Channel (LPDDR5 soldered)"
    if len(modules) == 4:
        return "Quad-Channel"
    if len(modules) == 1:
        return "Single-Channel"
    return f"{len(modules)} module(s)"


def get_memory_data() -> dict:
    """Return normalized memory information."""
    modules = []
    array_info = {}
    w = _get_wmi()

    if w:
        try:
            for m in w.Win32_PhysicalMemory():
                smbios_type = int(m.SMBIOSMemoryType or 0)
                mem_type = _decode_memory_type(smbios_type)
                raw_cap = int(m.Capacity or 0)
                capacity_gb = round(raw_cap / (1024 ** 3), 1)
                modules.append({
                    "slot": m.DeviceLocator or m.BankLabel or "Unknown",
                    "bank": m.BankLabel or "Unknown",
                    "capacity_gb": capacity_gb,
                    "capacity_bytes": raw_cap,
                    "speed_mts": int(m.Speed or 0),
                    "memory_type": mem_type,
                    "smbios_type": smbios_type,
                    "manufacturer": (m.Manufacturer or "Unknown").strip(),
                    "part_number": (m.PartNumber or "").strip(),
                    "serial_number": (m.SerialNumber or "").strip(),
                    "data_width": getattr(m, "DataWidth", None),
                    "total_width": getattr(m, "TotalWidth", None),
                    "form_factor": getattr(m, "FormFactor", None),
                    "voltage": getattr(m, "ConfiguredVoltage", None),
                })
        except Exception:
            pass

        try:
            arr = w.Win32_PhysicalMemoryArray()[0]
            array_info = {
                "max_capacity_kb": arr.MaxCapacity,
                "max_capacity_gb": round(arr.MaxCapacity / (1024 * 1024), 1) if arr.MaxCapacity else None,
                "slots": arr.MemoryDevices,
                "use": arr.Use,
            }
        except Exception:
            pass

    # psutil total memory
    vm = psutil.virtual_memory()
    total_gb = round(vm.total / (1024 ** 3), 2)
    available_gb = round(vm.available / (1024 ** 3), 2)
    used_pct = vm.percent

    # Infer memory type from modules
    primary_type = modules[0]["memory_type"] if modules else "Unknown"
    primary_speed = modules[0]["speed_mts"] if modules else 0
    total_installed_gb = sum(m["capacity_gb"] for m in modules) if modules else total_gb

    channel_config = _infer_channel_config(modules)

    return {
        "total_gb": total_gb,
        "total_installed_gb": total_installed_gb,
        "available_gb": available_gb,
        "used_pct": used_pct,
        "memory_type": primary_type,
        "speed_mts": primary_speed,
        "channel_config": channel_config,
        "modules": modules,
        "array": array_info,
        "spd_timings": {
            "available": False,
            "reason": "SPD access requires SMBus driver with admin elevation. Not available in standard mode.",
        },
        "data_sources": ["WMI:Win32_PhysicalMemory", "WMI:Win32_PhysicalMemoryArray", "psutil.virtual_memory"],
    }
