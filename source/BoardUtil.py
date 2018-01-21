#!/usr/bin/env python

import copy
import sys
from math import modf
import datetime


class BoardSnapShot:
    last_update_ts = 0
    update_number = 0
    full_board = {"bids": [], "asks": [], }

    def __init__(self, full_board, update_number, last_update_ts):
        self.last_update_ts = last_update_ts
        self.update_number = update_number
        self.full_board = copy.deepcopy(full_board)

    def cleanup(self):
        for side in ["bids", "asks"]:
            self.full_board[side] = [x for x in self.full_board[side] if x['size'] != 0.0]
            # print(self.full_board[side])
            pass

    # deprecated
    def board_difference(self, other_board_snapshot):
        # old_snapshot, new_snapshot = self, other_board_snapshot
        old, new = self.full_board, other_board_snapshot.full_board
        # print(old)
        # print(that)

        new_records = {}
        disappeared_records = {}
        for side in ["asks", "bids"]:
            print(f"Now, check side of {side}")
            new_records[side] = [val for val in new[side] if val not in old[side]]
            print("These are in new, not in old", new_records[side])

            disappeared_records[side] = [val for val in old[side] if val not in new[side]]
            print("These are in old, not in new", disappeared_records[side])

        for side in ["asks", "bids"]:
            side_prices = set([price_size_pair["price"]
                               for price_size_pair in new_records[side] + disappeared_records[side]])

            update_delta = {"bids": [], "asks": []}
            for price in side_prices:
                if not price_in_records(price, new_records[side]):
                    new_records[side].append({'price': price, 'size': 0.0})
                if not price_in_records(price, disappeared_records[side]):
                    disappeared_records[side].append({'price': price, 'size': 0.0})

                update_delta[side].append({'price': price,
                                           'size': get_size_of_price(price, new_records[side]) - get_size_of_price(
                                               price, disappeared_records[side])})

                update_delta[side] = sorted(update_delta[side], key=lambda x: -x['price'])
            print(side, "new", new_records[side])
            print(side, "old", disappeared_records[side])
            print(side, "delta", update_delta[side])

    # TODO: Add args n=5 to decide how many depth to print, n=0 to print full depth.
    def snapshot_pprint(self):
        print("-" * 10, f"update_number:{self.update_number}",
              f"updated_time:{get_last_update_time_jp_tz(self.last_update_ts)}")
        # for side in ["asks", "bids"]:
        #     for price_values_pair in self.full_board[side]:
        #         price, size = price_values_pair["price"], price_values_pair["size"]
        #         string = f"{side} - Price:{price:11.1f}, Size:{size:11.7f}"
        #         print(string)
        #     if side == "asks":
        #         price = self.full_board["mid_price"]
        #         string = f"mid  - Price:{price:11.1f}"
        #         print(string)

        # only print +/- 5 depth

        for price_values_pair in self.full_board["asks"][-5:]:
            price, size = price_values_pair["price"], price_values_pair["size"]
            string = f"asks - Price:{price:11.1f}, Size:{size:11.7f}"
            print(string)
        price = self.full_board["mid_price"]
        string = f"mid  - Price:{price:11.1f}"
        print(string)
        for price_values_pair in self.full_board["bids"][:5]:
            price, size = price_values_pair["price"], price_values_pair["size"]
            string = f"bids - Price:{price:11.1f}, Size:{size:11.7f}"
            print(string)

    def get_best_ask_price_size_pair(self):
        return min(self.full_board["asks"], key=lambda x: x["price"])

    def get_best_bid_price_size_pair(self):
        return max(self.full_board["bids"], key=lambda x: x["price"])

    def is_validate(self):
        bid_depth = len(self.full_board["bids"])
        ask_depth = len(self.full_board["asks"])
        if bid_depth == ask_depth == 0:
            return True
        if bid_depth == 0 and self.get_best_ask_price_size_pair()["price"] >= self.full_board["mid_price"]:
            return True
        if ask_depth == 0 and self.full_board["mid_price"] >= self.get_best_bid_price_size_pair()["price"]:
            return True
        return self.get_best_ask_price_size_pair()["price"] >= self.full_board["mid_price"] >= \
               self.get_best_bid_price_size_pair()["price"]

    def validate_error_type(self):
        best_ask = self.get_best_ask_price_size_pair()["price"]
        mid = self.full_board["mid_price"]
        best_bid = self.get_best_bid_price_size_pair()["price"]

        if best_bid >= mid and best_ask > mid:
            return "best_bid_higher_then_mid"
        if best_ask <= mid and best_bid < mid:
            return "best_ask_lower_then_mid"
        if best_bid > best_ask:
            return "crossed_bid_ask"
            # sys.exit()

    def get_board_error(self):
        mid = self.full_board["mid_price"]

        return {
            "bids": [item for item in self.full_board["bids"] if item["price"] >= mid],
            "asks": [item for item in self.full_board["asks"] if item["price"] <= mid],
        }

    def board_adjustment(self):
        print(self.validate_error_type())
        print("board_error is ", self.get_board_error())
        for side in ["bids", "asks"]:
            for price_size_pair in self.get_board_error()[side]:
                price_size_pair["size"] = 0
        self.cleanup()
        print("After adjustment:")
        self.snapshot_pprint()


def price_in_records(price, records):
    for price_size_pair in records:
        # print(type(price_size_pair),price_size_pair)
        if price_size_pair['price'] == price:
            return True
    return False


def get_last_update_time_jp_tz(last_update_ts):
    small_ts, ts = modf(last_update_ts)
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def get_last_update_time_utc_tz(last_update_ts):
    small_ts, ts = modf(last_update_ts)
    return datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def get_size_of_price(price, records):
    for price_size_pair in records:
        if price_size_pair['price'] == price:
            return price_size_pair['size']


class BoardDifference:
    old_snapshot = {}
    new_snapshot = {}
    update_delta = {"bids": [], "asks": [], }
    new_records = {}
    disappeared_records = {}

    def __init__(self, old_snapshot, new_snapshot):
        self.old_snapshot = old_snapshot
        self.new_snapshot = new_snapshot
        self.update_delta = {"bids": [], "asks": [], }
        self.new_records = {}
        self.disappeared_records = {}
        old_board = copy.deepcopy(old_snapshot.full_board)
        new_board = copy.deepcopy(new_snapshot.full_board)
        # print(old)
        # print(that)

        new_records = self.new_records
        disappeared_records = self.disappeared_records
        for side in ["asks", "bids"]:
            new_records[side] = [val for val in new_board[side] if val not in old_board[side]]

            disappeared_records[side] = [val for val in old_board[side] if val not in new_board[side]]

        for side in ["asks", "bids"]:
            side_prices = set([price_size_pair["price"]
                               for price_size_pair in new_records[side] + disappeared_records[side]])

            update_delta = self.update_delta
            for price in side_prices:
                if not price_in_records(price, new_records[side]):
                    new_records[side].append({'price': price, 'size': 0.0})
                if not price_in_records(price, disappeared_records[side]):
                    disappeared_records[side].append({'price': price, 'size': 0.0})

                update_delta[side].append({'price': price,
                                           'size': get_size_of_price(price, new_records[side]) - get_size_of_price(
                                               price, disappeared_records[side])})

                update_delta[side] = sorted(update_delta[side], key=lambda x: -x['price'])

        # for side in ["asks", "bids"]:
        #     print(side, "new  ", new_records[side])
        #     print(side, "old  ", disappeared_records[side])
        #     print(side, "delta", update_delta[side])

    def pprint(self):
        # print(self.update_delta)
        print(
            "-" * 10 + f"This is compare between {self.old_snapshot.update_number} and {self.new_snapshot.update_number}")

        for side in ["asks", "bids"]:
            for price_values_pair in self.update_delta[side]:
                price, size = price_values_pair["price"], price_values_pair["size"]
                string = f"{side}     - Price:{price:11.1f}, Size:{size:11.7f}"
                print(string)
            if side == "asks":
                best_ask = self.new_snapshot.get_best_ask_price_size_pair()
                price, size = best_ask["price"], best_ask["size"]
                string = f"best ask - Price:{price:11.1f}, Size:{size:11.7f}\n"

                best_bid = self.new_snapshot.get_best_bid_price_size_pair()
                price, size = best_bid["price"], best_bid["size"]
                string += f"best bid - Price:{price:11.1f}, Size:{size:11.7f}"

                print(string)

    @property
    def pattern(self):
        ask_delta_number = len(self.update_delta["asks"])
        bid_delta_number = len(self.update_delta["bids"])

        ask_delta_plus_number = len([x for x in self.update_delta["asks"] if x["size"] > 0])
        bid_delta_plus_number = len([x for x in self.update_delta["bids"] if x["size"] > 0])

        bid_delta_minus_number = len([x for x in self.update_delta["bids"] if x["size"] < 0])
        ask_delta_minus_number = len([x for x in self.update_delta["asks"] if x["size"] < 0])

        # to make pycharm happy
        # otherwise, "Local variable might be referenced before assignment."
        min_ask_delta_price = 0
        max_ask_delta_price = 0
        min_bid_delta_price = 0
        max_bid_delta_price = 0

        if ask_delta_number != 0:
            min_ask_delta_price = min([x["price"] for x in self.update_delta["asks"]])
            max_ask_delta_price = max([x["price"] for x in self.update_delta["asks"]])
        if bid_delta_number != 0:
            min_bid_delta_price = min([x["price"] for x in self.update_delta["bids"]])
            max_bid_delta_price = max([x["price"] for x in self.update_delta["bids"]])

        new_best_ask_price = self.new_snapshot.get_best_ask_price_size_pair()["price"]
        new_best_bid_price = self.new_snapshot.get_best_bid_price_size_pair()["price"]

        old_best_ask_price = self.old_snapshot.get_best_ask_price_size_pair()["price"]
        old_best_bid_price = self.old_snapshot.get_best_bid_price_size_pair()["price"]

        # 因为无法保证数据的连续性和完整性

        # 增加流动性的限价单 特点, 只在一次有单条变化,
        # 两种状况 新单在best bid/ask 之外, 称为 passive; 新单在best bid/ask 之内, 称为为aggressive
        if ask_delta_plus_number == 1 and bid_delta_number == 0 and min_ask_delta_price >= old_best_ask_price:
            return "passive_sell_limit"
        if ask_delta_plus_number == 1 and bid_delta_number == 0 and old_best_ask_price > min_ask_delta_price > new_best_bid_price:
            return "aggressive_sell_limit"
        if ask_delta_plus_number == 1 and bid_delta_number == 0 and new_best_bid_price >= min_ask_delta_price:
            print(f"old_best_ask_price is {old_best_ask_price}")
            print(f"min_ask_delta_price is {min_ask_delta_price}")
            print(f"new_best_bid_price is {new_best_bid_price}")
            return "Error: ask price is lower then best bid"

        if bid_delta_plus_number == 1 and ask_delta_number == 0 and max_bid_delta_price <= old_best_bid_price:
            return "passive_buy_limit"
        if bid_delta_plus_number == 1 and ask_delta_number == 0 and old_best_bid_price < max_bid_delta_price < new_best_ask_price:
            return "aggressive_buy_limit"
        if bid_delta_plus_number == 1 and ask_delta_number == 0 and new_best_ask_price <= max_bid_delta_price:
            return "Error: bid price is higher then best ask"

        # 撤销单, 这里判断了单条撤销单  条件: 只在单侧有厚度减小, 在best bid/ask 价格之外
        # 注意: 可能还有其他的撤销单
        if bid_delta_number == 0 and ask_delta_minus_number == 1 and min_ask_delta_price > new_best_ask_price:
            return "cancel_sell"
        if ask_delta_number == 0 and bid_delta_minus_number == 1 and max_bid_delta_price < new_best_bid_price:
            return "cancel_buy"

        # 消耗流动性的市价单, 这里判断了大单, 也就是吃掉了两条以上的深度,(所以新的best价格会在原来的价格之外) 同时没有残余, 也就是没有新增流动性
        # 如果是一个限价单,那么应当作为市价单处理吧.....
        if bid_delta_number == 0 and ask_delta_minus_number > 1 and new_best_ask_price > old_best_ask_price:
            return "market_sell"
        if ask_delta_number == 0 and bid_delta_minus_number > 1 and new_best_bid_price < old_best_bid_price:
            return "market_buy"

        # 消耗流动性的定价单, 这里判断了定价单在对侧最佳价格之外, 并且吃光了至少一条限价单, 同时有所残余, 所以会新增流动性
        # 本侧只有一条新增记录, 对侧只有减少记录且至少一条, 本侧的最佳报价会被更新至更高
        if ask_delta_number == ask_delta_plus_number == 1 and bid_delta_minus_number >= 1 and new_best_ask_price > old_best_ask_price:
            return "limit_execution_sell"
        if bid_delta_number == bid_delta_plus_number == 1 and ask_delta_minus_number >= 1 and new_best_bid_price > old_best_bid_price:
            return "limit_execution_buy"

        # liquidity_decrease
        # 不确定的流动性消失,  对侧没有变化, 发生在单侧, 最佳报价消失了一部分或全部,
        # 可能是:   市价单, 限价单, 撤销单
        # 前两者不可区分, 前两者与后者的区别在于后者没有成交记录
        if bid_delta_number == 0 and ask_delta_number == ask_delta_minus_number == 1 and min_ask_delta_price == old_best_ask_price:
            return "ask_liquidity_decrease"
        if ask_delta_number == 0 and bid_delta_number == bid_delta_minus_number == 1 and max_bid_delta_price == old_best_bid_price:
            return "bid_liquidity_decrease"

        # batch cancel
        # 同时撤销掉了自己的多条订单
        if bid_delta_number == 0 and ask_delta_minus_number > 1 and old_best_ask_price == new_best_ask_price:
            return "cancel_batch_ask"
        if ask_delta_number == 0 and bid_delta_minus_number > 1 and old_best_bid_price == new_best_bid_price:
            return "cancel_batch_bid"
        if ask_delta_number >= 1 and bid_delta_number >= 1 and old_best_ask_price == new_best_ask_price and old_best_bid_price == new_best_bid_price:
            return "cancel_batch_both"

        # 集合竞价
        # self.pprint()
        # print(f"bid_delta_number is {bid_delta_number }")
        # print(f"ask_delta_minus_number is {ask_delta_minus_number }")
        # print(f"old_best_ask_price is {old_best_ask_price }")
        # print(f"new_best_ask_price is {new_best_ask_price}")

        return "Unknown!!!!!!!!!!!!"

    def get_order(self):
        pass


class Order:
    id = ""

    executions = []
    size = 0.0
    left_size = 0.0
    start_ts = 0.0
    end_ts = 0.0


class Executions:
    pass


class Execution:
    pass
