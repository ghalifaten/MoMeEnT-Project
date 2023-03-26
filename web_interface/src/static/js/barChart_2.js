//Get data file from parameters of Script tag
function getSyncScriptParams() {
    var scripts = document.getElementsByTagName('script');
    var lastScript = scripts[scripts.length-1];
    var scriptName = lastScript;

    return scriptName.getAttribute('exp_nbr');
}

// set the dimensions and margins of the graph
var margin = {top: 0, right: 30, bottom: 90, left: 60},
    width = 1000 - margin.left - margin.right,
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
var legendSpacing = 10;
var xOffset = 0;
var yOffset = 10;

var legend_data = [ { Text: "Habitual behavior", Color: "#D3D3D3" },
                    { Text: "New behavior", Color: "#69b3a2" },
                    { Text: "Peak hours", Color: "#f9d4da"}];

var legend = d3.select('#bar-chart-legend')
                .append('svg')
                .append('g')
                .attr("transform", "translate(-150,0)")
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
                        var y = yOffset + (legendItemSize + legendSpacing) * i - 12;
                        return `translate(${x}, ${y})`;
                    });
                    
legend.enter().append('text')
        .attr('x', xOffset + legendItemSize + 5)
        .attr('y', (d, i) => yOffset + (legendItemSize + legendSpacing) * i)
        .text(d => d.Text); 

// Load data
var data = JSON.parse(window.localStorage.getItem("baseline_data"));

// Add X axis
var x = d3.scaleBand()
            .range([ 0, width ])
            .domain(data.map(function(d) { return d.Period; }))
            //.padding(0.7);
            .paddingInner(.1)
            .paddingOuter(.3)

svg.append("g")
    .attr("transform", "translate(-150," + height + ")")
    .call(d3.axisBottom(x))
    .selectAll(".tick text")
    .call(wrap, 100)
    .attr("transform", "translate(45,2)")
    .attr("font-size", "16px")
    .attr("font-weight", "bold")
    .style("text-anchor", "end");

    
// Add Y axis
var y = d3.scaleLinear()
.domain([0, 4])
.range([height, 0]);

//Add "Peak hours" rectangle
svg.selectAll("bar")
    .data(data)
    .enter()
    .append("rect")
    .attr("x", function(d) { return x(data[2].Period); })
    .attr("y", 0)
    .attr("width", 250)
    .attr("height", 310)
    .attr("fill", "#f9d4da")
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("transform", "translate(-120,0)")
    .attr("class", "peak-hours-rect")
    

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
    .attr("transform", "translate(-85,0)")
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
        .attr("transform", "translate(-75,0)")
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


d3.select("#stats-btn").on("click", function(d){  
    function getDiff() {
        //hide stats, show loader and disable buttons
        document.getElementById("stats-icon-you").style.display = "none";    
        document.getElementById("stats-nbr-you").style.display = "none";    
        document.getElementById("stats-old-val").hidden = true; 
        document.getElementById("stats-new-val").hidden = true;
        document.getElementById("loader").style.display = "block";        
        document.getElementById("stats-btn").disabled = true;
        document.getElementById("link-to-exp2").disabled = true;

        //send data to flask
        const current_data = JSON.parse(window.localStorage.getItem("current_data"))
        $.ajax({
            url: location.origin + "/get-diff",
            type: 'POST',
            data: JSON.stringify({
                "data": current_data,
                "scenario": "sc2",
            }),
            contentType: "application/json",
            dataType: "json",
            success: function (response) {
                //when response is received, hide loader, re-activate buttons and show results 
                document.getElementById("stats-icon-you").style.display = "block";    
                document.getElementById("stats-nbr-you").style.display = "block";    
                document.getElementById("loader").style.display = "none"
                document.getElementById("stats-btn").disabled = false;
                document.getElementById("link-to-exp2").disabled = false;

                const diff_peak = response.diff_peak;
                const peak = response.peak_load;

                var count = document.getElementById("stats-nbr-you");
                if (diff_peak != 0) {
                    let counts=setInterval(updated);
                    let upto=0;
                    function updated(){
                        count.innerHTML=++upto;
                        if(upto===Math.abs(Math.ceil(diff_peak))){ clearInterval(counts); }
                    }
                } else {
                    count.innerHTML = 0
                }
            
                //update stats-you 
                document.getElementById("stats-new-val").innerHTML = "<strong>New peak <br>" + peak + "</strong>" 
                document.getElementById("stats-old-val").hidden = false; 
                document.getElementById("stats-new-val").hidden = false;

                //update icon
                if (diff_peak >= 0) {
                    document.getElementById("stats-icon-you").innerHTML = "<img src=\"static/img/arrow-increase.png\"></img>"
                } else {
                    document.getElementById("stats-icon-you").innerHTML = "<img src=\"static/img/arrow-decrease.png\"></img>"
                }

                //update tooltip text of the [See Statistics] button
                document.getElementById("stats-btn").title = response.n_trials + " trials left"
            },
            error: function (response) {
                document.getElementById("link-to-exp2").disabled = false;
                document.getElementById("loader").style.display = "none"
                alert("You have exceeded the limit of 3 trials for this scenario!")
            }
        });
    }
    getDiff()

    const avg_peak = 35
    if (avg_peak != 0) {
        let counts=setInterval(updated);
        
        let upto=0;
        function updated(){
            var count= document.getElementById("stats-nbr-avg");
            count.innerHTML=++upto;
            if(upto===Math.abs(Math.ceil(avg_peak))){ clearInterval(counts); }
        }
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

