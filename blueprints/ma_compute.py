class MA_Compute:

    #计算5日均线
    def ma5(self, stock_data):
        return stock_data.rolling(window=5).mean()

    #计算10日均线
    def ma10(self, stock_data):
        return stock_data.rolling(window=10).mean()

    # 计算20日均线
    def ma20(self, stock_data):
        return stock_data.rolling(window=20).mean()

    # 计算60日均线
    def ma60(self, stock_data):
        return stock_data.rolling(window=60).mean()