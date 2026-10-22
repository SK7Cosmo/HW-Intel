"""
Motherboard / BIOS Provider
Gathers mainboard and BIOS information from WMI DMI data.
"""
from __future__ import annotations

def _get_wmi():
    try:
        import wmi
        return wmi.WMI()
    except Exception:
        return None


def get_mainboard_data() -> dict:
    """Return normalized motherboard and BIOS data."""
    board = {}
    bios = {}
    w = _get_wmi()

    if w:
        try:
            b = w.Win32_BaseBoard()[0]
            board = {
                "manufacturer": (b.Manufacturer or "").strip(),
                "product": (b.Product or "").strip(),
                "version": (b.Version or "").strip(),
                "serial_number": (b.SerialNumber or "").strip(),
                "tag": (b.Tag or "").strip(),
            }
        except Exception:
            pass

        try:
            bi = w.Win32_BIOS()[0]
            release_date = None
            if bi.ReleaseDate:
                # WMI BIOS date format: YYYYMMDD000000.000000+000
                raw = str(bi.ReleaseDate)[:8]
                if len(raw) == 8:
                    release_date = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
            bios = {
                "vendor": (bi.Manufacturer or "").strip(),
                "version": (bi.SMBIOSBIOSVersion or bi.Version or "").strip(),
                "release_date": release_date,
                "smbios_major": bi.SMBIOSMajorVersion,
                "smbios_minor": bi.SMBIOSMinorVersion,
                "smbios_version": f"{bi.SMBIOSMajorVersion}.{bi.SMBIOSMinorVersion}",
                "name": (bi.Name or "").strip(),
            }
        except Exception:
            pass

        # Chipset (best effort from system info)
        try:
            cs = w.Win32_ComputerSystem()[0]
            board["system_manufacturer"] = (cs.Manufacturer or "").strip()
            board["system_model"] = (cs.Model or "").strip()
        except Exception:
            pass

    return {
        "board": board,
        "bios": bios,
        "chipset": {
            "name": "Intel SoC (Raptor Lake-H integrated)",
            "note": "Chipset/PCH is integrated into the SoC for 13th Gen mobile. PCI enumeration requires elevated privileges.",
            "available": False,
        },
        "data_sources": ["WMI:Win32_BaseBoard", "WMI:Win32_BIOS", "WMI:Win32_ComputerSystem"],
    }
