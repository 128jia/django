$.ajaxSetup({
    headers: { 'X-CSRFToken': csrf_token },
    type: 'POST',
});

$(document).ready(function() {
    $('#data-table').DataTable({
        searching: false,  // Disable the search box
        paging: false,      // Enable pagination
        info: false,        // Show table information (e.g., "Showing 1 to 10 of 50 entries")
        ordering: true,     // Enable column ordering
        columns: [
            { data: 'wormbase_id' },
            { data: 'status' },
            { data: 'sequence_name' },
            { data: 'gene_name' },
            { data: 'other_names' },
            { data: 'transcript' },
            { data: 'type' },
            { data: 'count' }
        ]
    });

    $('#submit').click(function() {
        console.log($('#ajax').serialize());
        $.ajax({
            url: '/w293/search/',
            type: 'POST',
            data: $('#ajax').serialize(),  
            //dataType: 'json',
            success: function(response) {
                data =response.data
                var query = response.query.trim();
                const dup_number = response.dup_number;
                if (response.warning) {
                    alert(response.warning);
                }else {
                    console.log(response.data);
                }
                if (dup_number === 1) {
                    let tableRows = data.map(row => `
                        <tr>
                            <td><a href="https://wormbase.org/species/c_elegans/gene/${row.wormbase_id}#0-9f-10" target="_blank">${row.wormbase_id}</a></td>
                            <td>${row.status}</td>
                            <td>${row.sequence_name}</td>
                            <td>${row.gene_name}</td>
                            <td>${row.other_names}</td>
                            <td><a href="#" class="transcript-link" data-id="${row.transcript}">${row.transcript}</a></td>
                            <td>${row.type}</td>
                            <td>${row.count}</td>
                        </tr>
                    `).join('');
    
                    const modalHtml = `
                        <div id="wormbaseModal" class="modal">
                            <div class="modal-content">
                                <span class="close">&times;</span>
                                <h2>Wormbase IDs 詳細資料</h2>
                                <table class="modal-table">
                                    <thead>
                                        <tr>
                                            <th>Wormbase ID</th>
                                            <th>Status</th>
                                            <th>Sequence Name</th>
                                            <th>Gene Name</th>
                                            <th>Other Names</th>
                                            <th>Transcript</th>
                                            <th>Type</th>
                                            <th>Count</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${tableRows}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;
                    
                    $('body').append(modalHtml);
                    
                    // Modal CSS 和 JavaScript 開關功能
                    $('.modal').css({
                        display: 'block',
                        position: 'fixed',
                        zIndex: 1,
                        left: 0,
                        top: 0,
                        width: '100%',
                        height: '100%',
                        backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    });
                    $('.modal-content').css({
                        backgroundColor: '#fefefe',
                        margin: 'auto',
                        padding: '20px',
                        border: '1px solid #888',
                        width: '80%',
                        position: 'relative',
                        top: '50%',
                        transform: 'translateY(-50%)'
                    });
                    $('.modal-table').css({
                        width: '100%',
                        borderCollapse: 'collapse',
                    });
                    $('.modal-table th, .modal-table td').css({
                        border: '1px solid #ddd',
                        padding: '8px',
                        textAlign: 'left',
                    });
                    $('.modal-table th').css({
                        backgroundColor: '#f2f2f2',
                        fontWeight: 'bold',
                    });
                    $('.close').css({
                        color: '#aaa',
                        float: 'right',
                        fontSize: '28px',
                        fontWeight: 'bold',
                    });
                    $('.close').click(function() {
                        $('#wormbaseModal').remove();
                    });
                    $(window).click(function(event) {
                        if (event.target.id === 'wormbaseModal') {
                            $('#wormbaseModal').remove();
                        }
                    });
                }
                var table = $('#data-table').DataTable();
                table.clear();
                data = data.map(function(row) {
                    row.wormbase_id = `<a href="https://wormbase.org/species/c_elegans/gene/${row.wormbase_id}#0-9f-10" target="_blank">${row.wormbase_id}</a>`;
                    row.transcript = `<a href="#" class="transcript-link" data-id="${row.transcript}">${row.transcript}</a>`;
                    
                    return row;
                });
                table.rows.add(data);  // Adds the JSON data to the table
                table.draw();
                $('#data-table tbody tr').each(function() {
                    // 获取需要高亮的列
                    var wormbaseIdCell = $(this).find('td:nth-child(1)');   // Wormbase ID 列 (第1列)
                    var sequenceNameCell = $(this).find('td:nth-child(3)'); // Sequence Name 列 (第3列)
                    var geneNameCell = $(this).find('td:nth-child(4)');     // Gene Name 列 (第4列)
                    var otherNamesCell = $(this).find('td:nth-child(5)');   // Other Names 列 (第5列)
                    var transcriptCell = $(this).find('td:nth-child(6)');   // Transcript 列 (第6列)
    
                    // 将需要检查的列与关键字匹配
                    var columnsToCheck = [
                        wormbaseIdCell, sequenceNameCell, geneNameCell, otherNamesCell, transcriptCell
                    ];
    
                    columnsToCheck.forEach(function(cell) {
                        var cellText = cell.text().trim().toLowerCase(); 
                        if (cellText === query.toLowerCase()) {
                            cell.css('background-color', 'yellow');  // 设置反白效果
                        } else {
                            cell.css('background-color', '');  // 清除之前的反白效果
                        }
                    });
                });
            },
            error: function(xhr, status, error) {
                console.error('搜索请求失败:', error);
            }
        });
    });
    $(document).on('click', '.transcript-link', function(e) {
        $('#loading').show();
        e.preventDefault(); // 防止默認行為（如導航到 href）
        $('#wormbaseModal').remove();
        $('#splicedText').empty();
        $('#unsplicedText').empty();
        $('#protein').empty();
        $('#chart_m0, #chart_m1, #chart_m2').empty();
        $('#chart1, #chart2, #chart3').empty();
        var transcriptId = $(this).data('id');
        $('#transcript-id-display').text("Transcript ID: " + transcriptId);
        
        $("#name").html('<div class="alert alert-warning">' +'Transcript ID:'+ transcriptId + '</div>');
        var spliced_table = $('#splicedTable').DataTable({
            searching: false,  
            destroy: true,
            paging: false,      
            info: false,        
            ordering: true, 
            columns: [
                { data: 'Name' },
                { data: 'Start' },
                { data: 'End' },
                { data: 'Length' },
            ]    
        });
        var unspliced_table = $('#unsplicedTable').DataTable({
            searching: false, 
            destroy: true, 
            paging: false,      
            info: false,        
            ordering: true, 
            
            columns: [
                { data: 'Name' },
                { data: 'Start' },
                { data: 'End' },
                { data: 'Length' },
            ]    
        });
        //ToolTip*
        var tooltip = d3.select("body").append("div")
        .attr("id", "tooltip")
        .style("position", "absolute")
        .style("opacity", 0)
        .style("background-color", "lightgray")
        .style("padding", "5px")
        .style("border-radius", "3px")
        .style("pointer-events", "none");
        // 發送 AJAX 請求到後端
        $.ajax({
            url: '/w293/ajax_data2/', // 後端 API URL
            type: 'POST',
            data: { transcript_id: transcriptId },
            success: function(data) {
                //rna sequnence
                $('#loading').hide();
                var splicedText = data.spliced_RNA;
                var unsplicedText = data.unspliced_RNA;
                var protein =data.protein
                //{name,start,end,length}
                var splicedRegions = data.spliced;
                var unsplicedRegions = data.unspliced;
                //bedgraph
                var data_m0 = data['bedgraph']['m0'];
                var data_m1 = data['bedgraph']['m1'];
                var data_m2 = data['bedgraph']['m2'];
                
                unspliced_table.clear().rows.add(unsplicedRegions).draw();
                spliced_table.clear().rows.add(splicedRegions).draw();
                
                // 将格式化并着色的 RNA 序列插入 HTML
                document.getElementById('splicedText').innerHTML = colorRNASequence(splicedText, splicedRegions);
                document.getElementById('unsplicedText').innerHTML = colorRNASequence(unsplicedText, unsplicedRegions);
                document.getElementById('protein').innerHTML = formatRNASequence(protein);
                //-------------------------------------------------------//
                //                    d3                                 //
                //-------------------------------------------------------//
                var utr_cds_data = splicedRegions.filter(function(d) {
                    return ['five_prime_UTR', 'three_prime_UTR', 'CDS'].includes(d.Name);
                });
                
                var exon_data = splicedRegions.filter(function(d) {
                    return d.Name.startsWith('Exon');
                });
                
                //console.log("utr_cds:",utr_cds_data);
                //console.log("exon:",exon_data);
                ///////////////////////////D3/////////////////////////////
                // 設定圖表的寬度和高度
                //var group1 = splicedRegions.filter(d => d.Name === 'five_prime_UTR' || d.Name === 'three_prime_UTR' || d.Name === 'CDS');
                //var group2 = splicedRegions.filter(d => d.Name.startsWith('Exon'));
                //createBarChart("#chart3", data_m0, "Chart 3 - m0"); 最後 一項可以顯示標題
                createBarChart("#chart_m0", data_m0);
                createBarChart("#chart_m1", data_m1);
                createBarChart("#chart_m2", data_m2);
                // 設定圖表的寬度、高度和內邊距
                var width = 1000, height = 50, margin = {top: 20, right: 30, bottom: 40, left: 40};
                // 創建 x 軸尺度 (共用)
                var x = d3.scaleLinear()
                    .domain([0, d3.max(splicedRegions, function(d) { return d.End; })])
                    .range([0, width]);

                // 顏色設定
                var color1 = d3.scaleOrdinal()
                    .domain(['five_prime_UTR', 'three_prime_UTR', 'CDS'])
                    .range(['gray', 'gray', 'green']);
                console.log("cds:",utr_cds_data['CDS']);
             

                // 創建 SVG 及群組元素 chart1
                var svg1 = d3.select("#chart1")
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                var svg2 = d3.select("#chart2")
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
                // 交替顏色設定
                var color2 = d3.scaleOrdinal()
                .domain(exon_data.map(function(d, i) { return i % 2; }))
                .range(['orange', 'yellow']);
                
                // 畫第一個圖表（UTR 和 CDS，段落分布，顏色區分）
                svg1.selectAll(".bar")
                .data(utr_cds_data)
                .enter().append("rect")
                .attr("class", "bar")
                .attr("x", function(d) { return x(d.Start); })
                .attr("y", 0)
                .attr("width", function(d) { return x(d.Length); })
                .attr("height", height)
                .attr("fill", function(d) { return color1(d.Name); })
                .attr("stroke", "white")
                .attr("stroke-width", 2)
                .on("mouseover", handleMouseOver)   // Show tooltip on mouseover
                .on("mousemove", function(event, d) {  // Update tooltip position on mousemove
                    tooltip.style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 20) + "px");
                })
                .on("mouseout", handleMouseOut); 
                

                
                

                // 畫第二個圖表（Exon，交替顏色）
                svg2.selectAll(".bar")
                .data(exon_data)
                .enter().append("rect")
                .attr("class", "bar")
                .attr("x", function(d) { return x(d.Start); })
                .attr("y", 0)
                .attr("width", function(d) { return x(d.Length); })
                .attr("height", height)
                .attr("fill", function(d, i) { return color2(i % 2); })
                .attr("stroke", "white")
                .attr("stroke-width", 2) 
                .on("mouseover", handleMouseOver)   // Show tooltip on mouseover
                .on("mousemove", function(event, d) {  // Update tooltip position on mousemove
                    tooltip.style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 20) + "px");
                })
                .on("mouseout", handleMouseOut);  // Hide tooltip on mouseout
                
                // 加入 x 軸
                svg2.append("g")
                    .attr("class", "x-axis")
                    .attr("transform", "translate(0," + height + ")")
                    .call(d3.axisBottom(x));
                function handleMouseOver(event, d) {
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", 0.9);  // Show tooltip
                    tooltip.html("Name: " + d.Name + "<br>Start: " + d.Start + "<br>End: " + d.End)
                        .style("left", (event.pageX + 10) + "px")  // Position tooltip near the mouse
                        .style("top", (event.pageY - 20) + "px");
                }
                
                // Function to handle mouse out and hide tooltip
                function handleMouseOut(event, d) {
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", 0);  // Hide tooltip
                }
                
            
            },
            error: function(xhr, status, error) {
                console.error('Error executing script:', error);
            }
        });
        


    });
});
function formatRNASequence(sequence) {
    let formattedText = '';
    for (let i = 0; i < sequence.length; i++) {
        if (i % 50 === 0) {
            formattedText += `<span class="line-number">${i + 1}</span> `; // 顯示行號
        }
        formattedText += `<span>${sequence[i]}</span>`;
        if ((i + 1) % 10 === 0) {
            formattedText += ' '; // 每 10 個字母空一格
        }
        if ((i + 1) % 50 === 0) {
            formattedText += '<br>'; // 每 50 個字母換行
        }
    }
    return formattedText;
}

const colors = {
    'five_prime_UTR': '#E0E0E0',   // 浅红色
    'three_prime_UTR': '#E0E0E0',  // 浅蓝色
    'EXON_ORANGE': '#FFBB77',      // 橙色
    'EXON_YELLOW': '#FFE153'       // 黄色
};
const exonColors = [ '#FFE153','#f07b07']; // 黃、橘
let exonIndex = 0; // 用於記錄當前使用的顏色索引

function getColorForPosition(position, regions) {
    let color = '#FFFFFF';  // 默认白色
    regions.forEach(region => {
        if (position >= region.Start && position <= region.End) {
            if (region.Name === 'five_prime_UTR' || region.Name === 'three_prime_UTR') {
                color = colors[region.Name];
            } else if (region.Name.startsWith('Exon') && color === '#FFFFFF') {
                color = exonColors[exonIndex % 2];
            }
        }
    });
    return color;
}

// 格式化并着色 RNA 序列
function colorRNASequence(sequence, regions) {
    let coloredText = '';
    let lastExon = null;

    for (let i = 0; i < sequence.length; i++) {
        if (i % 50 === 0) {
            coloredText += `<span class="line-number">${i + 1}</span> `; // 顯示行號
        }
        let position = i + 1;  // 序列从1开始
        let currentExon = null;

        regions.forEach(region => {
            if (position >= region.Start && position <= region.End && region.Name.startsWith('Exon')) {
                currentExon = region;
            }
        });

        if (currentExon && currentExon !== lastExon) {
            exonIndex++; // 切換顏色
            lastExon = currentExon;
        }

        let charColor = getColorForPosition(position, regions);
        coloredText += `<span style="background-color: ${charColor};">${sequence[i]}</span>`;
        
        if ((i + 1) % 10 === 0) {
            coloredText += ' ';  // 每10个字母空一格
        }
        if ((i + 1) % 50 === 0) {
            coloredText += '<br>';  // 每50个字母换行
        }
    }
    return coloredText;
}
function createBarChart(selector, data, title) { 
    var width = 2000, 
        height = 200, 
        margin = {top: 20, right: 30, bottom: 40, left: 40};

    // 手動設定 X 軸的 domain 範圍
    var x = d3.scaleLinear()
        .domain([0, d3.max(data, d => 3000)])  // 0 到最大 end_pos
        .range([0, width]);

    // Y 軸比例尺 (固定範圍 0 到 50)
    var y = d3.scaleLinear()
        .domain([0, 50])
        .range([height, 0]);

    // 建立 SVG 容器
    var svg = d3.select(selector)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // 繪製長條
    svg.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d.init_pos))
        .attr("y", d => y(d.evenly_rc))
        .attr("width", d => x(d.end_pos) - x(d.init_pos))
        .attr("height", d => height - y(d.evenly_rc))
        .attr("fill", "darkblue")
        .on("mouseover", handleMouseOver)
        .on("mousemove", handleMouseMove)
        .on("mouseout", handleMouseOut);

    // X 軸
    svg.append("g")
        .attr("transform", `translate(0,${height})`)  // 修正這行的 `translate` 語法
        .call(d3.axisBottom(x).ticks(10));

    // Y 軸
    svg.append("g")
        .call(d3.axisLeft(y));

    // 標題
    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 0 - (margin.top / 2))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("text-decoration", "underline")
        .text(title);

    

    function handleMouseOver(event, d) { 
        tooltip.transition().duration(200).style("opacity", .9); 
        tooltip.html("Evenly RC: " + d.evenly_rc + "<br/>Start: " + d.init_pos + "<br/>End: " + d.end_pos)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 20) + "px");
    }

    function handleMouseMove(event, d) { 
        tooltip.style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 20) + "px");
    }

    function handleMouseOut(event, d) { 
        tooltip.transition().duration(500).style("opacity", 0);
    }
}