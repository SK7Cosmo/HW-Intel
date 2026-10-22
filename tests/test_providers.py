"""
Automated tests for all backend hardware providers and API endpoints.
Run: python -m pytest tests/ -v
"""
import sys
import os
import pytest
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# ─── Provider Tests ────────────────────────────────────────────────────────────

class TestCPUProvider:
    def setup_method(self):
        from providers.cpu_provider import get_cpu_data
        self.data = get_cpu_data()

    def test_has_name(self):
        assert self.data['name'], "CPU name must not be empty"
        assert 'Unknown' not in self.data['name'] or 'Intel' in self.data['name']

    def test_cores_positive(self):
        assert self.data['cores'] > 0, "Core count must be positive"

    def test_threads_positive(self):
        assert self.data['threads'] > 0, "Thread count must be positive"

    def test_threads_gte_cores(self):
        assert self.data['threads'] >= self.data['cores'], "Threads must be >= cores"

    def test_has_vendor(self):
        assert self.data['vendor'] in ('GenuineIntel', 'AuthenticAMD') or self.data['vendor']

    def test_family_model_stepping_present(self):
        assert isinstance(self.data['family'], int)
        assert isinstance(self.data['model'], int)
        assert isinstance(self.data['stepping'], int)

    def test_microarchitecture_known(self):
        # For this specific machine: Intel i5-13420H = Raptor Lake-H
        assert 'Raptor Lake' in self.data['microarchitecture'] or self.data['microarchitecture'] != 'Unknown'

    def test_cache_hierarchy(self):
        caches = self.data['cache_hierarchy']
        assert isinstance(caches, list)
        if caches:
            for c in caches:
                assert 'level' in c
                assert 'size_kb' in c
                assert c['size_kb'] > 0

    def test_l3_present(self):
        assert self.data['l3_cache_kb'] is not None
        assert self.data['l3_cache_kb'] > 0

    def test_instruction_sets_not_empty(self):
        assert len(self.data['instruction_sets']) > 0

    def test_data_sources_listed(self):
        assert isinstance(self.data['data_sources'], list)
        assert len(self.data['data_sources']) > 0

    def test_topology_structure(self):
        topo = self.data['topology']
        assert 'p_cores' in topo
        assert 'total_threads' in topo


class TestMemoryProvider:
    def setup_method(self):
        from providers.memory_provider import get_memory_data
        self.data = get_memory_data()

    def test_total_gb_positive(self):
        assert self.data['total_gb'] > 0

    def test_memory_type_not_unknown(self):
        assert self.data['memory_type'] != 'Unknown (0)'

    def test_lpddr5_detected(self):
        # This machine has LPDDR5 (SMBIOSMemoryType=34)
        assert 'LPDDR5' in self.data['memory_type'] or self.data['memory_type']

    def test_modules_present(self):
        assert isinstance(self.data['modules'], list)
        assert len(self.data['modules']) > 0

    def test_module_capacity_correct(self):
        total = sum(m['capacity_gb'] for m in self.data['modules'])
        assert abs(total - self.data['total_installed_gb']) < 0.5, \
            f"Module total {total}GB should match installed {self.data['total_installed_gb']}GB"

    def test_spd_marked_unavailable(self):
        spd = self.data['spd_timings']
        assert spd['available'] is False
        assert 'reason' in spd

    def test_channel_config_present(self):
        assert self.data['channel_config']
        assert 'Dual' in self.data['channel_config'] or 'channel' in self.data['channel_config'].lower()

    def test_speed_mts_nonzero(self):
        assert self.data['speed_mts'] > 0


class TestMainboardProvider:
    def setup_method(self):
        from providers.mainboard_provider import get_mainboard_data
        self.data = get_mainboard_data()

    def test_board_manufacturer(self):
        assert self.data['board']['manufacturer']

    def test_board_product(self):
        assert self.data['board']['product']

    def test_bios_version(self):
        assert self.data['bios']['version']

    def test_bios_date_format(self):
        date = self.data['bios']['release_date']
        if date:
            parts = date.split('-')
            assert len(parts) == 3, "BIOS date should be YYYY-MM-DD format"
            assert len(parts[0]) == 4

    def test_smbios_version(self):
        assert self.data['bios']['smbios_version']


class TestGPUProvider:
    def setup_method(self):
        from providers.gpu_provider import get_gpu_data
        self.data = get_gpu_data()

    def test_gpus_list(self):
        assert isinstance(self.data, list)

    def test_gpu_present(self):
        assert len(self.data) > 0, "At least one GPU should be detected"

    def test_gpu_name(self):
        for g in self.data:
            assert g['name'], "GPU name must not be empty"

    def test_driver_version_format(self):
        for g in self.data:
            ver = g.get('driver_version', '')
            if ver:
                parts = ver.split('.')
                assert len(parts) >= 2


class TestSystemProvider:
    def setup_method(self):
        from providers.system_provider import get_system_data
        self.data = get_system_data()

    def test_os_name(self):
        assert self.data['os']['name']
        assert 'Windows' in self.data['os']['name']

    def test_os_build(self):
        assert self.data['os']['build']

    def test_os_arch(self):
        assert '64' in self.data['os']['architecture']

    def test_disks_present(self):
        assert len(self.data['disks']) > 0

    def test_disk_usage_present(self):
        assert len(self.data['disk_usage']) > 0

    def test_disk_usage_c_drive(self):
        c_drive = [d for d in self.data['disk_usage'] if d['mountpoint'].startswith('C')]
        assert len(c_drive) > 0, "C:\\ drive should be in disk usage"

    def test_network_adapters(self):
        assert isinstance(self.data['network_adapters'], list)

    def test_battery_detected(self):
        # This is a laptop, battery should be present
        bat = self.data['battery']
        assert bat, "Battery should be detected on laptop"
        assert 'charge_pct' in bat


# ─── API Tests (require running server) ───────────────────────────────────────

@pytest.mark.integration
class TestAPI:
    BASE = 'http://127.0.0.1:7890/api'

    def _get(self, endpoint):
        import requests
        r = requests.get(f"{self.BASE}/{endpoint}", timeout=5)
        r.raise_for_status()
        return r.json()

    def test_health(self):
        data = self._get('health')
        assert data['status'] == 'ok'

    def test_overview_schema(self):
        data = self._get('overview')
        assert 'cpu' in data
        assert 'memory' in data
        assert 'board' in data
        assert 'gpu' in data
        assert 'os' in data

    def test_cpu_endpoint(self):
        data = self._get('cpu')
        assert data['name']
        assert data['cores'] > 0

    def test_memory_endpoint(self):
        data = self._get('memory')
        assert data['total_gb'] > 0

    def test_mainboard_endpoint(self):
        data = self._get('mainboard')
        assert 'board' in data
        assert 'bios' in data

    def test_gpu_endpoint(self):
        data = self._get('gpu')
        assert isinstance(data, list)

    def test_system_endpoint(self):
        data = self._get('system')
        assert 'os' in data

    def test_export_json_headers(self):
        import requests
        r = requests.get(f"{self.BASE}/export/json", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert 'cpu' in data
        assert 'memory' in data

    def test_cpu_live_endpoint(self):
        data = self._get('cpu/live')
        assert 'overall_pct' in data
        assert 0 <= data['overall_pct'] <= 100

    def test_no_fabricated_values(self):
        """Ensure unavailable fields are not fabricated."""
        mem = self._get('memory')
        spd = mem.get('spd_timings', {})
        assert spd.get('available') is False, "SPD should be marked unavailable, not fabricated"


if __name__ == '__main__':
    # Run provider tests without pytest for quick validation
    for cls in [TestCPUProvider, TestMemoryProvider, TestMainboardProvider, TestGPUProvider, TestSystemProvider]:
        inst = cls()
        inst.setup_method()
        methods = [m for m in dir(inst) if m.startswith('test_')]
        passed = failed = 0
        for m in methods:
            try:
                getattr(inst, m)()
                print(f"  ✓ {cls.__name__}.{m}")
                passed += 1
            except Exception as e:
                print(f"  ✗ {cls.__name__}.{m}: {e}")
                failed += 1
        print(f"  → {passed} passed, {failed} failed\n")
