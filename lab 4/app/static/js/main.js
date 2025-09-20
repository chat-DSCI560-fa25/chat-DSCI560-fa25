window.lastBacktestResult = null;

function fmt(n) {
  return (n == null ? '–'
    : Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
}

async function loadPortfolios() {
  const sel = document.getElementById('portfolio');
  if (!sel) return;

  try {
    const res = await fetch('/api/portfolios', { cache: 'no-store' });
    if (!res.ok) {
      const t = await res.text().catch(() => res.statusText);
      throw new Error(`GET /api/portfolios ${res.status} ${t}`);
    }
    const items = await res.json();

    sel.innerHTML = '';
    if (!Array.isArray(items) || items.length === 0) {
      sel.disabled = true;
      sel.insertAdjacentHTML('beforeend', '<option value="">(no portfolios)</option>');
      return;
    }

    items.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      sel.appendChild(opt);
    });
    sel.disabled = false;

    const pid = new URL(location.href).searchParams.get('pid');
    if (pid) {
      const o = [...sel.options].find(o => String(o.value) === String(pid));
      if (o) sel.value = o.value;
    }
  } catch (err) {
    console.error('[BT] loadPortfolios failed:', err);
    alert('Could not load portfolios. Check console/network.');
  }
}

async function runBacktest() {
  const sel = document.getElementById('portfolio');
  if (!sel || !sel.value) {
    alert('Choose a portfolio first.');
    return;
  }

  const body = {
    portfolio_id: Number(sel.value),
    start_date: document.getElementById('start').value,
    end_date: document.getElementById('end').value,
    cash_start: Number(document.getElementById('cash').value || 0),
    params: {
      strategy: (document.getElementById('strategy')?.value || 'sma').toLowerCase(),
      short: Number(document.getElementById('smaShort')?.value || 10),
      long: Number(document.getElementById('smaLong')?.value || 30),
    }
  };

  const runBtn = document.getElementById('runBtn');
  const saveBtn = document.getElementById('saveBtn');
  const downloadBtn = document.getElementById('downloadBtn');
  const statusMsg = document.getElementById('statusMessage');

  runBtn.disabled = true;
  saveBtn.style.display = 'none';
  downloadBtn.style.display = 'none';
  window.lastBacktestResult = null;
  statusMsg.textContent = 'Fetching data and running backtest...';
  statusMsg.style.color = 'blue';

  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!res.ok) {
      let msg = res.statusText;
      try { const j = await res.json(); msg = j.error || msg; } catch { }
      throw new Error(`Run failed: ${msg}`);
    }

    const data = await res.json();
    statusMsg.textContent = 'Backtest complete. You can now save or download.';
    statusMsg.style.color = 'green';

    window.lastBacktestResult = { params: body, kpis: data.kpis, trades: data.trades };
    saveBtn.style.display = 'inline-block';
    downloadBtn.style.display = 'inline-block';

    const k = data.kpis || {};
    const el = id => document.getElementById(id);
    if (el('kpiValue')) el('kpiValue').textContent = `$${fmt(k.portfolio_value)}`;
    if (el('kpiTotal')) el('kpiTotal').textContent = `$${fmt(k.total_pnl)}`;
    if (el('kpiReturn')) el('kpiReturn').textContent = `${fmt(k.return_pct)}%`;
    if (el('kpiSharpe')) el('kpiSharpe').textContent = fmt(k.sharpe_ratio);
    if (el('kpiDrawdown')) el('kpiDrawdown').textContent = `${fmt(k.max_drawdown_pct)}%`;

    const pb = el('posBody');
    if(pb){
      pb.innerHTML = '';
      (data.positions || []).forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${r.symbol}</td><td>${r.qty}</td><td>$${fmt(r.avg_cost)}</td><td>$${fmt(r.last)}</td><td>$${fmt(r.unrealized)}</td>`;
        pb.appendChild(tr);
      });
      if(!pb.children.length) pb.innerHTML = `<tr><td colspan="5" class="muted">No open positions.</td></tr>`;
    }

    const tb = el('tradesBody');
    if(tb){
      tb.innerHTML = '';
      (data.trades || []).forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${r.date}</td><td>${r.symbol}</td><td>${r.side}</td><td>${r.qty}</td><td>$${fmt(r.price)}</td>`;
        tb.appendChild(tr);
      });
      if(!tb.children.length) tb.innerHTML = `<tr><td colspan="5" class="muted">No trades in this range.</td></tr>`;
    }
  } catch (err) {
    statusMsg.textContent = err.message;
    statusMsg.style.color = 'red';
  } finally {
    runBtn.disabled = false;
  }
}

async function saveSession() {
  if (!window.lastBacktestResult) {
    alert("No backtest result to save. Please run a backtest first.");
    return;
  }

  const saveBtn = document.getElementById('saveBtn');
  saveBtn.disabled = true;
  saveBtn.textContent = 'Saving...';

  try {
    const res = await fetch('/api/save_session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(window.lastBacktestResult)
    });

    if (!res.ok) {
      let msg = res.statusText;
      try { const j = await res.json(); msg = j.error || msg; } catch {}
      throw new Error(`Save failed: ${msg}`);
    }

    const data = await res.json();
    alert(`Session saved successfully! (Session ID: ${data.session_id})`);
    saveBtn.style.display = 'none';

  } catch (err) {
    alert(err.message);
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = 'Save Session';
  }
}

async function downloadCSV() {
  if (!window.lastBacktestResult) {
    alert("No result to download.");
    return;
  }

  const downloadBtn = document.getElementById('downloadBtn');
  downloadBtn.disabled = true;
  downloadBtn.textContent = 'Preparing...';

  try {
    const res = await fetch('/api/download_csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(window.lastBacktestResult)
    });

    if (!res.ok) {
      throw new Error('Failed to prepare download.');
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    const filename = res.headers.get('content-disposition')?.split('filename=')[1] || 'trades.csv';
    a.download = filename;
    
    document.body.appendChild(a);
    a.click();
    
    window.URL.revokeObjectURL(url);
    a.remove();

  } catch (err) {
    alert(err.message);
  } finally {
    downloadBtn.disabled = false;
    downloadBtn.textContent = 'Download CSV';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadPortfolios();
  
  const runBtn = document.getElementById('runBtn');
  if (runBtn) runBtn.addEventListener('click', runBacktest);
  
  const saveBtn = document.getElementById('saveBtn');
  if (saveBtn) saveBtn.addEventListener('click', saveSession);
  
  const downloadBtn = document.getElementById('downloadBtn');
  if (downloadBtn) downloadBtn.addEventListener('click', downloadCSV);
});