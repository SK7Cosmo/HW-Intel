# Architecture & Implementation Decisions

## ADR-001: Python + FastAPI over Node.js
**Decision:** Python 3.12 + FastAPI + Uvicorn  
**Rationale:** All required packages (psutil, wmi, pywin32, fastapi, uvicorn) were pre-installed. Node npm was blocked by execution policy in this environment.

## ADR-002: WMI Lazy Initialization
**Decision:** Create a new `wmi.WMI()` connection inside each provider function, not at module import time.  
**Rationale:** Module-level WMI init silently fails when imported by uvicorn worker processes (different COM apartment). Lazy init creates a fresh COM connection each call — matches the pattern that works in direct Python scripts.

## ADR-003: int() casts on all WMI numeric fields
**Decision:** Cast `m.Capacity`, `m.Speed`, `m.SMBIOSMemoryType`, `d.Size`, `n.Speed` to `int()` before arithmetic.  
**Rationale:** The Python `wmi` library version on this system returns SMBIOS numeric fields as strings. Direct arithmetic raises `TypeError`. This is a known library behaviour difference between wmi versions.

## ADR-004: Static hardware cached 1h, live data 5s
**Decision:** FastAPI in-memory dict cache with per-endpoint TTLs.  
**Rationale:** CPU name, topology, memory modules etc. never change at runtime. Refreshing on every call wastes WMI round-trips (~1-2s each). Live fields (clock, usage %) use short TTL.

## ADR-005: SPD timings explicitly marked unavailable
**Decision:** Return `{"available": False, "reason": "..."}` for SPD. UI shows explanatory notice.  
**Rationale:** SPD requires SMBus driver + admin elevation. Fabricating timings would violate the no-fabrication rule.

## ADR-006: Microarchitecture inferred from CPUID Family/Model table
**Decision:** Map (Family=6, Model=186) → Raptor Lake-H from a compiled lookup table in cpu_provider.py.  
**Rationale:** WMI does not expose microarchitecture names. Family+Model is the standard CPUID-based identification used by CPU-Z and Intel ARK.

## ADR-007: Dual-channel detection via DeviceLocator, not BankLabel
**Decision:** Parse `Controller0-ChannelA` / `Controller1-ChannelA` from the DeviceLocator field.  
**Rationale:** Both LPDDR5 modules report `BANK 0` in BankLabel (soldered LPDDR5 convention). DeviceLocator accurately shows separate memory controller assignment = dual-channel confirmed.

## ADR-008: Vanilla HTML/CSS/JS frontend served via FastAPI StaticFiles
**Decision:** No frontend build chain.  
**Rationale:** npm was unavailable in this environment. This approach starts immediately after server launch with zero dependencies beyond the Python packages.

## ADR-009: WMI MaxClockSpeed note in UI
**Decision:** Show WMI MaxClockSpeed as "Base/Rated" not "Max Turbo".  
**Rationale:** WMI reports 2100 MHz for i5-13420H which is the nominal/rated speed; actual Intel-spec turbo is 4.6 GHz. The registry `~MHz` live reading is more accurate for current frequency.
