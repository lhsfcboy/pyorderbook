# pyorderbook
用来模拟订单驱动的交易市场, 方便进行各种研究.
使用者应当对交易系统有最初步的认识.例如, 理解什么是限价单, 什么是市价单.


## 预想的功能
绘制竞价板

## Board
竞价板, 应该为每个交易所的每个交易版的每个交易品种创建一个竞价板.
例如: 东证一部的索尼.
再例如, 套利交易时, 应该分别有交易所A的X品种与交易所B的X品种的两个板块.

## BoardSnapshot

某一时刻的orderbook的快照, 包含了各个价位上的订单.

## Order
不支持IFD一类的订单, 仅仅负责 现价单/市价单/修改单和撤销单

IFD订单, StopLoss订单, 应由发单模块负责.
(注意: 现实当中, 有些交易所会支持这样的订单. 即便如此, 也应该是一个发单模块进行处理. )

另外一个例子是Hunali订单, 若未成交则在收盘集合竞价时转为market order.

## Executions
成交组, 内含一系列成交.
例如: 一个市价单正好吃掉了同一个价位上的三个限价单, 则应有一个成交组, 包含三个成交.

## Execution.
单笔成交.


## Exchange
交易所.

## FXrate
用于实时返回可以成交的汇率.
