# -*- coding: utf-8 -*-
#!/usr/bin/python3

import time
import datetime

def createOrderId():
    t = time.time()
    orderId = int(round(t * 1000))    #毫秒级时间戳
    orderId = str(orderId)
    return orderId
 
 