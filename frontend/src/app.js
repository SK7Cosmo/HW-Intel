/**
 * Hardware Intelligence Dashboard — Application JS
 * Fetches data from the FastAPI backend and renders all sections.
 */

const API = 'http://127.0.0.1:7890/api';
const LIVE_INTERVAL_MS = 5000;

// ── State ──────────────────────────────────────────────────────────────────────
let _data = {};
let _liveTimer = null;
let _searchIndex = [];  // [{section, key, value}]

// ── DOM Helpers ────────────────────────────────────────────────────────────────
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const setText = (id, val) => { const el = $(id); if (el) el.textContent = val ?? '—'; };
const setHtml = (id, html) => { const el = $(id); if (el) el.innerHTML = html; };

// ── Navigation ─────────────────────────────────────────────────────────────────
function navigate(sectionId) {
  $$('.section').forEach(s => s.classList.remove('active'));
  $$('.nav-item').forEach(n => { n.classList.remove('active'); n.setAttribute('aria-selected', 'false'); });

  const sec = $(`#section-${sectionId}`);
  if (sec) sec.classList.add('active');

  const nav = $(`.nav-item[data-section="${sectionId}"]`);
  if (nav) { nav.classList.add('active'); nav.setAttribute('aria-selected', 'true'); }

  const titles = { overview: 'System Overview', cpu: 'CPU Details', memory: 'Memory', mainboard: 'Mainboard', gpu: 'Graphics', system: 'System' };
  setText('#page-title', titles[sectionId] || sectionId);

  // Hide search results when navigating
  $('#search-results').style.display = 'none';
}

$$('.nav-item').forEach(item => {
  item.addEventListener('click', (e) => {
    e.preventDefault();
    navigate(item.dataset.section);
  });
});

// Mobile menu
$('#menu-toggle')?.addEventListener('click', () => $('#sidebar').classList.toggle('open'));

// ── Theme ──────────────────────────────────────────────────────────────────────
let _isDark = true;
$('#theme-toggle')?.addEventListener('click', () => {
  _isDark = !_isDark;
  document.body.classList.toggle('dark', _isDark);
  document.body.classList.toggle('light', !_isDark);
  $('#icon-moon').style.display = _isDark ? '' : 'none';
  $('#icon-sun').style.display = _isDark ? 'none' : '';
});

// ── Gauge helper ───────────────────────────────────────────────────────────────
function updateGauge(arcId, valId, pct) {
  const circumference = 2 * Math.PI * 50;  // r=50
  const offset = circumference * (1 - pct / 100);
  const arc = $(arcId);
  if (arc) arc.style.strokeDashoffset = offset;
  setText(valId, `${Math.round(pct)}%`);
}

// ── Status ─────────────────────────────────────────────────────────────────────
function setStatus(online) {
  const dot = $('#status-dot');
  if (!dot) return;
  dot.classList.toggle('online', online);
  dot.classList.toggle('offline', !online);
}

// ── Loading ────────────────────────────────────────────────────────────────────
function hideLoading() {
  const overlay = $('#loading-overlay');
  if (overlay) { overlay.classList.add('hidden'); setTimeout(() => overlay.style.display = 'none', 400); }
}
function showError(msg) {
  const banner = $('#error-banner');
  if (banner) { banner.style.display = 'flex'; setText('#error-text', msg); }
}

// ── Fetch ──────────────────────────────────────────────────────────────────────
async function fetchData(endpoint) {
  const res = await fetch(`${API}/${endpoint}`);
  if (!res.ok) throw new Error(`HTTP ${res.status} on /api/${endpoint}`);
  return res.json();
}

// ── Table builder ──────────────────────────────────────────────────────────────
function buildTable(tableId, rows) {
  const tbody = $(`#${tableId} tbody`);
  if (!tbody) return;
  tbody.innerHTML = '';
  rows.forEach(([label, val, mono]) => {
    const tr = document.createElement('tr');
    const display = val ?? '—';
    tr.innerHTML = `<td>${label}</td><td class="${mono ? 'mono' : ''}" title="${display}">${display}</td>`;
    tbody.appendChild(tr);
    // Add to search index
    _searchIndex.push({ key: label, value: String(display), el: tr });
  });
}

// ── Render Overview ─────────────────────────────────────────────────────────────
function renderOverview(d) {
  const cpu = d.cpu || {};
  const mem = d.memory || {};
  const board = d.board || {};
  const gpus = d.gpu || [];
  const os = d.os || {};
  const bat = d.battery || {};

  // CPU hero
  setText('#ov-gen', cpu.generation || '');
  setText('#ov-cpu-name', cpu.name);
  setText('#ov-cpu-sub', [cpu.microarchitecture, cpu.process_node || d.cpu_microarch].filter(Boolean).join(' · '));
  setText('#ov-cores',  cpu.cores);
  setText('#ov-threads', cpu.threads);
  setText('#ov-base',   cpu.base_clock_mhz ? `${cpu.base_clock_mhz}` : '—');
  setText('#ov-turbo',  cpu.max_turbo_mhz  ? `${cpu.max_turbo_mhz}` : '—');
  setText('#ov-l3',     cpu.l3_cache_kb ? `${(cpu.l3_cache_kb / 1024).toFixed(0)} MB` : '—');
  updateGauge('#cpu-gauge-arc', '#cpu-gauge-val', cpu.usage_pct || 0);

  // Memory
  setText('#ov-mem-total', mem.total_gb);
  setText('#ov-mem-type', `${mem.memory_type || ''} @ ${mem.speed_mts || '—'} MT/s`);
  const usedPct = mem.used_pct || 0;
  const el = $('#ov-mem-bar');
  if (el) el.style.width = `${usedPct}%`;
  setText('#ov-mem-used-str', `${(mem.total_gb * usedPct / 100).toFixed(1)} GB used`);
  setText('#ov-mem-pct', `${Math.round(usedPct)}%`);
  setText('#ov-mem-speed', mem.speed_mts ? `${mem.speed_mts} MT/s` : '—');
  setText('#ov-mem-ch', mem.channel_config || '—');

  // Board
  setText('#ov-board-mfr',  board.manufacturer);
  setText('#ov-board-model', board.product);
  setText('#ov-bios-ver',   board.bios_version);
  setText('#ov-bios-date',  board.bios_date);

  // GPU
  const g = gpus[0] || {};
  setText('#ov-gpu-name',   g.name);
  setText('#ov-gpu-vram',   g.vram || '—');
  setText('#ov-gpu-driver', g.driver);
  setText('#ov-gpu-mode',   '—');

  // OS
  setText('#ov-os-name',  os.name);
  setText('#ov-os-ver',   os.version);
  setText('#ov-os-build', os.build ? `Build ${os.build}` : '—');
  setText('#ov-os-arch',  os.architecture);
  setText('#ov-os-boot',  d.boot_time || '—');
}

// ── Render CPU ──────────────────────────────────────────────────────────────────
function renderCPU(d) {
  // Identity table
  buildTable('cpu-identity-table', [
    ['Processor',        d.name],
    ['Vendor',           d.vendor],
    ['Generation',       d.generation],
    ['Microarchitecture',d.microarchitecture],
    ['Process Node',     d.process_node],
    ['Family',           d.family],
    ['Model',            d.model],
    ['Stepping',         d.stepping],
    ['CPUID',            d.identifier, true],
    ['Processor ID',     d.processor_id, true],
    ['Socket',           d.socket],
    ['Cores',            d.cores],
    ['Threads',          d.threads],
    ['P-Cores',          d.topology?.p_cores],
    ['E-Cores',          d.topology?.e_cores],
  ]);

  // Clocks table
  buildTable('cpu-clocks-table', [
    ['Base Clock',        d.base_clock_mhz ? `${d.base_clock_mhz} MHz` : '—'],
    ['Max Turbo Boost',   d.max_turbo_mhz  ? `${d.max_turbo_mhz} MHz`  : '—'],
    ['Current Clock*',    d.current_clock_mhz ? `${d.current_clock_mhz} MHz` : '—'],
    ['psutil Current*',   d.psutil_freq ? `${d.psutil_freq.current?.toFixed(0)} MHz` : '—'],
    ['Bus Clock',         d.base_clock_mhz === 100 || d.base_clock_mhz ? `100 MHz` : '—'],
  ]);

  // Topology diagram
  const topo = d.topology || {};
  const pCores = topo.p_cores || d.cores || 0;
  const eCores = topo.e_cores || 0;
  const topoViz = $('#cpu-topology-viz');
  if (topoViz) {
    let html = '';
    for (let i = 0; i < pCores; i++) {
      html += `<div class="core-box p-core" title="P-Core ${i} (HyperThreaded)">P${i}</div>`;
    }
    for (let i = 0; i < eCores; i++) {
      html += `<div class="core-box e-core" title="E-Core ${i}">E${i}</div>`;
    }
    topoViz.innerHTML = html;
  }

  // Cache hierarchy
  const cacheList = $('#cache-list');
  if (cacheList && d.cache_hierarchy?.length) {
    const maxSize = Math.max(...d.cache_hierarchy.map(c => c.size_kb));
    let html = '';
    d.cache_hierarchy.forEach(c => {
      const cls = `l${c.level}`;
      const pct = Math.max(8, Math.round((c.size_kb / maxSize) * 100));
      const sizeStr = c.size_kb >= 1024 ? `${(c.size_kb / 1024).toFixed(0)} MB` : `${c.size_kb} KB`;
      html += `
        <div class="cache-item" role="listitem">
          <div class="cache-level-badge ${cls}">L${c.level}</div>
          <div class="cache-bar-wrap ${cls}">
            <div class="cache-label">
              <span>${c.type}</span>
              <span>${sizeStr} · ${c.associativity}</span>
            </div>
            <div class="cache-bar">
              <div class="cache-bar-fill" style="width:${pct}%"></div>
            </div>
          </div>
        </div>`;
    });
    cacheList.innerHTML = html;
  } else if (cacheList) {
    // Fallback from WMI aggregate data
    const l2 = d.l2_cache_kb;
    const l3 = d.l3_cache_kb;
    let html = '';
    if (l2) html += `<div class="cache-item"><div class="cache-level-badge l2">L2</div><div class="cache-bar-wrap l2"><div class="cache-label"><span>Unified</span><span>${(l2/1024).toFixed(0)} MB</span></div><div class="cache-bar"><div class="cache-bar-fill" style="width:60%"></div></div></div></div>`;
    if (l3) html += `<div class="cache-item"><div class="cache-level-badge l3">L3</div><div class="cache-bar-wrap l3"><div class="cache-label"><span>Unified</span><span>${(l3/1024).toFixed(0)} MB</span></div><div class="cache-bar"><div class="cache-bar-fill" style="width:100%"></div></div></div></div>`;
    cacheList.innerHTML = html;
  }

  // Feature tags
  const featureTags = $('#feature-tags');
  const features = d.instruction_sets || [];
  setText('#feature-count', features.length);
  if (featureTags) {
    featureTags.innerHTML = features.map(f =>
      `<div class="feature-tag" role="listitem" title="${f}">${f}</div>`
    ).join('');
  }
}

// ── Render Memory ───────────────────────────────────────────────────────────────
function renderMemory(d) {
  const mods = d.modules || [];
  const live = d.live || {};

  buildTable('mem-summary-table', [
    ['Total Installed',    `${d.total_installed_gb} GB`],
    ['Memory Type',        d.memory_type],
    ['Speed',              d.speed_mts ? `${d.speed_mts} MT/s` : '—'],
    ['Channel Config',     d.channel_config],
    ['Module Count',       mods.length],
    ['Slots',              d.array?.slots],
    ['Max Supported',      d.array?.max_capacity_gb ? `${d.array.max_capacity_gb} GB` : '—'],
    ['Used',               live.used_pct ? `${Math.round(live.used_pct)}%` : '—'],
    ['Available',          live.available_gb ? `${live.available_gb} GB` : '—'],
  ]);

  // Capacity viz
  const capViz = $('#mem-capacity-viz');
  if (capViz && mods.length) {
    const maxGB = Math.max(...mods.map(m => m.capacity_gb));
    capViz.innerHTML = mods.map(m => `
      <div class="mem-slot">
        <div class="mem-slot-label">${m.slot || m.bank || 'SLOT'}</div>
        <div class="mem-slot-bar-wrap">
          <div class="mem-slot-bar-fill" style="width:${Math.max(20, (m.capacity_gb / maxGB) * 100)}%">
            <span class="mem-slot-bar-text">${m.capacity_gb} GB ${m.memory_type}</span>
          </div>
        </div>
      </div>`).join('');
  }

  // Module cards
  const grid = $('#mem-module-grid');
  if (grid && mods.length) {
    grid.innerHTML = mods.map((m, i) => `
      <div class="module-card">
        <div class="module-header">
          <span class="module-slot-badge">${m.bank || `DIMM ${i}`}</span>
          <span class="module-mfr">${m.manufacturer}</span>
        </div>
        <table class="spec-table"><tbody>
          <tr><td>Capacity</td><td>${m.capacity_gb} GB</td></tr>
          <tr><td>Type</td><td>${m.memory_type}</td></tr>
          <tr><td>Speed</td><td>${m.speed_mts} MT/s</td></tr>
          <tr><td>Part Number</td><td class="mono">${m.part_number || '—'}</td></tr>
          <tr><td>Serial</td><td class="mono">${m.serial_number || '—'}</td></tr>
        </tbody></table>
      </div>`).join('');
  }
}

// ── Render Mainboard ────────────────────────────────────────────────────────────
function renderMainboard(d) {
  const b = d.board || {};
  const bios = d.bios || {};

  buildTable('board-table', [
    ['Manufacturer',  b.manufacturer],
    ['Model',         b.product],
    ['Version',       b.version, true],
    ['Serial Number', b.serial_number, true],
    ['System Mfr',    b.system_manufacturer],
    ['System Model',  b.system_model],
  ]);

  buildTable('bios-table', [
    ['Vendor',         bios.vendor],
    ['Version',        bios.version, true],
    ['Release Date',   bios.release_date],
    ['SMBIOS Version', bios.smbios_version],
  ]);
}

// ── Render GPU ──────────────────────────────────────────────────────────────────
function renderGPU(gpus) {
  const container = $('#gpu-cards-container');
  if (!container) return;
  if (!gpus || !gpus.length) {
    container.innerHTML = '<div class="unavailable-notice"><svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg><div><strong>No Graphics Adapter Detected</strong><p>No display adapters were found via WMI.</p></div></div>';
    return;
  }
  container.innerHTML = gpus.map((g, i) => `
    <div class="gpu-detail-card">
      <div class="gpu-detail-header">
        <svg width="32" height="32" viewBox="0 0 48 48" fill="none" aria-hidden="true"><rect x="4" y="12" width="40" height="24" rx="4" fill="url(#gd${i})"/><rect x="10" y="18" width="20" height="12" rx="2" fill="rgba(255,255,255,0.15)"/><circle cx="35" cy="24" r="5" fill="rgba(255,255,255,0.2)"/><defs><linearGradient id="gd${i}" x1="4" y1="12" x2="44" y2="36" gradientUnits="userSpaceOnUse"><stop stop-color="#0c4a6e"/><stop offset="1" stop-color="#1e1b4b"/></linearGradient></defs></svg>
        <div>
          <div class="gpu-detail-name">${g.name || '—'}</div>
          <span class="gpu-detail-badge">GPU ${i}</span>
        </div>
      </div>
      <table class="spec-table"><tbody>
        <tr><td>VRAM</td><td>${g.adapter_ram_str || '—'}</td></tr>
        <tr><td>Driver Version</td><td class="mono">${g.driver_version || '—'}</td></tr>
        <tr><td>Resolution</td><td>${g.video_mode || '—'}</td></tr>
        <tr><td>Refresh Rate</td><td>${g.current_refresh_hz ? `${g.current_refresh_hz} Hz` : '—'}</td></tr>
        <tr><td>Status</td><td>${g.status || '—'}</td></tr>
        <tr><td>PNP Device ID</td><td class="mono">${g.device_id || '—'}</td></tr>
      </tbody></table>
    </div>`).join('');
}

// ── Render System ───────────────────────────────────────────────────────────────
function renderSystem(d) {
  const os = d.os || {};
  buildTable('os-table', [
    ['Operating System', os.name],
    ['Version',          os.version, true],
    ['Build Number',     os.build, true],
    ['Architecture',     os.architecture],
    ['Install Date',     os.install_date],
    ['Computer Name',    os.computer_name],
    ['System Directory', os.system_directory],
    ['Boot Time',        d.boot_time],
  ]);

  // Disks
  const diskList = $('#disk-list');
  if (diskList) {
    diskList.innerHTML = (d.disks || []).map(disk => `
      <div class="disk-item">
        <div class="item-title">${disk.model}</div>
        <div class="item-row"><span>Size</span><span>${disk.size_gb} GB</span></div>
        <div class="item-row"><span>Interface</span><span>${disk.interface}</span></div>
        <div class="item-row"><span>Media Type</span><span>${disk.media_type}</span></div>
      </div>`).join('') || '<div class="item-row"><span>No drives detected</span></div>';
  }

  // Disk usage
  const diskUsage = $('#disk-usage-list');
  if (diskUsage) {
    diskUsage.innerHTML = (d.disk_usage || []).map(du => {
      const cls = du.used_pct > 85 ? 'disk-high' : du.used_pct > 60 ? 'disk-med' : 'disk-low';
      return `<div class="disk-usage-item">
        <div class="disk-usage-label">
          <span>${du.mountpoint} (${du.fstype})</span>
          <span>${du.used_gb} / ${du.total_gb} GB (${Math.round(du.used_pct)}%)</span>
        </div>
        <div class="disk-usage-bar-wrap">
          <div class="disk-usage-bar-fill ${cls}" style="width:${du.used_pct}%"></div>
        </div>
      </div>`;
    }).join('') || '<div class="item-row"><span>No partitions</span></div>';
  }

  // Network
  const netList = $('#net-list');
  if (netList) {
    netList.innerHTML = (d.network_adapters || []).map(n => `
      <div class="net-item">
        <div class="item-title">${n.name}</div>
        <div class="item-row"><span>MAC</span><span class="mono">${n.mac}</span></div>
        <div class="item-row"><span>Speed</span><span>${n.speed_mbps ? n.speed_mbps + ' Mbps' : '—'}</span></div>
      </div>`).join('') || '<div class="item-row"><span>No physical adapters detected</span></div>';
  }

  // Battery
  const battInfo = $('#battery-info');
  if (battInfo) {
    const bat = d.battery || {};
    const pct = bat.charge_pct || 0;
    const cls = pct > 60 ? 'batt-high' : pct > 20 ? 'batt-med' : 'batt-low';
    if (Object.keys(bat).length) {
      battInfo.innerHTML = `
        <div class="battery-item">
          <div class="item-title">${bat.name || 'Battery'}</div>
          <div class="battery-bar-wrap">
            <div class="battery-bar-fill ${cls}" style="width:${pct}%"></div>
          </div>
          <div class="item-row"><span>Charge</span><span>${pct}%</span></div>
          <div class="item-row"><span>Status</span><span>${bat.status || '—'}</span></div>
        </div>`;
    } else {
      battInfo.innerHTML = '<div class="unavailable-notice" style="padding:12px;font-size:12px;">No battery detected.</div>';
    }
  }
}

// ── Search ──────────────────────────────────────────────────────────────────────
function buildSearchIndex(allData) {
  _searchIndex = [];
  function addFromObj(section, obj, prefix = '') {
    if (!obj || typeof obj !== 'object') return;
    Object.entries(obj).forEach(([k, v]) => {
      if (Array.isArray(v)) return;
      if (v && typeof v === 'object') return addFromObj(section, v, `${prefix}${k} > `);
      if (v !== null && v !== undefined) {
        _searchIndex.push({ section, key: `${prefix}${k}`, value: String(v) });
      }
    });
  }
  addFromObj('CPU', allData.cpu);
  addFromObj('Memory', allData.memory);
  addFromObj('Mainboard', allData.board);
  addFromObj('GPU', allData.gpu ? allData.gpu[0] : {});
  addFromObj('System', allData.system);
}

$('#global-search')?.addEventListener('input', (e) => {
  const q = e.target.value.trim().toLowerCase();
  const resDiv = $('#search-results');
  if (!q) { resDiv.style.display = 'none'; return; }
  resDiv.style.display = 'block';

  // Hide main sections
  $$('.section').forEach(s => s.classList.remove('active'));

  const results = _searchIndex.filter(r =>
    r.key.toLowerCase().includes(q) || r.value.toLowerCase().includes(q)
  ).slice(0, 30);

  if (!results.length) {
    resDiv.innerHTML = `<div style="color:var(--text-muted);font-size:13px;padding:8px 0">No results for "<em>${q}</em>"</div>`;
    return;
  }

  // Group by section
  const grouped = {};
  results.forEach(r => {
    if (!grouped[r.section]) grouped[r.section] = [];
    grouped[r.section].push(r);
  });

  resDiv.innerHTML = Object.entries(grouped).map(([sec, items]) => `
    <div class="search-section-label">${sec}</div>
    ${items.map(r => `
      <div class="search-result-item" data-section="${sec.toLowerCase()}" role="option" tabindex="0">
        <span class="search-result-key">${r.key}</span>
        <span class="search-result-val">${r.value}</span>
      </div>`).join('')}
  `).join('');

  resDiv.querySelectorAll('.search-result-item').forEach(item => {
    item.addEventListener('click', () => {
      e.target.value = '';
      resDiv.style.display = 'none';
      navigate(item.dataset.section);
    });
  });
});

// ── Export ──────────────────────────────────────────────────────────────────────
$('#export-json')?.addEventListener('click', () => { window.location.href = `${API}/export/json`; });
$('#export-csv')?.addEventListener('click',  () => { window.location.href = `${API}/export/csv`; });

// ── Refresh ─────────────────────────────────────────────────────────────────────
$('#refresh-btn')?.addEventListener('click', () => loadAll(true));

// ── Live Polling ────────────────────────────────────────────────────────────────
async function pollLive() {
  try {
    const live = await fetchData('cpu/live');
    updateGauge('#cpu-gauge-arc', '#cpu-gauge-val', live.overall_pct || 0);
  } catch (_) { /* silent */ }
}

// ── Main Load ───────────────────────────────────────────────────────────────────
async function loadAll(forceRefresh = false) {
  try {
    // Parallel fetch all sections
    const [overview, cpu, memory, mainboard, gpu, system] = await Promise.all([
      fetchData('overview'),
      fetchData('cpu'),
      fetchData('memory'),
      fetchData('mainboard'),
      fetchData('gpu'),
      fetchData('system'),
    ]);

    _data = { overview, cpu, memory, mainboard, gpu, system };

    // Build overview from overview endpoint + extra data
    renderOverview({
      cpu: { ...overview.cpu, microarchitecture: cpu.microarchitecture, process_node: cpu.process_node },
      memory: overview.memory,
      board: overview.board,
      gpu: overview.gpu,
      os: overview.os,
      battery: overview.battery,
      boot_time: system.boot_time,
    });

    renderCPU(cpu);
    renderMemory(memory);
    renderMainboard(mainboard);
    renderGPU(Array.isArray(gpu) ? gpu : [gpu]);
    renderSystem(system);
    buildSearchIndex({ cpu, memory, board: mainboard.board, gpu: Array.isArray(gpu) ? gpu : [gpu], system });

    setStatus(true);
    const now = new Date().toLocaleTimeString();
    setText('#last-updated', `Updated ${now}`);
    hideLoading();

    // Start live polling
    if (_liveTimer) clearInterval(_liveTimer);
    _liveTimer = setInterval(pollLive, LIVE_INTERVAL_MS);

  } catch (err) {
    console.error(err);
    setStatus(false);
    showError(`Failed to load hardware data: ${err.message}. Is the backend running on port 7890?`);
    hideLoading();
  }
}

// ── Boot ────────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadAll();
  navigate('overview');
});
