document.addEventListener('DOMContentLoaded', function() {
    // ================= Bar Chart =================
    const barEl = document.getElementById('bar-chart');
    if (barEl) {
        const data = JSON.parse(barEl.dataset.json);
        const trace = {
            x: data.labels,
            y: data.values,
            type: 'bar',
            marker: { color: '#016A70' },
        };
        const layout = {
            margin: { t: 40, b: 40, l: 40, r: 40 },
            plot_bgcolor: 'rgba(255,255,255,0.1)',
            paper_bgcolor: 'rgba(255,255,255,0.1)',
            font: { color: '#016A70' },
            yaxis: { title: 'Products', zeroline: false },
            xaxis: { title: 'Owner' }
        };
        Plotly.newPlot(barEl, [trace], layout, {responsive: true});
    }

    // ================= Pie Chart =================
    const pieEl = document.getElementById('pie-chart');
    if (pieEl) {
        const data = JSON.parse(pieEl.dataset.json);
        const trace = [{
            labels: data.labels,
            values: data.values,
            type: 'pie',
            marker: {
                colors: ['#016A70','#FFFFDD','#D2DE32','#A2C579']
            },
            textinfo: 'label+percent'
        }];
        const layout = {
            margin: { t: 40, b: 40 },
            plot_bgcolor: 'rgba(255,255,255,0.1)',
            paper_bgcolor: 'rgba(255,255,255,0.1)',
            font: { color: '#016A70' }
        };
        Plotly.newPlot(pieEl, trace, layout, {responsive: true});
    }

    // ================= Line Chart =================
    const lineEl = document.getElementById('line-chart');
    if (lineEl) {
        const data = JSON.parse(lineEl.dataset.json);
        const trace = {
            x: data.x,
            y: data.y,
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#D2DE32', width: 3 },
            marker: { color: '#016A70', size: 6 }
        };
        const layout = {
            margin: { t: 40, b: 40, l: 40, r: 40 },
            plot_bgcolor: 'rgba(255,255,255,0.1)',
            paper_bgcolor: 'rgba(255,255,255,0.1)',
            font: { color: '#016A70' },
            yaxis: { title: 'Temperature (°C)', zeroline: false },
            xaxis: { title: 'Date' }
        };
        Plotly.newPlot(lineEl, [trace], layout, {responsive: true});
    }
});
