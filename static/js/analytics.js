document.addEventListener('DOMContentLoaded', function() {
    const colors = ['#016A70', '#FFFFDD', '#D2DE32', '#A2C579'];

    // ====== BAR CHART ======
    const barEl = document.getElementById('bar-chart');
    if (barEl) {
        const barData = JSON.parse(barEl.dataset.json);
        const trace = { x: barData.labels, y: barData.values, type:'bar', marker:{color:colors[0]} };
        const layout = { margin:{t:40,b:40,l:40,r:40}, plot_bgcolor:'rgba(255,255,255,0.1)', paper_bgcolor:'rgba(255,255,255,0.1)', font:{color:colors[0]}, yaxis:{title:'Products'}, xaxis:{title:'Owner'} };
        Plotly.newPlot(barEl,[trace],layout,{responsive:true});
    }

    // ====== PIE CHART ======
    const pieEl = document.getElementById('pie-chart');
    if (pieEl) {
        const pieData = JSON.parse(pieEl.dataset.json);
        const trace = { labels: pieData.labels, values: pieData.values, type:'pie', marker:{colors:colors}, hole:0.3 };
        const layout = { margin:{t:40}, font:{color:colors[0]}, paper_bgcolor:'rgba(255,255,255,0.1)' };
        Plotly.newPlot(pieEl,[trace],layout,{responsive:true});
    }

    // ====== LINE CHART ======
    const lineEl = document.getElementById('line-chart');
    if (lineEl) {
        const lineData = JSON.parse(lineEl.dataset.json);
        const trace = { x: lineData.dates, y: lineData.counts, type:'scatter', mode:'lines+markers', line:{color:colors[2], width:3}, marker:{size:6,color:colors[2]} };
        const layout = { margin:{t:40,b:40,l:40,r:40}, plot_bgcolor:'rgba(255,255,255,0.1)', paper_bgcolor:'rgba(255,255,255,0.1)', font:{color:colors[0]}, yaxis:{title:'Products'}, xaxis:{title:'Date'} };
        Plotly.newPlot(lineEl,[trace],layout,{responsive:true});
    }

    // ====== STATUS CHART (Donut) ======
    const statusEl = document.getElementById('status-chart');
    if (statusEl) {
        const statusData = JSON.parse(statusEl.dataset.json);
        const trace = { labels: statusData.labels, values: statusData.values, type:'pie', marker:{colors:colors}, hole:0.5 };
        const layout = { margin:{t:40}, font:{color:colors[0]}, paper_bgcolor:'rgba(255,255,255,0.1)' };
        Plotly.newPlot(statusEl,[trace],layout,{responsive:true});
    }
});
