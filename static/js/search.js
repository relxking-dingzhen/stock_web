// 监听输入框的回车事件
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchStock();
    }
});

// 搜索股票函数
function searchStock() {
    const searchInput = document.getElementById('searchInput').value.trim();
    
    // 判断是否是股票代码（以.sz或.sh结尾）
    if (searchInput.endsWith('.sz') || searchInput.endsWith('.sh')) {
        // 是股票代码，跳转到股票图表页面
        window.location.href = `/stock_figure/${searchInput}`;
    } else {
        // 是关键字，跳转到搜索结果页面
        window.location.href = `/search?keyword=${encodeURIComponent(searchInput)}`;
    }
}