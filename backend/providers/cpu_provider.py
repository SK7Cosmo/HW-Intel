"""
CPU Hardware Provider
Gathers CPU information from WMI, Windows Registry, and psutil.
"""
from __future__ import annotations
import winreg
import platform
import re
from typing import Optional
import psutil

# Optional WMI import
try:
    import wmi
    _WMI = wmi.WMI()
    _WMI_AVAILABLE = True
except Exception:
    _WMI = None
    _WMI_AVAILABLE = False


# ── Intel microarchitecture lookup by (family, model) ────────────────────────
_INTEL_UARCH = {
    (6, 186): {"name": "Raptor Lake-H", "process": "Intel 7 (10nm ESF)", "generation": "13th Gen"},
    (6, 183): {"name": "Raptor Lake-S", "process": "Intel 7 (10nm ESF)", "generation": "13th Gen"},
    (6, 190): {"name": "Raptor Lake", "process": "Intel 7 (10nm ESF)", "generation": "13th Gen"},
    (6, 154): {"name": "Alder Lake-P", "process": "Intel 7 (10nm ESF)", "generation": "12th Gen"},
    (6, 151): {"name": "Alder Lake-S", "process": "Intel 7 (10nm ESF)", "generation": "12th Gen"},
    (6, 167): {"name": "Rocket Lake-S", "process": "14nm+++", "generation": "11th Gen"},
    (6, 165): {"name": "Comet Lake-H", "process": "14nm+++", "generation": "10th Gen"},
    (6, 142): {"name": "Kaby Lake / Coffee Lake", "process": "14nm++", "generation": "7th-9th Gen"},
    (6, 158): {"name": "Coffee Lake", "process": "14nm++", "generation": "8th-9th Gen"},
}

# Raptor Lake-H i5-13420H known topology
_RAPTOR_LAKE_H_TOPOLOGY = {
    "p_cores": 4,
    "e_cores": 4,
    "p_threads": 8,  # P-cores are HT
    "e_threads": 4,  # E-cores are single-threaded
    "total_threads": 12,
}

# Known instruction-set support for Raptor Lake
_RAPTOR_LAKE_FEATURES = [
    "MMX", "SSE", "SSE2", "SSE3", "SSSE3", "SSE4.1", "SSE4.2",
    "AVX", "AVX2", "AES-NI", "PCLMULQDQ", "RDRAND", "RDSEED",
    "FMA3", "F16C", "BMI1", "BMI2", "POPCNT", "LZCNT", "MOVBE",
    "SHA", "VAES", "VPCLMULQDQ", "GFNI",
    "Intel VT-x (VMX)", "Intel VT-d (IOMMU)", "Intel TXT",
    "Intel TSX-NI", "Intel SGX",
    "Intel Speed Shift (HWP)", "Intel Turbo Boost 2.0",
    "Intel Hyper-Threading (P-cores only)",
    "Intel Thread Director",
]


def _read_registry_cpu(core: int = 0) -> dict:
    """Read CPU info from Windows registry."""
    result = {}
    try:
        key_path = rf"HARDWARE\DESCRIPTION\System\CentralProcessor\{core}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            for name in ["ProcessorNameString", "VendorIdentifier", "Identifier", "~MHz", "FeatureSet"]:
                try:
                    val, _ = winreg.QueryValueEx(key, name)
                    result[name] = val
                except FileNotFoundError:
                    pass
    except Exception:
        pass
    return result


def _decode_family_model_stepping(identifier: str) -> tuple[int, int, int]:
    """Parse 'Intel64 Family 6 Model 186 Stepping 2' → (6, 186, 2)."""
    m = re.search(r"Family\s+(\d+)\s+Model\s+(\d+)\s+Stepping\s+(\d+)", identifier, re.I)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return (0, 0, 0)


def _decode_feature_set(feature_set: int) -> list[str]:
    """Decode Windows FeatureSet bitmask to feature names."""
    bits = {
        0:  "FPU",  1: "VME",  2: "DE",   3: "PSE",
        4:  "TSC",  5: "MSR",  6: "PAE",  7: "MCE",
        8:  "CX8",  9: "APIC", 11: "SEP", 12: "MTRR",
        13: "PGE",  14: "MCA", 15: "CMOV",16: "PAT",
        17: "PSE36",18: "PSN", 19: "CLFSH",20: "DS",
        21: "ACPI", 22: "MMX", 23: "FXSR", 24: "SSE",
        25: "SSE2", 26: "SS",  27: "HTT",  28: "TM",
        29: "IA64", 30: "PBE",
    }
    return [bits[i] for i in range(31) if (feature_set >> i) & 1 and i in bits]


def _get_cache_info() -> list[dict]:
    """Get cache hierarchy from WMI Win32_CacheMemory."""
    caches = []
    if not _WMI_AVAILABLE:
        return caches
    try:
        seen = set()
        for c in _WMI.Win32_CacheMemory():
            level_map = {3: 1, 4: 2, 5: 3}
            type_map = {3: "Instruction", 4: "Data", 5: "Unified"}
            level = level_map.get(c.Level, c.Level)
            ctype = type_map.get(c.CacheType, "Unknown")
            assoc_map = {1: "Direct mapped", 2: "2-way", 4: "4-way", 6: "8-way", 7: "16-way", 8: "12-way", 9: "Full"}
            assoc = assoc_map.get(c.Associativity, f"{c.Associativity}-way")
            key = (level, ctype, c.InstalledSize)
            if key not in seen:
                seen.add(key)
                caches.append({
                    "level": level,
                    "type": ctype,
                    "size_kb": c.InstalledSize,
                    "associativity": assoc,
                })
    except Exception:
        pass
    return sorted(caches, key=lambda x: (x["level"], x["type"]))


def get_cpu_data() -> dict:
    """Return a normalized CPU data dictionary."""
    reg = _read_registry_cpu(0)
    identifier = reg.get("Identifier", "")
    fam, model, stepping = _decode_family_model_stepping(identifier)

    uarch_info = _INTEL_UARCH.get((fam, model), {
        "name": "Unknown",
        "process": "Unknown",
        "generation": "Unknown",
    })

    # WMI fields
    wmi_cpu = {}
    if _WMI_AVAILABLE:
        try:
            p = _WMI.Win32_Processor()[0]
            wmi_cpu = {
                "name": p.Name.strip() if p.Name else None,
                "manufacturer": p.Manufacturer,
                "socket": p.SocketDesignation,
                "cores": p.NumberOfCores,
                "threads": p.NumberOfLogicalProcessors,
                "max_clock_mhz": p.MaxClockSpeed,
                "current_clock_mhz": p.CurrentClockSpeed,
                "ext_clock_mhz": p.ExtClock,  # bus/base clock
                "l2_kb": p.L2CacheSize,
                "l3_kb": p.L3CacheSize,
                "processor_id": p.ProcessorId,
                "characteristics": p.Characteristics,
                "voltage_raw": p.CurrentVoltage,
            }
        except Exception:
            pass

    # Live clock from registry (more current)
    reg_mhz = reg.get("~MHz")
    if isinstance(reg_mhz, int):
        current_clock_mhz = reg_mhz
    else:
        current_clock_mhz = wmi_cpu.get("current_clock_mhz")

    # psutil freq
    psutil_freq = None
    try:
        freq = psutil.cpu_freq(percpu=False)
        if freq:
            psutil_freq = {"current": freq.current, "min": freq.min, "max": freq.max}
    except Exception:
        pass

    # Voltage: Windows reports in 0.1V units
    voltage_v = None
    raw_v = wmi_cpu.get("voltage_raw")
    if raw_v:
        voltage_v = raw_v / 10.0

    # Feature set decode
    feature_set = reg.get("FeatureSet", 0)
    registry_features = _decode_feature_set(feature_set) if isinstance(feature_set, int) else []

    # Use known Raptor Lake features if architecture matches
    if (fam, model) in _INTEL_UARCH:
        known_features = _RAPTOR_LAKE_FEATURES
        topology = _RAPTOR_LAKE_H_TOPOLOGY
    else:
        known_features = registry_features
        topology = {
            "p_cores": wmi_cpu.get("cores", 0),
            "e_cores": 0,
            "p_threads": wmi_cpu.get("threads", 0),
            "e_threads": 0,
            "total_threads": wmi_cpu.get("threads", 0),
        }

    caches = _get_cache_info()

    return {
        "name": wmi_cpu.get("name") or reg.get("ProcessorNameString", "Unknown"),
        "vendor": reg.get("VendorIdentifier", wmi_cpu.get("manufacturer", "Unknown")),
        "family": fam,
        "model": model,
        "stepping": stepping,
        "identifier": identifier,
        "microarchitecture": uarch_info["name"],
        "process_node": uarch_info["process"],
        "generation": uarch_info["generation"],
        "socket": wmi_cpu.get("socket", "Unknown"),
        "cores": wmi_cpu.get("cores", 0),
        "threads": wmi_cpu.get("threads", 0),
        "topology": topology,
        "base_clock_mhz": wmi_cpu.get("ext_clock_mhz") or wmi_cpu.get("max_clock_mhz"),
        "max_turbo_mhz": wmi_cpu.get("max_clock_mhz"),
        "current_clock_mhz": current_clock_mhz,
        "psutil_freq": psutil_freq,
        "l2_cache_kb": wmi_cpu.get("l2_kb"),
        "l3_cache_kb": wmi_cpu.get("l3_kb"),
        "cache_hierarchy": caches,
        "processor_id": wmi_cpu.get("processor_id"),
        "voltage_v": voltage_v,
        "instruction_sets": known_features,
        "registry_features": registry_features,
        "data_sources": ["WMI:Win32_Processor", "Registry:CentralProcessor", "psutil.cpu_freq"],
    }
