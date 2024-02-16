console.log("This file is loaded from sts app....!");
$(document).ready(function() {
    const ctxPredictedRatio = document.getElementById('predictedRatioChart');

    new Chart(
      ctxPredictedRatio,{
        type: 'bar',
        options: {
          indexAxis: 'y',
          scales: {
            x: {
              stacked: true
            },
            y: {
              stacked: true
            }
          },
          plugins: {
            legend: {
              display: true
            }
          },
        },

        data: {
          labels: ["2015", "2014", "2013", "2012", "2011"],

          datasets: [{
            data: [727, 589, 537, 543, 574],
            backgroundColor: "rgba(63,103,126,1)",
            hoverBackgroundColor: "rgba(50,90,100,1)"
          },{
            data: [238, 553, 746, 884, 903],
            backgroundColor: "rgba(163,103,126,1)",
            hoverBackgroundColor: "rgba(140,85,100,1)"
          },{
            data: [1238, 553, 746, 884, 903],
            backgroundColor: "rgba(63,203,226,1)",
            hoverBackgroundColor: "rgba(46,185,235,1)"
          }]
        }
      }
    );

});