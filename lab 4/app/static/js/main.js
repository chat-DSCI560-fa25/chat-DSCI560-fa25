function fmt(n){ return (n==null? '–' : Number(n).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})); }


async function loadPortfolios(){
const res = await fetch('/api/portfolios');
const items = await res.json();
const sel = document.getElementById('portfolio');
sel.innerHTML = '';
items.forEach(p => {
const opt = document.createElement('option');
opt.value = p.id; opt.textContent = p.name; sel.appendChild(opt);
});
}


async function runBacktest(){
const body = {
portfolio_id: Number(document.getElementById('portfolio').value),
start_date: document.getElementById('start').value,
end_date: document.getElementById('end').value,
cash_start: Number(document.getElementById('cash').value || 0),
params: {}
};


const res = await fetch('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
const data = await res.json();


// Very Important needed KPIs
document.getElementById('kpiValue').textContent = `$${fmt(data.kpis?.portfolio_value)}`;
document.getElementById('kpiTotal').textContent = `$${fmt(data.kpis?.total_pnl)}`;
document.getElementById('kpiDay').textContent = `$${fmt(data.kpis?.day_pnl)}`;


// Ofcourse,Positions
const pb = document.getElementById('posBody'); pb.innerHTML = '';
(data.positions || []).forEach(r => {
const tr = document.createElement('tr');
tr.innerHTML = `
<td>${r.symbol}</td>
<td>${r.qty}</td>
<td>$${fmt(r.avg_cost)}</td>
<td>$${fmt(r.last)}</td>
<td>$${fmt(r.unrealized)}</td>`;
pb.appendChild(tr);
});


// The Trades
const tb = document.getElementById('tradesBody'); tb.innerHTML = '';
(data.trades || []).forEach(r => {
const tr = document.createElement('tr');
tr.innerHTML = `
<td>${r.date}</td>
<td>${r.symbol}</td>
<td>${r.side}</td>
<td>${r.qty}</td>
<td>$${fmt(r.price)}</td>`;
tb.appendChild(tr);
});
}


document.addEventListener('DOMContentLoaded', () => {
loadPortfolios();
document.getElementById('runBtn').addEventListener('click', runBacktest);
});