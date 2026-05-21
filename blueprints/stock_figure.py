import tushare as ts
import plotly.graph_objects as go
from datetime import timedelta, datetime
import pandas as pd
from flask import current_app
from plotly.subplots import make_subplots
from .ma_compute import MA_Compute
import os


def draw_stock_figure(stock_code):
    # 初始化ts接口
    pro = ts.pro_api()

    # 隐藏非交易日
    current_dir = os.path.dirname(os.path.abspath(__file__))
    holidays_file = os.path.join(current_dir, 'holidays.csv')
    
    try:
        # 添加错误处理
        data = pd.read_csv(holidays_file)
        holidays = data['Date'].tolist()
    except Exception as e:
        print(f"读取holidays.csv出错: {e}")
        print(f"当前路径: {current_dir}")
        print(f"尝试读取的文件: {holidays_file}")
        raise

    stock_code = stock_code
    # 用股票代码，开始日期截止日期来获取股票数据
    df = pro.daily(ts_code=stock_code, start_date='20100101', end_date='')
    # 反转数据
    df = df.iloc[::-1]
    # 将日期列转换为datetime格式
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    # 计算涨跌状态并设置颜色
    df['color'] = df.apply(lambda row: 'red' if row['close'] > row['open'] else 'green', axis=1)


    mc = MA_Compute()  # 计算移动平均线

    # 创建一个二行一列图表
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,  # 共享 x 轴
        vertical_spacing=0.1,  # 上下图之间的间距
        row_heights=[0.7, 0.3],  # 上下图的高度比例
        subplot_titles=["K线图", "成交量"]  # 子图标题
    )

    # 生成蜡烛图到第一行
    fig.add_trace(
        go.Candlestick(
            x=df['trade_date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="Stock Price",
            increasing_line_color='red',
            decreasing_line_color='green',
        ),
        row=1, col=1,
    )

    # 生成MA5移动平均线到第一行
    fig.add_trace(
        go.Scatter(
            x=df['trade_date'],
            y=mc.ma5(df['close']),  # 将计算好的ma5值传入y轴
            name='MA5',
            mode='lines',
            line=dict(color='blue')
        ),
        row=1, col=1
    )

    # 生成MA10移动平均线到第一行
    fig.add_trace(
        go.Scatter(
            x=df['trade_date'],
            y=mc.ma10(df['close']),  # 将计算好的ma10值传入y轴
            name='MA10',
            mode='lines',
            line=dict(color='#fff143')
        ),
        row=1, col=1
    )

    # 生成MA20移动平均线到第一行
    fig.add_trace(
        go.Scatter(
            x=df['trade_date'],
            y=mc.ma20(df['close']),  # 将计算好的ma20值传入y轴
            name='MA20',
            mode='lines',
            line=dict(color='magenta')
        ),
        row=1, col=1
    )

    # 生成MA60移动平均线到第一行
    fig.add_trace(
        go.Scatter(
            x=df['trade_date'],
            y=mc.ma60(df['close']),  # 将计算好的ma60值传入y轴
            name='MA60',
            mode='lines',
            line=dict(color='green')
        ),
        row=1, col=1
    )

    # 生成成交量的条形图到第二行
    fig.add_trace(
        go.Bar(
            x=df['trade_date'],
            y=df['vol'],
            name="Volume",
            marker=dict(color=df['color']),  # 根据涨跌动态设置颜色
            opacity=0.5
        ),
        row=2, col=1
    )

    # 生成MA5移动平均线到第2行
    fig.add_trace(
        go.Scatter(
            x=df['trade_date'],
            y=mc.ma5(df['vol']),  # 将计算好的ma5值传入y轴
            name='MA5_volume',
            mode='lines',
            line=dict(color='#808080')
        ),
        row=2, col=1
    )

    # 生成MA10移动平均线到第2行
    fig.add_trace(
        go.Scatter(
            x=df['trade_date'],
            y=mc.ma10(df['vol']),  # 将计算好的ma10值传入y轴
            name='MA10_volume',
            mode='lines',
            line=dict(color='magenta')
        ),
        row=2, col=1
    )

    # 图表默认显示2个月的数据
    # 获取最近的日期
    latest_date = df['trade_date'].max()

    # 计算两个月前的日期
    two_months_ago = latest_date - timedelta(days=60)

    # 更新布局
    fig.update_layout(
        width=1500,  # 设置图表宽度
        height=800,  # 设置图表高度
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all", label="All"),
                ],
                activecolor='lightgrey',  # 活动按钮高亮颜色
                bgcolor='white',  # 按钮背景颜色
                bordercolor="black",  # 边框颜色
                borderwidth=1  # 边框宽度
            ),
            tickmode="auto",
            nticks=5,
            type='date',
            rangeslider=dict(visible=False),  # 不在主图显示缩放滑块
            rangebreaks=[
                dict(bounds=["sat", "mon"]),  # 隐藏周六、周日
                dict(values=holidays)  # 隐藏具体日期
            ],
            range=[two_months_ago, latest_date]  # 默认显示范围
        ),
        xaxis2=dict(
            tickmode="auto",
            nticks=5,
            type='date',
            rangeslider=dict(visible=True),  # 在子图 2 显示缩放滑块
            range=[two_months_ago, latest_date]  # 默认显示范围
        ),
        yaxis=dict(
            title='price',
            tickmode="auto",
            nticks=5,
            autorange=True
        ),
        yaxis2=dict(
            title='volume',
            tickmode="auto",
            nticks=5,
            autorange=True
        ),
        # template="plotly_dark",  # 图表风格
        hovermode="x unified"
    )

    # 返回图表的HTML代码
    return fig.to_html(full_html=False, include_plotlyjs=True)
    
