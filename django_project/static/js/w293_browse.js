$.ajaxSetup({
    headers: { 'X-CSRFToken': csrf_token },
    type: 'POST',
});

$(document).ready(function() {
    var Browse_table = $('#resultTable').DataTable({
        searching: true,  // 启用搜索框
        paging: true,     // 启用分页
        pageLength: 50,   // 每页显示10条记录
        info: true,       // 显示表格信息 (例如 "Showing 1 to 10 of 50 entries")
        ordering: false,  // 禁用列排序
        processing: true, // 显示加载进度条
        serverSide: false, // 关闭服务端处理模式 // 启用服务端处理模式
        ajax: {
            url: '/w293/ajax/',  // 后端处理 URL
            type: 'POST',
            data: function(d) {
                // 将表单中的数据序列化并发送
                return $('#browseform').serialize();
            },
            dataSrc: function(response) {
                console.log("搜索成功，收到的数据:", response);
                return response.data;  // 返回表格需要显示的数据
            }
        },
        columns: [
            { data: 'wormbase_id' },
            { data: 'sequence_name' },
            { data: 'gene_name' },
            { data: 'other_names' },
            { data: 'transcript' },
            { data: 'status' },
            { data: 'type' },
            { data: 'count' }
        ]
    });
    $('#submit').click(function(e) {
        e.preventDefault();  
        Browse_table.ajax.reload();
        
    });
});    
