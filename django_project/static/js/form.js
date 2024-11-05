//summerproject serch function
$.ajaxSetup({
    headers: { 'X-CSRFToken': csrf_token },
    type: 'POST',
});

$(document).ready(function(){
    var table = $('#myTable').DataTable({
        searching: false,  // Disable the search box
        paging: false,      // Enable pagination
        info: false,        // Show table information (e.g., "Showing 1 to 10 of 50 entries")
        ordering: true     // Enable column ordering
    });
    // 先建立svg並設定大小
    var tooltip = d3.select("body").append("div")
    .attr("id", "tooltip")
    .style("position", "absolute")
    .style("opacity", 0)
    .style("background-color", "lightgray")
    .style("padding", "5px")
    .style("border-radius", "3px")
    .style("pointer-events", "none");
    $('#submit').click(function(){
        
        $.ajax({
            url: '/web_tool/ajax_data/', 
            data: $('#ajax_form').serialize(),
            type:"POST",
            
            
            success: function(response){ 
                //$("#message").html('<div class="alert alert-warning">' + response.message + '</div>');
                table.clear();
                // spliced_table.clear();
                // unspliced_table.clear();
                
                var gene_id = response.data.gene_id || 'N/A';
                var transcript_id = response.data.transcript_id || 'N/A';
                var numbers = response.data.numbers || 'N/A';
                
                $('th').removeClass('table-primary');
                if(response.type === 'gene') {
                    $('th:contains("Gene ID")').addClass('table-primary');
                } else if(response.type === 'transcript') {
                    $('th:contains("Transcript ID")').addClass('table-primary');
                }
                var transcript_ids = Array.isArray(transcript_id) ? transcript_id : transcript_id.split(',');

                // 創建超連結 HTML
                var transcriptLinks = transcript_ids.map(function(id) {
                    return '<a href="." class="transcript-link" data-id="' + id + '">' + id + '</a>';
                }).join('<br>'); // 使用 <br> 分隔每個超連結
                
                
                table.row.add([
                    gene_id || 'N/A',
                    transcriptLinks ||'N/A',
                    numbers || 'N/A'
                ]).draw();
                   
            },
               
            error: function(xhr, status, error) {
                $("#message").html('<div class="alert alert-danger">Something went wrong: ' + error + '</div>');
            }
        });
    });
    $(document).on('click', '.transcript-link', function(e) {
        e.preventDefault(); // 防止默認行為（如導航到 href）
        
        $('#splicedText').empty();
        $('#unsplicedText').empty();
        $('#protein').empty();
        $('#chart1').empty();
        $('#chart2').empty();
        var transcriptId = $(this).data('id');
        
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
        // 發送 AJAX 請求到後端
        $.ajax({
            url: '/web_tool/ajax_data2/', // 後端 API URL
            type: 'POST',
            data: { transcript_id: transcriptId },
            success: function(data) {
                //rna sequnence
                var splicedText = data.spliced_RNA;
                var unsplicedText = data.unspliced_RNA;
                var protein =data.protein
                //{name,start,end,length}
                var splicedRegions = data.spliced;
                var unsplicedRegions = data.unspliced;
                unspliced_table.clear().rows.add(unsplicedRegions).draw();
                //重新計算畫圖用資料
                if (data.spliced && data.spliced.length > 0) {
                    
                    splicedRegions=recalculateSplicedData(splicedRegions);
                } else {
                    splicedRegions= data.specialspliced;    
                }
                spliced_table.clear().rows.add(splicedRegions).draw();
                console.log(splicedRegions);
                // 将格式化并着色的 RNA 序列插入 HTML
                document.getElementById('splicedText').innerHTML = colorRNASequence(splicedText, splicedRegions);
                document.getElementById('unsplicedText').innerHTML = colorRNASequence(unsplicedText, unsplicedRegions);
                document.getElementById('protein').innerHTML = formatRNASequence(protein);
                var utr_cds_data = splicedRegions.filter(function(d) {
                    return ['five_prime_UTR', 'three_prime_UTR', 'CDS'].includes(d.Name);
                });
                
                var exon_data = splicedRegions.filter(function(d) {
                    return d.Name.startsWith('Exon');
                });
                ///////////////////////////D3/////////////////////////////
                // 設定圖表的寬度和高度
                //var group1 = splicedRegions.filter(d => d.Name === 'five_prime_UTR' || d.Name === 'three_prime_UTR' || d.Name === 'CDS');
                //var group2 = splicedRegions.filter(d => d.Name.startsWith('Exon'));

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
                function handleMouseOver(event, d) {
                    if (d) {
                        console.log("Name: " + d.Name + ", Start: " + d.Start + ", End: " + d.End);
                    } else {
                        console.log("No data found for this segment.");
                    }
                }
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
const exonColors = [ '#FFE153','#FFBB77']; // 橘色與黃色
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
function recalculateSplicedData(splicedData) {
    //let previousEnd = splicedData[1].End;
    let previousEnd = splicedData.find(entry => entry.Name === 'Exon1')?.End;  // Exon1 的 End
    const CDS = splicedData[splicedData.length - 1];
    CDS.Start = splicedData[0].End + 1;  // 如果不符合條件，設置其他值
    
    console.log('splicedData.length',splicedData.length);
    for (let i = 2; i < splicedData.length - 2; i++) {  // 遍歷 Exon2 到 Exon7
      let currentSegment = splicedData[i];
      currentSegment.Start = previousEnd + 1;
      currentSegment.End = currentSegment.Start + currentSegment.Length - 1;
      previousEnd = currentSegment.End;
    }
  
    // 更新 three_prime_UTR 的 Start 和 End
    const threePrimeUTR = splicedData[splicedData.length - 2];
    threePrimeUTR.Start = previousEnd - threePrimeUTR.Length + 1 ;
    threePrimeUTR.End = previousEnd;
    CDS.End = threePrimeUTR.Start - 1 ;
    CDS.Length =CDS.End -CDS. Start + 1;
    return splicedData;
  }