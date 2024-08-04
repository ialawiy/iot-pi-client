<!-- Chart.svelte -->
<script>
  import { onMount, afterUpdate, createEventDispatcher, getContext } from "svelte";
  import { readable } from "svelte/store";
  import Chart from "chart.js/auto";
  import { linear } from "svelte/easing";
  /*-------------------- Props -----------------------*/
  export let title = ''; //
  export let values = []; //
  export let keys = []; //
  export let stacks = false;
  export let yID = [];
  export let filled = false;
  export let axisYLabel = ''
  export let axisXLabel = ''
  
  export let labelss = []; //
  export let height = "200px"; //
  export let width = "250px"; //
  export let type = "line";
  export let span = "";
  export let displayX = true;

  export let displayLegend = true;
  /*-------------------- Vars -----------------------*/

  let datasets = [];
  let canvasID = Math.random();
  
  const muted = 1;
  
  // console.log("datsChart",span,title,keys,labelss,values)

  /*-------------------- Helpers -----------------------*/

	function generateHues(num) {
	  const hues = [];
	  const hueStep = 360 / num;
	  for (let i = 0; i < num; i++) {
		hues.push(i * hueStep);
	  }
	  return hues;
	}

	function getColor(hue, vibrant) {
	  return `hsl(${hue}, ${vibrant ? '100%' : '50%'}, ${vibrant ? '50%' : '80%'})`;
	}

	const hues = generateHues(values.length / 2);

  function newGradient(lineStart, lineEnd, fillStart, fillEnd) {
  return { lineStart, lineEnd, fillStart, fillEnd };
  }

  // Function to get a random key from an object
  function getRandomKey(obj) {
  const keys = Object.keys(obj);
  return keys[Math.floor(Math.random() * keys.length)];
  }
  
  
  
  const gradients = {
	"Battery Voltage": newGradient(
      "rgba(108, 117, 125, 0.9)",
      "rgba(73, 80, 87, 0.9)",
      "rgba(173, 181, 189, 0.9)",
      "rgba(134, 142, 150, 0.9)"
    ),
    "Battery Current": newGradient(
      "rgba(255, 153, 153, 0.9)",
      "rgba(255, 102, 102, 0.9)",
      "rgba(255, 204, 153, 0.9)",
      "rgba(255, 128, 0, 0.9)"
    ),
	"Battery Yesterday Voltage": newGradient(
      "rgba(108, 117, 125, 0.3)",
      "rgba(73, 80, 87, 0.3)",
      "rgba(173, 181, 189, 0.3)",
      "rgba(134, 142, 150, 0.3)"
    ),
    "Battery Yesterday Current": newGradient(
      "rgba(255, 153, 153, 0.3)",
      "rgba(255, 102, 102, 0.3)",
      "rgba(255, 204, 153, 0.3)",
      "rgba(255, 128, 0, 0.3)"
    ),
    "Solar Panel Voltage": newGradient(
      "rgba(0, 123, 255, 0.9)",
      "rgba(0, 86, 179, 0.9)",
      "rgba(102, 178, 255, 0.9)",
      "rgba(51, 153, 255, 0.9)"
    ),
    "Solar Panel Current": newGradient(
      "rgba(255, 255, 224, 0.9)",
      "rgba(255, 174, 0, 0.9)",
      "rgba(0, 193, 207, 0.9)",
      "rgba(0, 225, 136, 0.9)"
    ),
    "Solar Panel Yesterday Voltage": newGradient(
      "rgba(0, 123, 255, 0.3)",
      "rgba(0, 86, 179, 0.3)",
      "rgba(102, 178, 255, 0.3)",
      "rgba(51, 153, 255, 0.3)"
    ),
    "Solar Panel Yesterday Current": newGradient(
      "rgba(255, 255, 224, 0.3)",
      "rgba(255, 174, 0, 0.3)",
      "rgba(0, 193, 207, 0.3)",
      "rgba(0, 225, 136, 0.3)"
    ),
	"Production Power & Energy": newGradient(
      "rgba(255, 255, 224, 0.9)",
      "rgba(255, 174, 0, 0.9)",
      "rgba(0, 193, 207, 0.9)",
      "rgba(0, 225, 136, 0.9)"
    ),
    "Battery State of Charge": newGradient(
      "rgba(40, 167, 69, 0.9)",
      "rgba(33, 136, 56, 0.9)",
      "rgba(144, 238, 144, 0.9)",
      "rgba(120, 224, 143, 0.9)"
    ),
	"Battery Yesterday State of Charge": newGradient(
      "rgba(40, 167, 69, 0.3)",
      "rgba(33, 136, 56, 0.3)",
      "rgba(144, 238, 144, 0.3)",
      "rgba(120, 224, 143, 0.3)"
    ),
	"Solar Panel Temperature": newGradient(
      "rgba(255, 153, 153, 0.9)",
      "rgba(255, 102, 102, 0.9)",
      "rgba(255, 204, 153, 0.9)",
      "rgba(255, 128, 0, 0.9)"
    ),
	"Solar Panel Yesterday Temperature": newGradient(
      "rgba(255, 153, 153, 0.3)",
      "rgba(255, 102, 102, 0.3)",
      "rgba(255, 204, 153, 0.3)",
      "rgba(255, 128, 0, 0.3)"
    ),
    "Production This Month": newGradient(
      "rgba(220, 53, 69, 0.9)",
      "rgba(175, 42, 55, 0.9)",
      "rgba(255, 99, 132, 0.9)",
      "rgba(235, 77, 102, 0.9)"
    ),
	"Production Last Month": newGradient(
      "rgba(108, 117, 125, 0.9)",
      "rgba(73, 80, 87, 0.9)",
      "rgba(173, 181, 189, 0.9)",
      "rgba(134, 142, 150, 0.9)"
    ),
    // Add more gradients using the newGradient function
  };
  
  // Function to add minutes to a JavaScript Date object
	function addMinutes(date, minutes) {
	  return new Date(date.getTime() + minutes * 60000);
	}

	// Start time at 06:00
	let startTime = new Date();
	startTime.setHours(6, 0, 0, 0); // Set to 06:00

	// Generate labels for each 5-minute interval

	// Generate labels for each 5-minute interval
	let hours = [];
	for (let i = 0; i < 145; i++) {
		if (displayX) { 
	  let time = addMinutes(startTime, i * 5);
	  // Format the time as 'HH:mm' and push to hours array
	  if(i%2)
		  hours.push("")

		else	hours.push(time.toTimeString().substring(0, 5));
		}
		else hours.push("")
	}
	 
	// console.log(hours,"hours")

  const Utils = {
      // Generate an array of month names
      months: function({ count }) {
          const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
          const currentMonth = new Date().getMonth();
          let months = [];
          for (let i = 0; i < count; ++i) {
              months.push(monthNames[(currentMonth + i) % 12]);
          }
          return months;
      },
      // Generate an array of random numbers within a specified range
      numbers: function({ count, min, max }) {
          const numbers = [];
          for (let i = 0; i < count; ++i) {
              numbers.push(Math.floor(Math.random() * (max - min + 1)) + min);
          }
          return numbers;
      },
      // Create gradient for line color
      createGradient: function(ctx, chartArea, colorStops) {
          const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
          colorStops.forEach(({ position, color }) => gradient.addColorStop(position, color));
          return gradient;
      },
  };


  const generateDatasetConfig = (key, values) => {
  let name = (title+" "+key);
  if (!gradients[name]) {
    name = getRandomKey(gradients);
  }
  // console.log(gradients[name]);

  const config = {
    label: key,
    data: values.map(( y ) => y === 0 ? null : y),
    backgroundColor: function(context) {
      const chart = context.chart;
      const { ctx, chartArea } = chart;
      if (!chartArea) {
        return;
      }
      return Utils.createGradient(ctx, chartArea, [
        { position: 0, color: gradients[name].fillStart },
        { position: 1, color: gradients[name].fillEnd }
      ]);
    }
  };

  // If the chart type is 'scatter', return the config object here
  if (type === 'scatter') {
	
    return config;
  }

  // Add additional properties for other types of charts
  config.fill = filled;
  config.pointRadius = 0;
  config.borderWidth = 5;
  config.borderColor = function(context) {
    const chart = context.chart;
    const { ctx, chartArea } = chart;
    if (!chartArea) {
      return;
    }
    return Utils.createGradient(ctx, chartArea, [
      { position: 0, color: gradients[name].lineStart },
      { position: 1, color: gradients[name].lineEnd }
    ]);
  };

  return config;
};


  function createChartConfig(dataset) {
      const config = {
          type: type,
          data: dataset,
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      display: displayLegend,
                      position: 'top',
                      labels: {
                        usePointStyle: true,
                        boxWidth: 16, // Adjust the size as needed
                    }
                  },
                  tooltip: {
                      enabled: true,
                      mode: 'index',
                      intersect: false
                  }
              },
              scales: type === 'radar' ? {} : {
				  
                  y: {
					  ticks: {
						  callback : function(value, index, values) {
							return value + axisYLabel;
						  }
						},
					  type: "linear",
                      stacked: stacks,
					  display: true, // show y axis
                      grid: {
                          display: false // hide y axis gridlines
                      }                  
                  },
                  x: {
					  ticks: {
							autoSkip: true, // Default behavior
							maxTicksLimit: 13, // Adjust this number based on your need
							maxRotation: 0, // Rotate labels to 45 degrees
							
						},
                      grid: {
                          display: false // hide x axis gridlines
                      },
                      display: true // show x axis
                  }
              }
          }  

		  
      };

      // Adjustments for 'pie', 'doughnut', and similar types
      if (['pie', 'doughnut', 'polarArea'].includes(type)) {
          delete config.options.scales;
          config.options.plugins.tooltip.mode = 'point';
      }
	  	//if(['Solar Panel', 'Battery'].includes(title)) config.options.scales.y.type = 'logarithmic'
	   /* if(yID) config.options.scales = {
				  "Voltage" : {
					type: 'linear',
					position: 'left',
					grid: {
					  drawOnChartArea: false, // Only want the grid lines for one axis to show up
					},
					ticks: {
					  max: 15, // Set max to the highest voltage value
					}
					// Additional options for voltage axis
				  },
				  "Current" : {
					type: 'linear',
					position: 'right',
					// Additional options for current axis
					grid: {
					  drawOnChartArea: false, // Only want the grid lines for one axis to show up
					},
					ticks: {
					  max: 3, // Set max to the highest voltage value
					}
				  },
				  y: {
                      stacked: stacks,
                      display: true, // show y axis
                      grid: {
                          display: false // hide y axis gridlines
                      }                  
                  },
                  x: {
					  ticks: {
							autoSkip: true, // Default behavior
							maxTicksLimit: 13, // Adjust this number based on your need
							maxRotation: 0, // Rotate labels to 45 degrees
							
						},
                      grid: {
                          display: false // hide x axis gridlines
                      },
                      display: true // show x axis
                  }
	  } */

      return config;
  }

  
  /*-------------------- Fake Data -----------------------*/

  
  if (["daily"].includes(span)) type = "line";
  else if (["monthly"].includes(span)) type = "bar";
  else if (["curveIV", "soc"].includes(span)) type = "scatter";

  /* if (!labelss[0]) {
    const fakeLabel = Utils.months({count: 7});
    keys = fakeLabel;

    keys.forEach((element,index) => {
    values.push(Utils.numbers({count: 7, min: 0, max: 100}));
    datasets.push(generateDatasetConfig(element, values[index]));
    });


    // console.log(keys,values)
  } else {
    keys = [];
    if (values[0])
      for (let i = 0; i < values[0].length; ++i) {
        keys.push(i + 1);
      }
    if(['scatter'].includes(type)){
      let tempData = []
      keys.forEach((element, index) => {
      tempData.push({
        x : values[0][index],
        y : values[1][index]
      });
      // console.log("element",element)

    });

    datasets.push(generateDatasetConfig(keys, tempData));
    }
    else{
    labelss.forEach((element, index) => {
      datasets.push(generateDatasetConfig(element, values[index]));
    });}
  }
  // console.log("key,val,lab,datas", keys, values, labelss, datasets);
  */
  
  
/* if(type == "line") {
  datasets = labelss.map((key, index) => {
	  const hue = hues[Math.floor(index % (labelss.length / 2))];
	  // console.log(hue)
	  let datasetData = [];
	  // console.log("datasets",key)

	  
		// Handle other chart types
		datasetData = values[index];
	  
	  
	  // console.log(type, datasets)

	  return {
		label: key,
		yaxisID : yID.length ? yID[index] : "1",
		data: datasetData.map(( y ) => y === 0 ? null : y),
		fill: filled,
		borderColor: getColor(hue, !key.includes('esterday')),
		backgroundColor: getColor(hue, !key.includes('esterday')),
		tension: 0.1,
		// Add other properties as needed for scatter chart
	  };
	});
	// console.log("linedata",datasets)
	}
	  
else {
    keys = [];
      for (let i = 0; i < values[0].length; ++i) {
        keys.push(i + 1);
      }
    if(['scatter'].includes(type)){
      let tempData = []
      keys.forEach((element, index) => {
      tempData.push({
        x : values[0][index],
        y : values[1][index]
      });


    });
      // console.log("element",tempData)
    datasets.push(generateDatasetConfig(keys, tempData));
    }
    else{
    labelss.forEach((element, index) => {
      datasets.push(generateDatasetConfig(element, values[index]));
    });
	}
} */


  datasets = labelss.map((key, index) => {
	  
	  if(['scatter'].includes(type)){
		  keys = [];
		  for (let i = 0; i < values[0].length; ++i) {
			keys.push(i + 1);
		  }
		  let tempData = []
		  keys.forEach((element, index) => {
		  tempData.push({
			x : values[0][index],
			y : values[1][index]
		  });
		  // console.log("element",element)

		});

		return generateDatasetConfig(keys, tempData)
	  }
	  return generateDatasetConfig(key, values[index])
	  
		

	})

  /*-------------------- Auto Config -----------------------*/
  
  if(['Power Production'].includes(title)) {
      type = 'line';
      span = 'daily';
  }


  const chartData = {
      labels: keys,
      datasets: datasets
  };

  const config = createChartConfig(chartData);
  // console.log("chatconf",config)

  
  /*-------------------- Plugins -----------------------*/

  // Update the tooltip configuration to disable it
  config.options.plugins.tooltip.enabled = true;

  const crosshairPlugin = {
      id: 'custom-crosshair',
      afterDraw: function(chart) {
          const ctx = chart.ctx;
          const dataset = chart.data.datasets[0]; // Assuming you want to use the first dataset
          const meta = chart.getDatasetMeta(0); // Meta data for the first dataset
          let x = meta.data[meta.data.length - 1].x; // X position of the last point by default

          // If the chart is being hovered, update the x position to the hovered point
          if (chart.tooltip._active && chart.tooltip._active.length) {
              const activePoint = chart.tooltip._active[0];
              x = activePoint.element.x;
          }

          const topY = chart.scales.y.top;
          const bottomY = chart.scales.y.bottom;

          // draw line
          ctx.save();
          ctx.beginPath();
          ctx.moveTo(x, topY);
          ctx.lineTo(x, bottomY);
          ctx.lineWidth = 2; // Make the line thicker
          ctx.strokeStyle = 'rgba(128, 128, 128, 0.75)'; // Make the line greyer
          ctx.setLineDash([5, 5]);
          ctx.stroke();
          ctx.restore();
      }
  };

  var sunriseTime = 'June'
  var sunsetTime = 'August' 

  const sunriseSunsetShadingPlugin = {
      id: 'sunrise-sunset-shading',
      beforeDraw: function(chart, args, options) {
          const ctx = chart.ctx;
          const xaxis = chart.scales['x'];
          const yaxis = chart.scales['y'];

      
          const sunriseX = xaxis.getPixelForValue(sunriseTime);
          const sunsetX = xaxis.getPixelForValue(sunsetTime);

          ctx.save();
          ctx.fillStyle = 'rgba(0, 0, 0, 0.1)'; // Adjust the darkness of the background
          ctx.fillRect(sunriseX, yaxis.top, sunsetX - sunriseX, yaxis.bottom - yaxis.top);
          ctx.restore();
      }
  };

  // Properties specific to 'line' and 'span' charts
  if (['line'].includes(type) && ['daily'].includes(span)) {
      config.pointRadius = 0;
      config.stack = true;
      config.cubicInterpolationMode = 'monotone';
	  config.data.labels = hours
	
	  
	  
      // Register the plugin
    //  Chart.register(crosshairPlugin);
    //  Chart.register(sunriseSunsetShadingPlugin);
  }
  // Properties specific to 'line' and 'span' charts
  if (['bar'].includes(type) && ['monthly'].includes(span)) {
      config.pointRadius = 0;
      config.stack = true;
      config.cubicInterpolationMode = 'monotone';
	  let date = [];
		for (let i = 1; i < 32; i++) {
			if (displayX) { 
		  let time = addMinutes(startTime, i * 5);
		  // Format the time as 'HH:mm' and push to hours array
		  if(i% 2)
			  date.push("")

			else	date.push(i);
			}
			else date.push("")
		}
	  config.data.labels = date;
	
	  
	  
      // Register the plugin
    //  Chart.register(crosshairPlugin);
    //  Chart.register(sunriseSunsetShadingPlugin);
  }

  // Adjustments for 'pie', 'doughnut', 'polarArea', and 'radar' charts
  if (['pie', 'doughnut', 'polarArea', 'radar'].includes(type)) {
      delete config.fill;
      delete config.stack;
      delete config.cubicInterpolationMode;
  }
  
  
  // Adjustments for 'pie', 'doughnut', 'polarArea', and 'radar' charts
  if (['scatter'].includes(type)) {
      // delete config.labels;
      delete config.fill;
      delete config.stack;
      delete config.cubicInterpolationMode;
      // delete config.options.plugins;
	  
		
      config.options.scales.x.display = true;
      config.options.scales.x.position = 'bottom';      
      config.options.scales.x.type = 'linear';
      config.options.scales.y.display = true;
	  /* config.options.scales.x.scaleLabel = {
        display: true,
        labelString: 'Voltage (V)'
      }
		config.options.scales.y.scaleLabel = {
        display: true,
        labelString: 'Current (A)'
      } */
		config.options.scales.x.ticks.callback = function(value, index, values) {
          return value + 'V';
        }
		config.options.scales.y.ticks.callback = function(value, index, values) {
          return value + 'A';
        } 
      config.pointRadius = 2;
	 
  
	  
      if(!labelss[0]) {
      config.data.datasets = [{
      label: 'Scatter Dataset',
      data: [{
        x: -10,
        y: 0
      }, {
        x: 0,
        y: 10
      }, {
        x: 10,
        y: 5
      }, {
        x: 0.5,
        y: 5.5
      }],
      backgroundColor: 'rgb(255, 99, 132)'
    }]}
      // console.log("scatter",config)
    }
  
  let ctx;
  
  // Initialize Chart.js with the initial configuration
  let chart;

  $: if (chart) {
    ctx = document.getElementById(canvasID).getContext("2d");

    if (chart) {
      chart.destroy(); // Destroy the existing chart
    }

    chart = new Chart(ctx, config);
  }

  onMount(() => {
    ctx = document.getElementById(canvasID).getContext("2d");

    if (chart) {
      chart.destroy(); // Destroy the existing chart
    }

    chart = new Chart(ctx, config);
    // Programmatically change the size of the chart
    chart.canvas.parentNode.style.height = height;
    chart.canvas.parentNode.style.width = width;
  });
  

</script>
<div class="chart-container">
  <canvas id={canvasID} />
</div>

<style>
.chart-container {
	box-sizing: border-box;
    margin: 0 auto;
	width: 100%;
	height: 40vh;
  }
  

</style>