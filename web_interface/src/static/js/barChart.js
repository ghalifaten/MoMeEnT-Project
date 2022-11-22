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
var svg = d3.select("#bar_chart")
            .append("svg")
            .attr("class", "svg-style")
            .append("g");


// initialize variables of sliders
var morningValue = 0, middayValue = 0, afternoonValue = 0, eveningValue = 0, nightValue = 0;
var baseline_data = [{ Period: "morning (06:00-09:59)", Value: "0" },
                     { Period: "midday (10:00-13:59)", Value: "0" },
                     { Period: "afternoon (14:00-17:59)", Value: "0" },
                     { Period: "evening (18:00-21:59)", Value: "0" },
                     { Period: "night (22:00-05:59)", Value: "0" }];

var current_data = []

// Parse the Data
exp_nbr = getSyncScriptParams()
if (exp_nbr == "0") {
    var data = baseline_data;
} else if (exp_nbr == "1") {
    var data = current_data;
}

//d3.csv(datafile, function(data) {

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
        .attr("y", function(d) {baseline_data.push(d.Value); return y(d.Value); })
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

        /* svg.selectAll(".baseline-bar")
            .attr("fill", "#D3D3D3");*/

        svg.selectAll(".new-bar").remove();
        
        if (exp_nbr == "0") {
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
                .attr("transform", "translate(48,0)")
                .attr("class", "new-bar")

        } else if (exp_nbr == "1") {
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
        }
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
        var baseline_sum = baseline_data.reduce((partialSum, a) => partialSum + parseInt(a), 0)
        var current_sum = current_data.reduce((partialSum, a) => partialSum + parseInt(a.Value), 0)
        return baseline_sum - current_sum;
    }

    d3.select("#stats-btn").on("click", function(d){
        //Animation for statistics numbers
        const end = difference(baseline_data, current_data);
        d3.select('#stats-nbr').transition()
        .tween("text", () => {
            const interpolator = d3.interpolateNumber(0, end);
            return function(t) {
            d3.select(this).text(Math.round(interpolator(t))) 
            }
        })
        .duration(1000);
    })

    /* **Not a good idea because this will download a file on the client-side
    d3.select("#link-to-exp1").on("click", function(d){
        const titleKeys = Object.keys(current_data[0]) //get keys from first the first object in the array (since they are the same for all objects)
        const refinedData = [] //refinedData contains data in the format that is suitable for export to csv
        refinedData.push(titleKeys) //add in the keys for the first row then loop over all the objects to get the values
        current_data.forEach(item => {
            refinedData.push(Object.values(item))  
        })
        //create the csv file content
        let csvContent = ''
        refinedData.forEach(row => {
            csvContent += row.join(',') + '\n'
        })
        //create the URI and use a hidden <a> to download the file

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8,' })
        const objUrl = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.setAttribute('href', objUrl)
        link.setAttribute('download', 'exp1_baseline.csv')
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    })
    */

//});

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



