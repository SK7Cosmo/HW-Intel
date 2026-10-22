import sys
sys.path.insert(0, 'providers')

print('=== Testing CPU Provider ===')
from cpu_provider import get_cpu_data
cpu = get_cpu_data()
print(f"  Name: {cpu['name']}")
print(f"  Microarch: {cpu['microarchitecture']}")
print(f"  Cores/Threads: {cpu['cores']}/{cpu['threads']}")
print(f"  Family/Model/Stepping: {cpu['family']}/{cpu['model']}/{cpu['stepping']}")
print(f"  L2: {cpu['l2_cache_kb']} KB, L3: {cpu['l3_cache_kb']} KB")
print(f"  Cache entries: {len(cpu['cache_hierarchy'])}")
print(f"  Features: {len(cpu['instruction_sets'])} items")
print(f"  P-cores: {cpu['topology']['p_cores']}, E-cores: {cpu['topology']['e_cores']}")

print()
print('=== Testing Memory Provider ===')
from memory_provider import get_memory_data
mem = get_memory_data()
print(f"  Total: {mem['total_gb']} GB")
print(f"  Type: {mem['memory_type']}")
print(f"  Speed: {mem['speed_mts']} MT/s")
print(f"  Modules: {len(mem['modules'])}")
print(f"  Channel: {mem['channel_config']}")
for m in mem['modules']:
    print(f"    Module: {m['capacity_gb']}GB {m['memory_type']} @ {m['speed_mts']} MT/s [{m['manufacturer']}] {m['part_number']}")

print()
print('=== Testing Mainboard Provider ===')
from mainboard_provider import get_mainboard_data
board = get_mainboard_data()
print(f"  Manufacturer: {board['board']['manufacturer']}")
print(f"  Product: {board['board']['product']}")
print(f"  BIOS: {board['bios']['version']} ({board['bios']['release_date']})")
print(f"  SMBIOS: {board['bios']['smbios_version']}")

print()
print('=== Testing GPU Provider ===')
from gpu_provider import get_gpu_data
gpus = get_gpu_data()
for g in gpus:
    print(f"  GPU: {g['name']}")
    print(f"  Driver: {g['driver_version']}")
    print(f"  Resolution: {g['video_mode']}")

print()
print('=== Testing System Provider ===')
from system_provider import get_system_data
sys_data = get_system_data()
print(f"  OS: {sys_data['os']['name']}")
print(f"  Build: {sys_data['os']['build']}")
print(f"  Disks: {len(sys_data['disks'])}")
print(f"  Battery: {sys_data['battery']}")
print(f"  Network: {len(sys_data['network_adapters'])} adapters")

print()
print('=== ALL PROVIDERS VALIDATED ===')
