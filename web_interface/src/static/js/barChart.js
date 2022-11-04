// set the dimensions and margins of the graph
var margin = {top: 0, right: 30, bottom: 90, left: 60},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#bar_chart")
            .append("svg")
            .attr("class", "svg-style")
            //.attr("width", width + margin.left + margin.right)
            //.attr("height", height + margin.top + margin.bottom)
            .append("g");
            //.attr("transform",
              //    "translate(" + margin.left + "," + margin.top + ")")


// initialize variables of sliders
var morningValue = 0, middayValue = 0, afternoonValue = 0, eveningValue = 0;

// Parse the Data
d3.csv("static/data/XYZ.csv", function(data) {

    // Add X axis
    var x = d3.scaleBand()
                .range([ 0, width ])
                .domain(data.map(function(d) { return d.Period; }))
                .padding(0.7);

    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "translate(-10,0)rotate(-45)")
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
        .attr("width", x.bandwidth())
        .attr("height", function(d) { return height - y(d.Value); })
        .attr("fill", "#69b3a2")
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("class", "baseline-bar")

    // A function that update the chart when slider is moved?
        function updateChart(morningValue, middayValue, afternoonValue, eveningValue) {
            //TODO optimize this
            data[0].Value = morningValue;
            data[1].Value = middayValue;
            data[2].Value = afternoonValue;
            data[3].Value = eveningValue;

            svg.selectAll(".baseline-bar")
                .attr("fill", "#D3D3D3");

            svg.selectAll(".new-bar").remove();
            
            svg.selectAll("bar")
                .data(data)
                .enter()
                .append("rect")
                .attr("x", function(d) { return x(d.Period); })
                .attr("y", function(d) { return y(d.Value); })
                .attr("width", x.bandwidth())
                .attr("height", function(d) { return height - y(d.Value); })
                .attr("fill", "#69b3a2")
                .attr("rx", 10)
                .attr("ry", 10)
                .attr("class", "new-bar")
        }

    // Listen to the sliders
    //morning
    d3.select("#morningSlider").on("change", function(d){
        morningValue = this.value
        })
    //midday
    d3.select("#middaySlider").on("change", function(d){
        middayValue = this.value
        })
    //afternoon
    d3.select("#afternoonSlider").on("change", function(d){
        afternoonValue = this.value
        })
    //evening
    d3.select("#eveningSlider").on("change", function(d){
        eveningValue = this.value
        })

    // Listen to the submit button
    d3.select("#submit-btn").on("click", function(d){
        updateChart(morningValue, middayValue, afternoonValue, eveningValue)
        })
});