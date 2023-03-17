//Get data file from parameters of Script tag
function getSyncScriptParams() {
    var scripts = document.getElementsByTagName('script');
    var lastScript = scripts[scripts.length-1];
    var scriptName = lastScript;

    return scriptName.getAttribute('exp_nbr');
}

// set the dimensions and margins of the graph
var margin = {top: 0, right: 30, bottom: 90, left: 60},
    width = 800 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#bar-chart")
            .append("svg")
            .attr("class", "svg-style")
            .append("g");


// initialize variables of sliders
var morningValue = 0, middayValue = 0, afternoonValue = 0, eveningValue = 0, nightValue = 0;
var current_data = [{ Period: "morning (06:00-09:59)", Value: "0" },
                    { Period: "midday (10:00-13:59)", Value: "0" },
                    { Period: "afternoon (14:00-17:59)", Value: "0" },
                    { Period: "evening (18:00-21:59)", Value: "0" },
                    { Period: "night (22:00-05:59)", Value: "0" }];

window.localStorage.setItem("current_data", JSON.stringify(current_data));

// Add legend (Manually)
var legendItemSize = 12;
var legendSpacing = 5;
var xOffset = 0;
var yOffset = 10;

var legend_data = [ { Text: "Habitual behavior", Color: "#D3D3D3" },
                    { Text: "New behavior", Color: "#69b3a2" },
                    { Text: "Price line", Color: "red"} ];

var legend = d3.select('#bar-chart-legend')
                .append('svg')
                .append('g')
                .selectAll(".legendItem")
                .data(legend_data);

legend.enter().append('rect')
        .attr('class', 'legendItem')
        .attr('width', legendItemSize)
        .attr('height', legendItemSize)
        .style('fill', d => d.Color)
        .attr('transform',
                    (d, i) => {
                        var x = xOffset;
                        var y = yOffset + (legendItemSize + legendSpacing) * i;
                        return `translate(${x}, ${y})`;
                    });
                    
legend.enter().append('text')
        .attr('x', xOffset + legendItemSize + 5)
        .attr('y', (d, i) => yOffset + (legendItemSize + legendSpacing) * i + 12)
        .text(d => d.Text); 

// Load data
var data = JSON.parse(window.localStorage.getItem("baseline_data"));
var price_data;

// Load price data and add line to the chart
d3.csv('static/data/price_data.csv',function (d) {
    price_data = d;
    add_line(price_data);
});

function add_line(price_data) { 
    // Define the line
    var valueline = d3.line()
                        .x(function(d) { return x(d.Period); })
                        .y(function(d) { return y(d.Value); })
                        .curve(d3.curveStep);
                    
    // Add the line path
    svg.append("path")
        .attr("class", "line")
        .style("stroke", "red")
        .style("stroke-width", 3)
        .attr("fill", "none")
        .attr("d", valueline(price_data))
        .attr("transform", "translate(58,0)");
}

// Add X axis
var x = d3.scaleBand()
            .range([ 0, width ])
            .domain(data.map(function(d) { return d.Period; }))
            //.padding(0.7);
            .paddingInner(.1)
            .paddingOuter(.3)

svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x))
    .selectAll(".tick text")
    .call(wrap, x.bandwidth())
    .attr("transform", "translate(50,0)")
    .attr("font-size", "12px")
    .attr("font-weight", "bold")
    .style("text-anchor", "end");

    
// Add Y axis
var y = d3.scaleLinear()
.domain([0, 4])
.range([height, 0]);

// Bars
svg.selectAll("bar")
    .data(data)
    .enter()
    .append("rect")
    .attr("x", function(d) { return x(d.Period); })
    .attr("y", function(d) {return y(d.Value); })
    .attr("width", 20)
    .attr("height", function(d) { return height - y(d.Value); })
    .attr("fill", "#D3D3D3")
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("transform", "translate(48,0)")
    .attr("class", "baseline-bar")

// A function that updates the chart when slider is moved
function updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue) {
    //TODO optimize this
    data[0].Value = morningValue;
    data[1].Value = middayValue;
    data[2].Value = afternoonValue;
    data[3].Value = eveningValue;
    data[4].Value = nightValue;

    svg.selectAll(".new-bar").remove();
    
    svg.selectAll("bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", function(d) { return x(d.Period); })
        .attr("y", function(d) { return y(d.Value); })
        .attr("width", 20)
        .attr("height", function(d) { return height - y(d.Value); })
        .attr("fill", "#69b3a2")
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("transform", "translate(60,0)")
        .attr("class", "new-bar")
    
    window.localStorage.setItem("current_data", JSON.stringify(data));
    return data;
}

// Listen to the sliders
//morning
d3.select("#morningSlider").on("change", function(d){
    morningValue = this.value
    current_data = updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
})
//midday
d3.select("#middaySlider").on("change", function(d){
    middayValue = this.value
    current_data = updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
})
//afternoon
d3.select("#afternoonSlider").on("change", function(d){
    afternoonValue = this.value
    current_data = updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
})
//evening
d3.select("#eveningSlider").on("change", function(d){
    eveningValue = this.value
    current_data = updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
})
//night
d3.select("#nightSlider").on("change", function(d){
    nightValue = this.value
    current_data = updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
})


// Listen to the submit button
function difference(baseline_data, current_data) {
    var baseline_sum = baseline_data.reduce((partialSum, a) => partialSum + parseInt(a.Value), 0);
    var baseline_avg = baseline_sum/5 * 100;
    var current_sum = current_data.reduce((partialSum, a) => partialSum + parseInt(a.Value), 0);
    var current_avg = current_sum/5 * 100;
    return [current_sum - baseline_sum, current_avg - baseline_avg];
}

d3.select("#stats-btn").on("click", function(d){   
    function getDiff() {
        const current_data = JSON.parse(window.localStorage.getItem("current_data"))

        //... and send them to Flask to use them in computing the cost.
        $.ajax({
            url: location.origin + "/get-diff",
            type: 'POST',
            data: JSON.stringify({
                "data": current_data,
                "scenario": "sc1",
            }),
            contentType: "application/json",
            dataType: "json",
            success: function (response) {
                const cost = response.diff_cost;
                if (cost != 0) {
                    let counts=setInterval(updated);
                    let upto=0;
                    function updated(){
                        var count= document.getElementById("stats-nbr-you");
                        count.innerHTML=++upto;
                        if(upto===Math.abs(Math.ceil(cost))){ clearInterval(counts); }
                    }
                }
            
                //update stats-you 
                if (cost >= 0) {
                    document.getElementById("stats-txt-you").innerText = "Increase in cost for running the dishwasher."
                    document.getElementById("stats-icon-you").innerHTML = "<img src=\"static/data/arrow-increase.png\"></img>"
                } else {
                    document.getElementById("stats-txt-you").innerText = "Decrease in cost for running the dishwasher."
                    document.getElementById("stats-icon-you").innerHTML = "<img src=\"static/data/arrow-decrease.png\"></img>"
                }
            },
            error: function (response) {
                alert("You have exceeded the limit of 3 trials for this scenario!")
            }
        });
    }
    getDiff()
    
    //Animation for statistics numbers
    var baseline_data = JSON.parse(window.localStorage.getItem("baseline_data"));
    var current_data = JSON.parse(window.localStorage.getItem("current_data"));
    const differences = difference(baseline_data, current_data);
    const diffValue = differences[0];
    const diffAvg = differences[1];

   
    if (diffAvg != 0) {
        let counts=setInterval(updated);
        
        let upto=0;
        function updated(){
            var count= document.getElementById("stats-nbr-avg");
            count.innerHTML=++upto;
            if(upto===Math.abs(Math.ceil(diffAvg))){ clearInterval(counts); }
        }
    }

    //update stats-avg
    if (diffAvg >= 0) {
        document.getElementById("stats-txt-avg").innerText = "Increase in cost for running the dishwasher."
        document.getElementById("stats-icon-avg").innerHTML = "<img src=\"static/data/arrow-increase.png\"></img>"
    } else {
        document.getElementById("stats-txt-avg").innerText = "Decrease in cost for running the dishwasher."
        document.getElementById("stats-icon-avg").innerHTML = "<img src=\"static/data/arrow-decrease.png\"></img>"
    }

})


//For long x-axis labels to be written on two lines
function wrap(text, width) {
    text.each(function() {
      var text = d3.select(this),
          words = text.text().split(/\s+/).reverse(),
          word,
          line = [],
          lineNumber = 0,
          lineHeight = 1.1, // ems
          y = text.attr("y"),
          dy = parseFloat(text.attr("dy")),
          tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em")
      while (word = words.pop()) {
        line.push(word)
        tspan.text(line.join(" "))
        if (tspan.node().getComputedTextLength() > width) {
          line.pop()
          tspan.text(line.join(" "))
          line = [word]
          tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", `${++lineNumber * lineHeight + dy}em`).text(word)
        }
      }
    })
}

