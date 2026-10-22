# Test Results — 2026-10-21

## Provider Smoke Tests (`validate_providers.py`)

| Provider | Result | Key Values |
|---|---|---|
| CPU | ✅ PASS | i5-13420H, Raptor Lake-H, 8C/12T, 33 features |
| Memory | ✅ PASS | 16 GB LPDDR5, 5600 MT/s, 2 modules, Dual-Channel |
| Mainboard | ✅ PASS | Lenovo LNVNB161216, BIOS QDCN27WW 2025-07-11 |
| GPU | ✅ PASS | Intel UHD Graphics, driver 32.0.101.7076 |
| System | ✅ PASS | Win11 Build 26200, 1 disk, 2 adapters, battery |

---

## pytest Suite — 47/47 Passed

```
platform win32 -- Python 3.12.7, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\KAILASH S\.gemini\antigravity-ide\scratch\hwdash

TestCPUProvider         (12 tests) — ALL PASSED
TestMemoryProvider      (8 tests)  — ALL PASSED
TestMainboardProvider   (5 tests)  — ALL PASSED
TestGPUProvider         (4 tests)  — ALL PASSED
TestSystemProvider      (8 tests)  — ALL PASSED
TestAPI (integration)   (10 tests) — ALL PASSED

===================== 47 passed, 1 warning in 54.66s ======================
```

**Warning:** `PytestUnknownMarkWarning` for `@pytest.mark.integration` — harmless.

---

## Bugs Found & Fixed During Testing

| # | Bug | Root Cause | Fix Applied |
|---|---|---|---|
| 1 | Memory: 0 modules | `m.Capacity` returned as `str` by wmi lib | `int(m.Capacity or 0)` |
| 2 | Memory: speed=0, type=Unknown | Same str issue on Speed/SMBIOSMemoryType | `int()` casts |
| 3 | System: 0 disks | `d.Size` str | `int(d.Size or 0)` |
| 4 | System: 0 adapters | `n.Speed` str | `int(n.Speed)` |
| 5 | All providers: silent failure in uvicorn | Module-level `wmi.WMI()` fails in worker thread | Lazy `_get_wmi()` per call |
| 6 | start.bat: path not found | `%~dp0\backend` = `scripts\backend` | Fixed to `%~dp0\..\backend` |
| 7 | Channel: "0-channel" shown | BankLabel="BANK 0" for both LPDDR5 modules | Use DeviceLocator parse |

---

## API Endpoint Validation

| Endpoint | HTTP | Result | Notes |
|---|---|---|---|
| `GET /api/health` | 200 | ✅ | `status: ok` |
| `GET /api/overview` | 200 | ✅ | All sections populated |
| `GET /api/cpu` | 200 | ✅ | Full CPU data |
| `GET /api/cpu/live` | 200 | ✅ | Per-core usage + frequency |
| `GET /api/memory` | 200 | ✅ | 2 LPDDR5 modules, 5600 MT/s |
| `GET /api/mainboard` | 200 | ✅ | Lenovo + QDCN27WW BIOS |
| `GET /api/gpu` | 200 | ✅ | Intel UHD Graphics |
| `GET /api/system` | 200 | ✅ | OS, disk, network, battery |
| `GET /api/export/json` | 200 | ✅ | Full snapshot download |
| `GET /api/export/csv` | 200 | ✅ | Key fields CSV download |

---

## No-Fabrication Verification

- `GET /api/memory` → `spd_timings.available == False` ✅
- No temperature readings fabricated ✅
- No per-core voltage fabricated ✅
- WMI MaxClockSpeed shown with caveat label ✅

---

## Outstanding Issues / Known Limitations

| Issue | Severity | Workaround |
|---|---|---|
| WMI MaxClockSpeed = 2100 MHz (not actual 4.6 GHz turbo) | Low | Live clock from Registry `~MHz` is accurate |
| GPU VRAM = ~2 GB (shared system memory estimate) | Low | Noted in UI with label |
| SPD timings unavailable | Medium | Explanatory notice in UI |
| CPU-Z shared memory inaccessible (process not running) | Info | All data from WMI/Registry |
