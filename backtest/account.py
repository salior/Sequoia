# -*- encoding: UTF-8 -*-

class TradeData:
    def __init__(self,stock,op,day,price,number,tax = 0):
        self.op = op
        self.day = day
        self.price = price
        self.number = number
        self.stock = stock
        self.tax = tax

#用来账户管理,后面再算交易费用
class BaseAccount():
    # fund 当前资金
    def __init__(self,fund=100000):
        self.fund = fund 
        self.init_fund = fund
        self.position = {}              #当前持仓
        self.tax_ratio = 1/1000
        self.trade_rec = []

    def buy(self,stock,day,price,num):
        if stock in self.position:
            #调整成本价
            old_price = self.position[stock].price
            old_number = self.position[stock].number
            self.position[stock].price = (old_price*old_number+price*num)/(old_number+num)
            self.position[stock].number += num
        else:
            self.position[stock] = TradeData(stock,0,day,price,num)

        self.trade_rec.append(TradeData(stock,0,day,price,num))
        self.fund = self.fund - price*num*(1+self.tax_ratio)
        return
    
    def sell(self,stock,day,price,num):
        if stock in self.position and self.position[stock].number >= num:
            left_num = self.position[stock].number - num
            if left_num > 0:
                #调整成本价
                old_price = self.position[stock].price
                old_number = self.position[stock].number
                self.position[stock].price = (old_price*old_number-price*num)/(old_number-num)
                self.position[stock].number = left_num
            elif left_num == 0:
                del self.position[stock]
            self.fund = self.fund + price*num*(1-self.tax_ratio)
            self.trade_rec.append(TradeData(stock,1,day,price,num))
            return True
        return False
    
    def sell_out(self,stock,day,price):
        if stock in self.position:
            num = self.position[stock].number
            del self.position[stock]
            self.trade_rec.append(TradeData(stock,1,day,price,num))
            self.fund = self.fund + price*num*(1-self.tax_ratio)
            return True
        return False
    
    #获取当前资产价值
    def get_cur_capital(self):
        total = 0
        for val in self.position.values():
            total += val.number*val.price #这里要查最近股价来算
        total += self.fund
        return total
    
    #当前盈亏比
    def get_cur_profit_ratio(self):
        return self.get_cur_capital()/self.init_fund-1
    
    def get_cur_fund(self):
        return self.fund
    
    def get_trade_rec(self):
        return self.trade_rec
    
    def get_position(self):
        return self.position

#等分账户，每个股买相同份额
class EqualPartAccount(BaseAccount):
    # fund 当前资金，max_pos_num 最大持仓的个股数
    def __init__(self,fund=100000,max_pos_num=3):
        BaseAccount.__init__(fund = fund)
        self.max_pos_num = max_pos_num

    def buy(self,stock,price): #每次买一份
        return
    
    def sell(self,stock,price):#每次卖一份
        return