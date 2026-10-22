# Data Access Strategy — Hardware Intelligence Dashboard

## Target Machine
- CPU: Intel Core i5-13420H (13th Gen Raptor Lake-H), 8 cores / 12 threads
- Motherboard: Lenovo LNVNB161216
- BIOS: Lenovo QDCN27WW (2025-07-11), SMBIOS 3.4
- Memory: 2x 8GB Kingston LPDDR5 @ 5600 MT/s (SMBIOSMemoryType=34)
- GPU: Intel UHD Graphics
- OS: Windows 11 Home, Build 26200, 64-bit

## Recommended Stack
- Backend: Python 3.12 + FastAPI + Uvicorn (all installed)
- Hardware data: WMI + pywin32 + psutil + winreg (all installed)
- Frontend: HTML5 + Vanilla CSS + JS (served via FastAPI StaticFiles)

## Data Sources
| Section | Source |
|---|---|
| CPU name/arch | Registry ProcessorNameString + WMI Win32_Processor |
| Cores/Threads | WMI NumberOfCores/NumberOfLogicalProcessors |
| Cache | WMI Win32_CacheMemory |
| Clock | Registry ~MHz + psutil cpu_freq() |
| Motherboard | WMI Win32_BaseBoard |
| BIOS | WMI Win32_BIOS |
| Memory | WMI Win32_PhysicalMemory + SMBIOS decode |
| GPU | WMI Win32_VideoController |
| OS | WMI Win32_OperatingSystem |
| Storage | WMI Win32_DiskDrive + psutil |
| Battery | WMI Win32_Battery + psutil |

## Limitations
- SPD timings: Not available (requires SMBus driver/admin)
- Temperatures: Not available without kernel driver
- CPUID Pro SDK: Commercial — not used
- CPU-Z CLI export: Blocked by system policy
