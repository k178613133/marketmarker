#!/usr/bin/python3
# -*- coding: utf-8 -*-
# encoding: utf-8
import ccxt
import json
import time
from numpy import NaN
import math
import sys
from pprint import pprint
from tool.logtool.logger import Logger #日志模块

#初始化日志系统
log = Logger("debug")
'''日志系统调用方法和级别
x.critical("这是一个 critical 级别的问题！")
x.error("这是一个 error 级别的问题！")
x.warning("这是一个 warning 级别的问题！")
x.info("这是一个 info 级别的问题！")
x.debug("这是一个 debug 级别的问题！")
'''
#读取配置文件
Info = json.load(open('sport.json')); log.info("配置文件信息读取");log.info(Info)

initCounter = Info['initCounter']
baseInfo = Info['baseInfo']
Names = [info['currency'] for info in baseInfo]

marketLength = len(baseInfo)
Balances = [0.0 for i in range(marketLength)]
buyOrders = [[] for i in range(marketLength)]
sellOrders = [[] for i in range(marketLength)]

#初始化apikey，secretkey,url
config = open('.apikey','r')
lines = config.readlines()
apikey = lines[0].strip()
secretkey = lines[1].strip()
config.close()

exchange = ccxt.huobipro({
    'apiKey': apikey,
    'secret': secretkey
})

flagShow = True
def checkMyOrders(index, orders, targetOrders, Type):
	temp = [order for order in targetOrders]
	uselessOrdersID = []
	#print(orders)
	for order in orders:
		#print(order)
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
			print (u'##Cancel order')
			print (exchange.cancelOrder(id = str(seq), symbol = Names[index]+'/'+Names[0]))
			print (u'##Cancel order')
			#except:
			#	print (u'##Cancel order')
			#	continue
	for target in temp:
		orderprice = target[0]
		orderamount = target[1]
		#createMarketOrder(index, Type, price, amount)
		print (Names[index]+'/'+Names[0], Type, str(orderprice), str(orderamount))
		try:
			# result = 
			log.info (exchange.createOrder(symbol=Names[index]+'/'+Names[0],side=Type,type='limit',amount=orderamount,price=orderprice))
		except Exception as ex:
			# log.error('订单创建失败');log.error(ex)
			continue

while True:
	time.sleep(5)
	#################1. Fetch balance###################
	log.info("#################1. Fetch balance###################")
	try:
		res = exchange.fetchBalance()
		funds = res
	except Exception as ex:
		log.error ('##Fail to fetch balance' + str (ex))
		continue
	try:
		for i in range(marketLength):
			Balances[i] = float(funds['free'][Names[i]])+float(funds['used'][Names[i]])
			log.info(Names[i] + ': ' + str(Balances[i]))
	except Exception as ex:
		log.error ('##Fail to fetch free or used balance' + str(ex))
        
		continue
	#################2. Fetch open order###################
	log.info ('#################2. Fetch open order###################')
	flagsuc = True
	for i in range(1, marketLength):
		buyOrders[i] = []
		sellOrders[i] = []
		try:
			res = exchange.fetchOpenOrders(symbol = Names[i]+'/'+Names[0])
			orders = res
			#pprint(res)
		except:
			log.error(res)
			flagsuc = False
			break
		for order in orders:
			info = [order['id'], order['price'], order['amount']]
			#print (info)
			if order['side'] == 'buy':
				buyOrders[i].append(info)
			elif order['side'] == 'sell':
				sellOrders[i].append(info)
		# print('##' + Names[i], '\n Buy orders: ', buyOrders[i], '; Sell orders: ', sellOrders[i])
		log.info ('Buy orders:');log.info (buyOrders[i])
		log.info ('Sell orders:');log.info (sellOrders[i])
        
	if not flagsuc:
		continue
	#print (Balances)
	#################3. Analyse###################
	log.info('#################3. Analyse###################')
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

		initbuy = - gap
		initsell = gap
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
				buyamount = round(buyAmount,8) - 0.00000001
				sellprice = round(sellPrice,6)
				sellamount = round(sellAmount,8) - 0.00000001
			else:
				buyprice = round(buyPrice * math.pow(rate, -i), 6)
				buyamount = round(tradeAmount,3)
				sellprice = round(sellPrice * math.pow(rate, i), 6)
				sellamount = round(tradeAmount,3)

			if buyamount >= minAmount :
				buyTarget.append([buyprice, buyamount])
			if sellamount >= minAmount :
				sellTarget.append([sellprice, sellamount])
		print (Names[t],'Target\n',buyTarget,'\n',sellTarget)

		#if (Balances[t] < tradeAmount * orderLength):
		if (Balances[t] < sellAmount):
			if flagShow:
				log.info('not enough '+Names[t]+' to create sell orders')
		elif highLimit < sellprice:
			if flagShow:
				log.info(Names[t]+' is too high')
		else:
			log.info("sellTarget：");log.info(sellTarget)
			checkMyOrders(t, sellOrders[t], sellTarget, 'sell')

		#if (Balances[0] < tradeAmount * orderLength * buyPrice):
		if (Balances[0] < tradeAmount * buyPrice):
			print('not enough '+Names[t]+' to create buy orders')
		elif lowLimit > buyprice:
			if flagShow:
				print(Names[t]+' is too low')
		else:
			log.info("buyTarget：");log.info(buyTarget)
			checkMyOrders(t, buyOrders[t], buyTarget, 'buy')

	if flagShow:
		log.info ('current Balances:');log.info(Balances)
		needBalance = initCounter+diff
		log.info ('you should have ');log.info(str(needBalance)+Names[0])
		flagShow = False
