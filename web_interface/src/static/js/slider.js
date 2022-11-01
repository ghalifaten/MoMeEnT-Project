var ticks=["Never","Often","Usually","Always"];

var sliderStep = d3
    .sliderLeft()
    .min(0)
    .max(4)
	.step(1)
    .height(150)
    .ticks(4)
    .tickFormat(function(d,i){return ticks[i]})
    .default(0)
    .handle(
        d3.symbol()
          .type(d3.symbolCircle)
          .size(200)
      )
      .fill("#206595")
      .on('onchange', val => {
        d3.select('g.parameter-value text').text(ticks[val])
        document.getElementById("value-step").value=ticks[val]
      });

var gSimple = d3
    .select('div#slider-step')
    .append('svg')
    .attr('width', 100)
    .attr('height', 200)
    .append('g')
    .attr('transform', 'translate(125,0)');

gSimple.call(sliderStep);

