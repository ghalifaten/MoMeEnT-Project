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

// Parse the Data
d3.csv("static/data/XYZ.csv", function(data) {

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
        .style("text-anchor", "end");

    // Add Y axis
    var y = d3.scaleLinear()
                .domain([0, 4])
                .range([ height, 0]);

    svg.append("g")
        .call(d3.axisLeft(y));

    // Bars
    svg.selectAll("bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", function(d) { return x(d.Period); })
        .attr("y", function(d) { return y(d.Value); })
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

    // Listen to the sliders
    //morning
    d3.select("#morningSlider").on("change", function(d){
        morningValue = this.value
        updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
        })
    //midday
    d3.select("#middaySlider").on("change", function(d){
        middayValue = this.value
        updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
        })
    //afternoon
    d3.select("#afternoonSlider").on("change", function(d){
        afternoonValue = this.value
        updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
        })
    //evening
    d3.select("#eveningSlider").on("change", function(d){
        eveningValue = this.value
        updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
        })
    //night
    d3.select("#nightSlider").on("change", function(d){
        nightValue = this.value
        updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
        })

    /*
        // Listen to the submit button
    d3.select("#submit-btn").on("click", function(d){
        updateChart(morningValue, middayValue, afternoonValue, eveningValue, nightValue)
        })
    */
});

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
    })}