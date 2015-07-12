
$(function () {
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        Chart.defaults.global.responsive = true;
        var ctx = $("#tempChart").get(0).getContext("2d");
        var ctx2 = $("#humidityChart").get(0).getContext("2d");
        var myTempChart, myHumidityChart;

        $.get("/event/last", function (data){
            var event =  data.results["event"];
            var status = $('#status_color');
            if (event === "Off"){
                status.removeClass('bg-green').addClass('bg-red');
            } else if(event === "On"){
                status.removeClass('bg-red').addClass('bg-green');
            }
            $('#status_text').text(event);
        });

        $('#dashboard').addClass('active');

        function convertChartData(data) {
            var i, max, tData=[], hData=[];

            for (i = 0, max = data.results.length; i < max; i += 1) {
                var date = new Date((data.results[i]["timestamp"] * 1000));
                tData.push({x: date, y:data.results[i]["temp"]});
                hData.push({x: date, y: data.results[i]["humidity"]})
            }

            myTempChart = new Chart(ctx).Scatter(
                [{
                    label: 'Temperature',
                    strokeColor: '#F16220',
                    pointColor: '#F16220',
                    pointStrokeColor: '#fff',
                    data: tData.reverse()
                }],
                {
                    bezierCurve: true,
                    showTooltips: true,
                    useUtc: false,
                    scaleType: "date",
                    scaleLabel: "<%=value%> °C",
                    scaleOverride: true,
			        scaleStepWidth: 5,
                    scaleSteps: 7,
			        scaleStartValue: 10
                });
            myHumidityChart = new Chart(ctx2).Scatter(
                [{
                    label: 'Humidity',
                    strokeColor: '#F16220',
                    pointColor: '#F16220',
                    pointStrokeColor: '#fff',
                    data: hData.reverse()
                }],
                {
                    bezierCurve: true,
                    useUtc: false,
                    showTooltips: true,
                    scaleType: "date",
                    scaleLabel: "<%=value%>%",
                    scaleOverride: true,
			        scaleStepWidth: 5,
                    scaleSteps: 10,
			        scaleStartValue: 20
                });

            $('#humidity_text').text(data.results[0]["humidity"]);
            $('#temp_text').text(data.results[0]["temp"]);
        }
        $.get("/data", function (data) {
            convertChartData(data)
        }, "json");

        $('#btn_on').click(function () {
            $.get("/poweron", function (e) {
                $('#status_color').removeClass('bg-red').addClass('bg-green');
                $('#status_text').text("On");
            });
        });

        $('#btn_off').click(function () {
            $.get("/poweroff", function(e){
                $('#status_color').removeClass('bg-green').addClass('bg-red');
                $('#status_text').text("Off");
            });
        });

    function updatePage(data){
        var date = new Date((data["timestamp"] * 1000));
        var temperature = data["temp"];
        var humidity = data["humidity"];

        $('#humidity_text').text(humidity);
        $('#temp_text').text(temperature);

        if (myTempChart.datasets[0].points.length > 30) {
            myTempChart.datasets[0].removePoint(0);
            myHumidityChart.datasets[0].removePoint(0);
        }
        myTempChart.datasets[0].addPoint(date, temperature);
        myHumidityChart.datasets[0].addPoint(date, humidity);

        myTempChart.update();
        myHumidityChart.update();

    }
        socket.on('chart_data', function(data) {
        data = $.parseJSON(data);
        console.log(data);
        updatePage(data);
    });

    socket.on('connect', function(){
        socket.emit('register');
    });

    }
);



