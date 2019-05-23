 
# import ccxt
import json
import time
from numpy import NaN
import math
import sys
from pprint import pprint
import tool
from huobi.RESTPython3.HuobiDMService import HuobiDM

#读取配置文件
Info = json.load(open('btc.json'))

initCounter = Info['initCounter']
baseInfo = Info['baseInfo']
Names = [info['currency'] for info in baseInfo]



marketLength = len(baseInfo)
Balances = [0.0 for i in range(marketLength)]
buyOrders = [[] for i in range(marketLength)]
sellOrders = [[] for i in range(marketLength)]

 
#获取APIkey配置文件
config = open('.apikey','r')
lines = config.readlines()
ACCESS_KEY = lines[0].strip()
SECRET_KEY = lines[1].strip()
config.close()
#关闭APIkey配置文件

#初始化，调用火币期货接口
dm = HuobiDM( ACCESS_KEY, SECRET_KEY)
  


flagShow = True #是否打印语句
def checkMyOrders(index, orders, targetOrders, Type):
    temp = [order for order in targetOrders]
    uselessOrdersID = []
    for order in orders:
        seq = order[0]
        myPrice = order[1]
        myIOUAmount = order[2]
        flagUseless = True
        for target in temp:
            price = target[0]
            amount = target[1]
           
            if  (abs(myPrice/price - 1) < 0.000001) and  (abs(myIOUAmount/amount - 1) < 0.1) :
                temp.remove(target)
                flagUseless = False
                break
        if flagUseless:
			#cancelOrder(index, seq)
			#try:
            print (u'##撤销订单')
			
            pprint(dm.cancel_contract_order(symbol=Names[index], order_id=str(seq)))
			# print (exchange.cancelOrder(id = str(seq), symbol = Names[index]+'/'+Names[0]))

			#except:
			#	print (u'##Cancel order')
			#	continue
    for target in temp:
        orderprice = target[0]
        orderamount = target[1]
        leverRate = target[2]

        #createMarketOrder(index, Type, price, amount)
        print (Names[index]+'/'+Names[0], Type, str(orderprice), str(orderamount))
        try:
            print("***")

            orderId = tool.createOrderId()
            #买入，则开多
            offset = 'open'
            if Type=='sell':
            # 	#卖出，则平多
            	offset = 'close'

            print('try to create:  '+str(Type)+' '+str(orderprice)+' '+str(orderamount))

            pprint(dm.send_contract_order(symbol='BTC', contract_type='quarter', contract_code='', 
                                    client_order_id=orderId, price=orderprice, volume=orderamount, direction=Type,
                                    offset=offset, lever_rate=leverRate, order_price_type='limit'))


			# print (exchange.createOrder(symbol=Names[index]+'/'+Names[0],side=Type,type='limit',amount=orderamount,price=orderprice))
        except Exception as ex:
            print (u'##Fail to fetch balance' + str (ex))

            continue

while True:
	time.sleep(5)#暂停5秒
	
	print (u'#################1. 获取火币账号合约余额###################')
	try:
	 
	 	# res = exchange.fetch_balance()
	 	accountInfo =  dm.get_contract_account_info()
 		# funds = res
	except Exception as ex:
		print (u'##Fail to fetch balance' + str (ex))
		continue
		 
	try:
		for i in range(marketLength):
		 
			# Balances[i] = float(funds['free'][Names[i]])+float(funds['used'][Names[i]])
			# print(Names[i] + ': ' + str(Balances[i]))

		
			accountSymbol = accountInfo['data'][i]['symbol'] #火币合约账户持有数字货币种类
			accountFree =  accountInfo['data'][i]['margin_available'] #火币合约账户持有数字货币数量
		
			if Names[i]==accountSymbol:
				Balances[i]=accountFree
			 
				print(Names[i] + ': ' + str(Balances[i]))
		 
	except Exception as ex:
		print (u'##Fail to fetch free or used balance' + str(ex))
		continue
 
	#################2. Fetch open order###################
	print (u'#################2. 获取火币合约账号挂单信息###################')
	flagsuc = True
 
	for i in range(1,  marketLength):
		buyOrders[i] = []
		sellOrders[i] = []
		try:
		
			# res = exchange.fetchOpenOrders(symbol = Names[i]+'/'+Names[0])
			# orders = res
			# 未成交
			symbol = Names[i]
			openOrders =dm.get_contract_history_orders(symbol=symbol, trade_type=0, type=1, status=3, create_date=90)['data']['orders']
			
			# openOrder = openOrders['data'];
			# print("the openOrder is " + openOrders)
			#pprint(res)	
		except Exception as ex:
			print("error"+str(ex))
			flagsuc = False
			break
		for order in openOrders:
			# print(order)
			orderId = order['order_id']#订单号
			volume = order['volume']#委托数量
			price = order['price']#委托价格
			direction = order['direction']# buy买 sell卖
			offset = order['offset']#open 开 close 平
			leverRate = order['lever_rate']#杠杆倍数
			info=[orderId,price,volume]
			# profit_rate = order['profit_rate']
			# profit_rate = profit_rate*100
			# info = [orderId,order['cost_open'],order['volume'],str(profit_rate)+"%"]
			if order['direction'] == 'buy':
				buyOrders[i].append(info)
			elif order['direction'] == 'sell':
				sellOrders[i].append(info)
		print('##' + Names[i], '\n Buy orders: ', buyOrders[i], '; Sell orders: ', sellOrders[i])
		# for order in orders:
		# 	info = [order['id'], order['price'], order['amount']]
		# 	#print (info)
		# 	if order['side'] == 'buy':
		# 		buyOrders[i].append(info)
		# 	elif order['side'] == 'sell':
		# 		sellOrders[i].append(info)
		# print('##' + Names[i], '\n Buy orders: ', buyOrders[i], '; Sell orders: ', sellOrders[i])
	if not flagsuc:
		continue
	#print (Balances)
	#################3. Analyse###################
	print(u'#################3. 买单/卖单操作###################')
	diff = 0
	for t in range(1, marketLength):
		initPrice = baseInfo[t]['initPrice']
		lowLimit = baseInfo[t]['lowLimit']
		highLimit = baseInfo[t]['highLimit']
		gap = baseInfo[t]['gap']
		rate = baseInfo[t]['rate']
		initBase = baseInfo[t]['initBase']
		tradeAmount = baseInfo[t]['tradeAmount']
		orderLength = baseInfo[t]['orderLength']
		minAmount = baseInfo[t]['minAmount']
		leverRat = baseInfo[t]['leverRate']
		priceUSD = baseInfo[t]['priceUSD']
		direction = baseInfo[t]['direction']
		offset = baseInfo[t]['offset']
		initbuy = - gap #最低买单，比基准价格高 gap*rate
		initsell = gap  #最高卖单，比基准价格低 gap*rate
		balanceState = (initBase - Balances[t])/tradeAmount
		balanceStateBuy = balanceState
		buyDecimal = balanceStateBuy - math.floor(balanceStateBuy)

		if (buyDecimal < 0.1) :
			buyDecimal = buyDecimal + 1
			balanceStateBuy = math.floor(balanceStateBuy)
		else:
			balanceStateBuy = math.ceil(balanceStateBuy)
		buyAmount = buyDecimal * tradeAmount
		buyPower = initbuy + balanceStateBuy
		buyPrice = initPrice * math.pow(rate, buyPower)


		balanceStateSell = balanceState
		sellDecimal = math.ceil(balanceStateSell) - balanceStateSell
		if (sellDecimal < 0.1):
			sellDecimal = sellDecimal + 1
			balanceStateSell = math.ceil(balanceStateSell)
		else:
			balanceStateSell = math.floor(balanceStateSell)
		sellAmount = sellDecimal * tradeAmount
		sellPower = initsell + balanceStateSell
		sellPrice = initPrice * math.pow(rate, sellPower)
		diff = diff + (-balanceState)*tradeAmount*buyPrice

		#if (orderLength == 0): continue
		buyTarget = []
		sellTarget = []
		for i in range(orderLength):
			if i == 0:
				buyprice = round(buyPrice,6)
				buyamount = round(buyAmount,8) #- 0.00000001
				sellprice = round(sellPrice,6)
				sellamount = round(sellAmount,8)# - 0.00000001
			else:
				buyprice = round(buyPrice * math.pow(rate, -i), 6)
				buyamount = round(tradeAmount,3)
				sellprice = round(sellPrice * math.pow(rate, i), 6)
				sellamount = round(tradeAmount,3)
			if buyamount >= minAmount :
				buyamount = int(buyamount)#合约张数，只能取整
				buyprice = round(buyprice,2)#价格只能取2位数
				buyTarget.append([buyprice, buyamount,leverRat,direction,offset])
			if sellamount >= minAmount :
				sellamount = int(sellamount)#张数，只能取整
				sellprice = round(sellprice,2)#价格只能取2位数
				sellTarget.append([sellprice, sellamount,leverRat])
		print (Names[t],'Target\n','buy:',buyTarget,'\n','sell:',sellTarget)

		#if (Balances[t] < tradeAmount * orderLength):
       
		try:
			holdOrders = dm.get_contract_position_info()['data'] #用户持仓
			print('用户持仓信息',holdOrders)
			holdOrdersLength = len(holdOrders)
			if holdOrdersLength>=1:
				holdVolume = holdOrders[0]['volume'];
				print("the holdVolume is " + str(holdVolume) +'the sellAmount is ' + str(sellAmount))
				# if (Balances[t] < sellAmount):
				if (holdVolume < sellAmount):
            
                    # if flagShow:
						print('not enough '+Names[t]+' to create sell orders')
				elif highLimit < sellprice:
                    # if flagShow:
						print(Names[t]+' is too high')
				else:
					print('开始卖出')
					checkMyOrders(t, sellOrders[t], sellTarget, 'sell')
		except Exception as ex:
			print (u'##未获取到当前用户持仓数据' + str (ex))
			continue

		

        #if (Balances[0] < tradeAmount * orderLength * buyPrice):
        # if (Balances[0] < tradeAmount * buyPrice):
        # if (Balances[0] < tradeAmount * buyPrice):	
		if (Balances[0] * leverRat   < tradeAmount *  priceUSD / buyPrice):		 
			print('not enough '+Names[t]+' to create buy orders')
		elif lowLimit > buyprice:
			if flagShow:
				print(Names[t]+' is too low')
		else:
			print("开始购买")
			checkMyOrders(t, buyOrders[t], buyTarget, 'buy')

		if flagShow:
			print ('current Balances:',Balances)
			print ('you should have ',initCounter+diff,Names[0])
			flagShow = False
