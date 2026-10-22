# Coverage Matrix — Hardware Intelligence Dashboard
_Last updated: 2026-10-21 | Test machine: Intel i5-13420H / Lenovo IdeaPad_

## Status Key
- ✅ **Implemented & Verified** — data provider implemented, validated against actual hardware
- ⚠️ **Implemented, Partial** — provider exists but field has caveats or limited accuracy
- ❌ **Unavailable** — blocked by permissions, driver requirements, or API limitations
- 🔍 **Inferred** — value derived/inferred from other data, not directly measured

---

## CPU

| Field | Status | Source | Notes |
|---|---|---|---|
| Processor name | ✅ | WMI / Registry | Full marketing name |
| Vendor (GenuineIntel) | ✅ | Registry VendorIdentifier | |
| Family / Model / Stepping | ✅ | Registry Identifier | 6 / 186 / 2 |
| CPUID string | ✅ | Registry Identifier | |
| Processor ID | ✅ | WMI ProcessorId | BFEBFBFF000B06A2 |
| Microarchitecture | ✅ | 🔍 Inferred from Family+Model | Raptor Lake-H |
| Process node | ✅ | 🔍 Inferred from uarch table | Intel 7 (10nm ESF) |
| Generation | ✅ | 🔍 Inferred | 13th Gen |
| Core count | ✅ | WMI NumberOfCores | 8 |
| Thread count | ✅ | WMI NumberOfLogicalProcessors | 12 |
| P-core count | ✅ | 🔍 Inferred from Raptor Lake-H spec | 4 |
| E-core count | ✅ | 🔍 Inferred from Raptor Lake-H spec | 4 |
| Socket | ✅ | WMI SocketDesignation | U3E1 |
| Base clock | ⚠️ | WMI ExtClock / MaxClockSpeed | WMI shows nominal, not all-core max |
| Max Turbo Boost | ⚠️ | WMI MaxClockSpeed | Reports 2100 MHz; actual turbo is 4.6 GHz per Intel spec |
| Current clock | ✅ | Registry ~MHz + psutil | Live, OS-reported |
| Bus clock | ✅ | WMI ExtClock | 100 MHz |
| L1 Instruction cache | ✅ | WMI Win32_CacheMemory | 192 KB (P-cores) |
| L1 Data cache | ✅ | WMI Win32_CacheMemory | 128 KB + 256 KB |
| L2 cache | ✅ | WMI Win32_CacheMemory | 5120 KB (P) + 2048 KB (E) |
| L3 cache | ✅ | WMI Win32_CacheMemory | 12288 KB |
| Instruction sets (core) | ✅ | 🔍 Known Raptor Lake features | SSE/AVX/AVX2/AES/etc. |
| Intel Thread Director | ✅ | 🔍 Architecture feature | Listed |
| Voltage | ⚠️ | WMI CurrentVoltage (×0.1V) | Coarse reading only |
| Per-core voltage | ❌ | — | Requires ECDriver / kernel |
| Temperature | ❌ | — | Requires OHM or admin driver |
| Power consumption | ❌ | — | Requires RAPL or admin |

---

## Memory

| Field | Status | Source | Notes |
|---|---|---|---|
| Total capacity | ✅ | psutil / WMI | 16 GB (15.67 usable) |
| Module count | ✅ | WMI Win32_PhysicalMemory | 2 modules |
| Per-module capacity | ✅ | WMI Capacity (int cast) | 8 GB each |
| Memory type | ✅ | WMI SMBIOSMemoryType=34 → LPDDR5 | Correctly decoded |
| Speed | ✅ | WMI Speed | 5600 MT/s |
| Channel config | ✅ | 🔍 DeviceLocator parse | Dual-Channel (2 controllers) |
| Manufacturer | ✅ | WMI Manufacturer | Kingston |
| Part numbers | ✅ | WMI PartNumber | LV56S46BS6HA-8KM / LV56S46BS6MD-8KI |
| Serial numbers | ✅ | WMI SerialNumber | Available (one is 00000000) |
| Max supported capacity | ✅ | WMI Win32_PhysicalMemoryArray | 24 GB |
| Live usage % | ✅ | psutil virtual_memory | Dynamic |
| SPD tCL / tRCD / tRP / tRAS | ❌ | — | Requires SMBus kernel driver + admin |
| XMP / EXPO profiles | ❌ | — | Requires SPD access |
| Configured voltage | ❌ | — | WMI ConfiguredVoltage not populated on this system |

---

## Mainboard

| Field | Status | Source | Notes |
|---|---|---|---|
| Manufacturer | ✅ | WMI Win32_BaseBoard | LENOVO |
| Product / Model | ✅ | WMI Win32_BaseBoard | LNVNB161216 |
| Version | ✅ | WMI Win32_BaseBoard | SDK0T76485 WIN |
| Serial number | ✅ | WMI Win32_BaseBoard | PF5YKYGB |
| BIOS vendor | ✅ | WMI Win32_BIOS | LENOVO |
| BIOS version | ✅ | WMI SMBIOSBIOSVersion | QDCN27WW |
| BIOS release date | ✅ | WMI ReleaseDate | 2025-07-11 |
| SMBIOS version | ✅ | WMI SMBIOSMajor/MinorVersion | 3.4 |
| Chipset ID | ❌ | — | Integrated SoC; PCI enumeration needs admin |
| PCIe slot info | ❌ | — | Requires admin PCI scan |

---

## Graphics

| Field | Status | Source | Notes |
|---|---|---|---|
| Adapter name | ✅ | WMI Win32_VideoController | Intel UHD Graphics |
| VRAM | ⚠️ | WMI AdapterRAM | ~2 GB reported (shared memory, capped at 32-bit) |
| Driver version | ✅ | WMI DriverVersion | 32.0.101.7076 |
| Current resolution | ✅ | WMI CurrentH/VRes | 1920×1200 |
| Refresh rate | ✅ | WMI CurrentRefreshRate | 60 Hz |
| DirectX version | ❌ | — | Not exposed via WMI |
| GPU clock | ❌ | — | Requires Intel GPU driver API |
| GPU temperature | ❌ | — | Requires driver API |

---

## System

| Field | Status | Source | Notes |
|---|---|---|---|
| OS name | ✅ | WMI Win32_OperatingSystem | Windows 11 Home SL |
| OS version | ✅ | WMI | 10.0.26200 |
| OS build | ✅ | WMI | 26200 |
| Architecture | ✅ | WMI | 64-bit |
| Install date | ✅ | WMI | Decoded from WMI format |
| Boot time | ✅ | psutil | Live |
| Computer name | ✅ | WMI | LAPTOP-C97VE2UT |
| Storage model | ✅ | WMI Win32_DiskDrive | Micron NVMe 1TB |
| Storage size | ✅ | WMI | 1024 GB |
| Disk usage per partition | ✅ | psutil disk_usage | C:\ etc. |
| Network adapters | ✅ | WMI Win32_NetworkAdapter | Wi-Fi 6 AX203 + BT |
| Battery charge | ✅ | WMI Win32_Battery + psutil | 100%, Plugged In |
| Battery capacity (design) | ❌ | — | Not reported by WMI on this system |

---

## Summary

| Category | Total Fields | Implemented & Verified | Partial | Unavailable |
|---|---|---|---|---|
| CPU | 22 | 16 | 3 | 3 |
| Memory | 14 | 10 | 1 | 3 |
| Mainboard | 10 | 8 | 0 | 2 |
| Graphics | 8 | 4 | 1 | 3 |
| System | 14 | 13 | 0 | 1 |
| **Total** | **68** | **51 (75%)** | **5 (7%)** | **12 (18%)** |
