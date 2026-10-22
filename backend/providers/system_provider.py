"""
System Provider
Gathers OS, storage, network, battery, and overall system information.
"""
from __future__ import annotations
import platform
import os
import psutil
from datetime import datetime

def _get_wmi():
    """Lazy WMI connection."""
    try:
        import wmi
        return wmi.WMI()
    except Exception:
        return None


def _boot_time_str() -> str:
    try:
        bt = psutil.boot_time()
        return datetime.fromtimestamp(bt).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Unknown"


def get_system_data() -> dict:
    """Return OS, storage, network, and battery info."""
    os_info = {}
    disks = []
    network_adapters = []
    battery = {}
    w = _get_wmi()

    if w:
        try:
            o = w.Win32_OperatingSystem()[0]
            install_date = None
            if o.InstallDate:
                raw = str(o.InstallDate)[:8]
                if len(raw) == 8:
                    install_date = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
            os_info = {
                "name": (o.Caption or "").strip(),
                "version": (o.Version or "").strip(),
                "build": (o.BuildNumber or "").strip(),
                "architecture": (o.OSArchitecture or "").strip(),
                "install_date": install_date,
                "system_directory": (o.SystemDirectory or "").strip(),
                "windows_directory": (o.WindowsDirectory or "").strip(),
                "registered_user": (o.RegisteredUser or "").strip(),
                "computer_name": (o.CSName or "").strip(),
                "total_memory_kb": o.TotalVisibleMemorySize,
                "free_memory_kb": o.FreePhysicalMemory,
            }
        except Exception:
            os_info = {
                "name": platform.system(),
                "version": platform.version(),
                "architecture": platform.machine(),
            }

        try:
            for d in w.Win32_DiskDrive():
                raw_size = int(d.Size or 0)
                size_gb = round(raw_size / (1024 ** 3), 1) if raw_size else None
                disks.append({
                    "model": (d.Model or "").strip(),
                    "size_gb": size_gb,
                    "size_bytes": raw_size,
                    "media_type": (d.MediaType or "").strip(),
                    "interface": (d.InterfaceType or "").strip(),
                    "serial_number": (d.SerialNumber or "").strip(),
                    "partitions": d.Partitions,
                    "firmware_revision": (d.FirmwareRevision or "").strip(),
                })
        except Exception:
            pass

        try:
            for n in w.Win32_NetworkAdapter():
                if n.PhysicalAdapter:
                    speed_mbps = round(int(n.Speed) / 1_000_000, 0) if n.Speed else None
                    network_adapters.append({
                        "name": (n.Name or "").strip(),
                        "mac": (n.MACAddress or "").strip(),
                        "speed_mbps": speed_mbps,
                        "adapter_type": (n.AdapterType or "").strip(),
                        "manufacturer": (n.Manufacturer or "").strip(),
                    })
        except Exception:
            pass

        try:
            b = w.Win32_Battery()
            if b:
                b = b[0]
                status_map = {1: "Discharging", 2: "Plugged In", 3: "Fully Charged", 4: "Low", 5: "Critical", 6: "Charging", 7: "Charging+High", 8: "Charging+Low", 9: "Charging+Critical", 10: "Undefined", 11: "Partially Charged"}
                battery = {
                    "name": (b.Name or "").strip(),
                    "charge_pct": b.EstimatedChargeRemaining,
                    "status": status_map.get(b.BatteryStatus, "Unknown"),
                    "status_code": b.BatteryStatus,
                    "design_capacity_mwh": b.DesignCapacity,
                    "full_capacity_mwh": b.FullChargeCapacity,
                }
        except Exception:
            pass

    # psutil disk usage
    disk_usage = []
    try:
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disk_usage.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024 ** 3), 1),
                    "used_gb": round(usage.used / (1024 ** 3), 1),
                    "free_gb": round(usage.free / (1024 ** 3), 1),
                    "used_pct": usage.percent,
                })
            except PermissionError:
                pass
    except Exception:
        pass

    # psutil battery
    psutil_battery = None
    try:
        pb = psutil.sensors_battery()
        if pb:
            psutil_battery = {
                "percent": pb.percent,
                "power_plugged": pb.power_plugged,
                "secsleft": pb.secsleft if pb.secsleft != psutil.POWER_TIME_UNLIMITED else -1,
            }
            if not battery:
                battery = {
                    "charge_pct": pb.percent,
                    "status": "Plugged In" if pb.power_plugged else "Discharging",
                }
    except Exception:
        pass

    return {
        "os": os_info,
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "boot_time": _boot_time_str(),
        "hostname": os_info.get("computer_name") or platform.node(),
        "disks": disks,
        "disk_usage": disk_usage,
        "network_adapters": network_adapters,
        "battery": battery,
        "psutil_battery": psutil_battery,
        "data_sources": [
            "WMI:Win32_OperatingSystem", "WMI:Win32_DiskDrive",
            "WMI:Win32_NetworkAdapter", "WMI:Win32_Battery",
            "psutil.disk_partitions", "psutil.sensors_battery",
        ],
    }
