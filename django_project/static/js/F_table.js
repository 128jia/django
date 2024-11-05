(async () => { 
    // 从后端获取数据
    
    const response = await fetch('/finance/get_stock_data/');
    const data = await response.json();
    // 将数据转换为 Highcharts 所需的格式
    const aaplData = data.AAPL.map(item => [
        new Date(item.Date).getTime(), // 将日期转换为时间戳
        item.Close // 获取 AAPL 的关闭价格
    ]);
    const profittable = data.profits;
    console.log("profit::::",profittable);
    const gldData = data.GLD.map(item => [
        new Date(item.Date).getTime(), // 将日期转换为时间戳
        item.Close // 获取 GLD 的关闭价格
    ]);
    const spreadData = data.spread.map(item => [new Date(item.date).getTime(), item.value]);
    const meanData = data.rolling_mean.map(item => [new Date(item.date).getTime(), item.value]);
    const upperStdData = data.rolling_mean.map((item, index) => [new Date(item.date).getTime(), item.value + 2 * data.rolling_std[index].value]);
    const lowerStdData = data.rolling_mean.map((item, index) => [new Date(item.date).getTime(), item.value - 2 * data.rolling_std[index].value]);
    
    console.log("spreaddata",spreadData)
    
    console.log("meandata",meanData)
    
    
    console.log("lowerstd",lowerStdData)
    const longPositions1 = data.open_positions.filter(pos => pos.type === 'long').map(pos => [new Date(pos.date).getTime(), pos.gld_price]);
    const shortPositions1 = data.open_positions.filter(pos => pos.type === 'short').map(pos => [new Date(pos.date).getTime(), pos.gld_price]);

    const longCloses1= data.close_positions.filter(pos => pos.type === 'long').map(pos => [new Date(pos.close.date).getTime(), pos.close.gld_price]);
    const shortCloses1 = data.close_positions.filter(pos => pos.type === 'short').map(pos => [new Date(pos.close.date).getTime(), pos.close.gld_price]);
    
    const longPositions = data.open_positions.filter(pos => pos.type === 'long').map(pos => {
        const spreadValue = spreadData.find(d => d[0] === new Date(pos.date).getTime());
        return [new Date(pos.date).getTime(), spreadValue ? spreadValue[1] : null];
    });

    const shortPositions = data.open_positions.filter(pos => pos.type === 'short').map(pos => {
        const spreadValue = spreadData.find(d => d[0] === new Date(pos.date).getTime());
        return [new Date(pos.date).getTime(), spreadValue ? spreadValue[1] : null];
    });

    const longCloses = data.close_positions.filter(pos => pos.type === 'long').map(pos => {
        const spreadValue = spreadData.find(d => d[0] === new Date(pos.close.date).getTime());
        return [new Date(pos.close.date).getTime(), spreadValue ? spreadValue[1] : null];
    });

    const shortCloses = data.close_positions.filter(pos => pos.type === 'short').map(pos => {
        const spreadValue = spreadData.find(d => d[0] === new Date(pos.close.date).getTime());
        return [new Date(pos.close.date).getTime(), spreadValue ? spreadValue[1] : null];
    });
    const dailyProfits = data.daily_profits;
    // Chart1:Price Comparison
    Highcharts.stockChart('container', {
        rangeSelector: {
            selected: 1
        },

        title: {
            text: 'AAPL and GLD Stock Prices'
        },
        xAxis: {
            plotLines: [] // 初始化空的 plotLines 数组
        },

        series: [{
            name: 'AAPL',
            data: aaplData,
            tooltip: {
                valueDecimals: 2
            }
        }, {
            name: 'GLD',
            data: gldData,
            tooltip: {
                valueDecimals: 2
            }
        }, {
            type: 'scatter',
            name: 'Long Open',
            data: longPositions1,
            marker: {
                symbol: 'triangle',
                fillColor: 'green',
                lineColor: 'green',
                lineWidth: 10
            }
        }, {
            type: 'scatter',
            name: 'Short Open',
            data: shortPositions1,
            marker: {
                symbol: 'triangle-down',
                fillColor: 'red',
                lineColor: 'red',
                lineWidth: 10
            }
        }, {
            type: 'scatter',
            name: 'Long Close',
            data: longCloses1,
            marker: {
                symbol: 'circle',
                fillColor: 'green',
                lineColor: 'green',
                lineWidth: 10
            }
        }, {
            type: 'scatter',
            name: 'Short Close',
            data: shortCloses1,
            marker: {
                symbol: 'circle',
                fillColor: 'red',
                lineColor: 'red',
                lineWidth: 10
            }
        }]
    });
    //Chart2:Spread 
    Highcharts.stockChart('container2', {
        title: {
            text: 'AAPL and GLD Spread'
        },
        series: [{
            name: 'Spread',
            data: spreadData,
            color: 'black',
            lineWidth: 1
        }, {
            name: 'Rolling Mean',
            data: meanData,
            color: 'orange',
            dashStyle: 'ShortDot'
        }, {
            name: '+2 Std',
            data: upperStdData,
            color: 'red',
            dashStyle: 'ShortDashDotDot'
        }, {
            name: '-2 Std',
            data: lowerStdData,
            color: 'green',
            dashStyle: 'ShortDashDotDot'
        }, {
            type: 'scatter',
            name: 'Long Open',
            data: longPositions,
            marker: {
                symbol: 'triangle',
                fillColor: 'green',
                lineColor: 'green',
                lineWidth: 2,
                //name: "buy",
                enabled: true,
                radius: 6,
          },
            visibility: true,
        
        }, {
            type: 'scatter',
            name: 'Short Open',
            data: shortPositions,
            marker: {
                symbol: 'triangle-down',
                fillColor: 'red',
                lineColor: 'red',
                lineWidth: 2,
                //name: "sell",
                enabled: true,
                radius: 6,
          },
          visibility: true,
        }, {
            type: 'scatter',
            name: 'Long Close',
            data: longCloses,
            marker: {
                symbol: 'circle',
                fillColor: 'green',
                lineColor: 'green',
                lineWidth: 2,
                //name: "sell",
                enabled: true,
                radius: 6,
          },
          visibility: true,
        }, {
            type: 'scatter',
            name: 'Short Close',
            data: shortCloses,
            marker: {
                symbol: 'circle',
                fillColor: 'red',
                lineColor: 'red',
                lineWidth: 2,
                //name: "sell",
                enabled: true,
                radius: 6,
          },
          visibility: true,
        }]
    });
    const tableData = data.close_positions.map(pos => [
        pos.type,
        pos.open.date,
        pos.open.aapl_price,
        pos.open.gld_price,
        pos.close.date,
        pos.close.aapl_price,
        pos.close.gld_price
    ]);

    $('#positions-table').DataTable({
        data: tableData,
        columns: [
            { title: "Type" },
            { title: "Open Date" },
            { title: "Open AAPL Price" },
            { title: "Open GLD Price" },
            { title: "Close Date" },
            { title: "Close AAPL Price" },
            { title: "Close GLD Price" }
        ]
    });
    // profitTable
    const tableData2 = data.profits.map(pos => [
        pos.type,
        pos.date,
        pos.appl_action,
        pos.aapl_price,
        pos.gld_action,
        pos.gld_price,
        pos.profit_percent
    ]);
    
    $('#profitTable').DataTable({
        data: tableData2,
        columns: [
            { title: "type" },
            { title: "Date" },
            { title: "AAPL Action" },
            { title: "AAPL Price" },
            { title: "GLD Action" },
            { title: "GLD Price" },
            { title: "Profit Percentage" }
            
        ],
        createdRow: function(row, data, dataIndex) {
            // 使用奇偶判断来交替行颜色
            if (dataIndex % 2 === 0) {
                $(row).addClass('green-column');  // 偶数行绿色
            } else {
                $(row).addClass('red-column');    // 奇数行红色
            }
        }
    });
    
    
    console.log("profit:",dailyProfits);
    Highcharts.chart('profitContainer', {
        title: {
            text: 'Daily Profit Percentage'
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'Profit Percentage (%)'
            }
        },
        series: [{
            name: 'Profit Percentage',
            data: dailyProfits.map(point => [new Date(point.date).getTime(), point.profit_percent]),
            tooltip: {
                valueSuffix: '%'
            },
            connectNulls: true
        }]
    });

})();
// $(document).ready(function() {
//     // 发出 AJAX 请求获取数据
//     $.ajax({
//         url: '/your-django-url/',  // 替换为你的Django URL
//         method: 'GET',
//         success: function(response) {
//             // 初始化 DataTable
//             $('#profitTable').DataTable({
//                 data: response.profits,  // 从response中获取 profits 数据
//                 columns: [
//                     { data: 'date' },          // 显示 date
//                     { data: 'appl_action' },   // 显示 AAPL Action (BUY/SELL)
//                     { data: 'aapl_price' },    // 显示 AAPL Price
//                     { data: 'gld_action' },    // 显示 GLD Action (BUY/SELL)
//                     { data: 'gld_price' },     // 显示 GLD Price
//                     { data: 'profit_percent',  // 显示 Profit Percentage
//                       render: function(data, type, row) {
//                           return data.toFixed(2) + '%';  // 四舍五入到小数点后两位并加上百分号
//                       }
//                     }
//                 ]
//             });
//         },
//         error: function(xhr, status, error) {
//             console.log('Error fetching data:', error);
//         }
//     });
// });





function addVerticalLinesForScatter(seriesData) {
    const chart = Highcharts.charts[0]; // 获取图表实例
    seriesData.forEach(series => {
        if (series.type === 'scatter') {
            series.data.forEach(point => {
                chart.xAxis[0].addPlotLine({
                    value: point[0], // 使用点的X值
                    color: 'gray',
                    dashStyle: 'Dash', // 虚线样式
                    width: 1,
                    label: {
                        text: 'Assist Line',
                        align: 'left',
                        style: {
                            color: 'gray'
                        }
                    }
                });
            });
        }
    });
}

// 获取所有散点图系列的数据
const scatterSeries = Highcharts.charts[0].series.filter(s => s.type === 'scatter');

// 为每个散点数据增加垂直虚线
scatterSeries.forEach(series => {
    addVerticalLinesForScatter(series.points);
});