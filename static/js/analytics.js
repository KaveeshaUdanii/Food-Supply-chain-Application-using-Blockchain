function renderChart(id, data, type, layoutOverrides={}) {
    let trace, layout;

    switch(type) {
        case "line":
            trace = [
                { x: data.timestamps, y: data.temperature, name: "Temp (°C)", mode: "lines+markers" },
                { x: data.timestamps, y: data.humidity, name: "Humidity (%)", mode: "lines+markers" }
            ];
            layout = { colorway: ["#016A70","#D2DE32"], ...layoutOverrides };
            break;

        case "bar":
            trace = [{ x: data.owners, y: data.violations || data.counts, type: "bar" }];
            layout = { colorway: ["#A2C579"], ...layoutOverrides };
            break;

        case "pie":
            trace = [{ labels: data.labels, values: data.values, type: "pie" }];
            layout = { colorway: ["#016A70","#FFFFDD","#D2DE32"], ...layoutOverrides };
            break;

        case "scatter":
            trace = [{ x: data.distance, y: data.time, mode: "markers" }];
            layout = { xaxis:{title:"Distance (km)"}, yaxis:{title:"Time (h)"}, ...layoutOverrides };
            break;

        case "heatmap":
            trace = [{ z: data.counts, x: data.locations, y:["Violations"], type:"heatmap", colorscale:[["0","#FFFFDD"],["1","#016A70"]] }];
            layout = { ...layoutOverrides };
            break;

        case "stacked":
            trace = [{ x: data.statuses, y: data.counts, type:"bar" }];
            layout = { barmode:"stack", colorway:["#016A70","#D2DE32","#A2C579"], ...layoutOverrides };
            break;

        case "timeline":
            trace = [{ x: data.batches, y: data.durations, type:"bar" }];
            layout = { xaxis:{title:"Batch"}, yaxis:{title:"Duration (days)"}, ...layoutOverrides };
            break;

        case "network":
            // Placeholder (Plotly doesn't directly support networks) → show as scatter
            trace = [{
                x: [1,2,3,4],
                y: [1,3,2,4],
                text: data.nodes,
                mode: "markers+text",
                textposition: "top center"
            }];
            layout = { ...layoutOverrides };
            break;
    }

    Plotly.newPlot(id, trace, layout, {responsive:true});
}

// Render all charts
document.addEventListener("DOMContentLoaded", function() {
    let charts = [
        ["safety-line-chart","line"],
        ["violations-bar-chart","bar"],
        ["heatmap-chart","heatmap"],
        ["fraud-pie-chart","pie"],
        ["fraud-scatter-chart","scatter"],
        ["fraud-network-chart","network"],
        ["performance-bar-chart","bar"],
        ["performance-stacked-chart","stacked"],
        ["performance-timeline-chart","timeline"]
    ];

    charts.forEach(([id, type]) => {
        let el = document.getElementById(id);
        if (el) {
            let data = JSON.parse(el.dataset.json);
            renderChart(id, data, type);
        }
    });
});
