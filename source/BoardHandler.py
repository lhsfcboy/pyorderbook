#!/usr/bin/env python
#  coding: utf-8
import json
import time
import datetime
import sys
import re
from BoardUtil import *

import copy


class FullBoard:
    """A simple example class"""
    full_board = {"bids": [], "asks": [], "mid_price": None, }
    # full_board = {"mid_price": 35625,
    #               "bids": [{"price": 33000, "size": 1}, {"price": 33350, "size": 1}, {"price": 33351, "size": 1}, ],
    #               "asks": []}
    update_number = 0
    update_number_last_time_unfound_price = 0
    unfound_price_per_update = 0
    executed_order_list = []
    onboard_order_list = []

    previous_update_ts = 0
    last_update_ts = time.mktime(datetime.datetime.strptime("2017-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").timetuple())


    board_snapshot_list = []

    def __init__(self):
        self.board_snapshot_list.append(BoardSnapShot(self.full_board, self.update_number, self.last_update_ts))
        # self.update_number += 1
        # print(self.get_last_snapshot().full_board)
        # sys.exit()
        # pass

    def get_market_depth(self):
        market_depth = 0
        for side in ["bids", "asks"]:
            # print(self.full_board[side])
            # print(len(self.full_board[side]))
            market_depth += len(self.full_board[side])
        return market_depth

    def board_pprint(self):
        # for side in ["asks", "bids"]:
        #     for price_values_pair in self.full_board[side]:
        #         price, size = price_values_pair["price"], price_values_pair["size"]
        #         string = f"{side} - Price:{price:11.1f}, Size:{size:11.7f}"
        #         print(string)
        #     if side == "asks":
        #         price = self.full_board["mid_price"]
        #         string = f"mid  - Price:{price:11.1f}"
        #         print(string)
        print("-" * 10, f"update_number:{self.update_number}",
              f"last_time_unfound:{self.update_number_last_time_unfound_price}",
              # f"unfound_price_per_update:{self.unfound_price_per_update}",
              f"market_depth:{self.get_market_depth()}",
              "\n", end="")
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

    def board_cleanup(self):
        for side in ["bids", "asks"]:
            self.full_board[side] = [x for x in self.full_board[side] if x['size'] != 0.0]
            # print(self.full_board[side])
            pass

    def board_update(self, board_update_info):
        self.update_number += 1
        self.unfound_price_per_update = 0

        self.full_board["mid_price"] = board_update_info["mid_price"]
        self.last_update_ts = board_update_info["ts"]
        for side in ["bids", "asks"]:
            # print(board_update_info[side])
            side_price_tags = set([price_size_pair["price"]
                                   for price_size_pair in self.full_board[side]])
            # print(board_update_info[side])
            for price_values_pair in board_update_info[side]:
                if price_values_pair in self.full_board[side]:
                    # print("This price size is already on board.")
                    pass
                elif price_values_pair["price"] in side_price_tags:
                    target_price = price_values_pair["price"]
                    target_size = price_values_pair["size"]
                    # print("Updating the size of that price")
                    for current_price_size_pair in self.full_board[side]:
                        # print(type(current_price_size_pair), current_price_size_pair)
                        if current_price_size_pair['price'] == target_price:
                            current_price_size_pair['size'] = target_size

                else:
                    # print("Appending the price size pair")
                    self.full_board[side].append(price_values_pair)
                    self.update_number_last_time_unfound_price = self.update_number
                    self.unfound_price_per_update += 1
                pass
            # print(side, price_values_pair, type(price_values_pair), type(self.full_board[side]))
            # print("Is this price_value_pair in current board already?", price_values_pair in self.full_board[side])
            self.full_board[side] = sorted(self.full_board[side], key=lambda x: -x['price'])

        self.board_cleanup()



        # current_board_snapshot = BoardSnapShot(self.full_board, self.update_number, self.last_update_ts)
        # # 修正!!!
        # # 这里我们判断此次update是否有效,
        # # 若有效则, 否则进行修正, 生成修正订单, 并且将修正后的snapshot传给下游处理
        # if not current_board_snapshot.is_validate():
        #     print("----------\n", "本次update未通过检查")
        #     print("Update之前:")
        #     self.get_last_snapshot().snapshot_pprint()
        #     print("update_info is ", board_update_info)
        #     print("Update之后,调整之前:")
        #     self.board_pprint()
        #
        #     current_board_snapshot.board_adjustment()
        #     self.board_snapshot_list.append(current_board_snapshot)
        #
        # else:
        #     current_board_snapshot = BoardSnapShot(self.full_board, self.update_number, self.last_update_ts)
        #     self.board_snapshot_list.append(current_board_snapshot)
        #
        #     pass

        self.previous_update_ts = self.last_update_ts
        # self.board_pprint()
        # print(self.full_board)
        # print("-" * 20, "\n", self.get_current_update_number(), "\n", self.full_board, "\n")
        # print(self.update_number, self.last_update_ts)

    def get_current_board(self):
        # print(self.get_current_update_number(), "\n", self.full_board)
        # pprint()
        return self.full_board

    def get_current_update_number(self):
        return self.update_number

    def get_snapshot_from_update_number(self, update_number):
        return [item for item in self.board_snapshot_list if item.update_number == update_number][0]

    def get_current_snapshot(self):
        return self.get_snapshot_from_update_number(self.update_number)

    def get_last_snapshot(self):
        return self.get_snapshot_from_update_number(self.update_number - 1)


def local_test():
    bitflyer_board = FullBoard()
    test_board_1 = {"mid_price": 35625.0, "bids": [{"price": 33350.0, "size": 1.0}, {
        "price": 33351.0, "size": 2.0}], "asks": [{"price": 33359.0, "size": 1.0}, {"price": 33358.0, "size": 2.0}]}
    test_board_2 = {"mid_price": 35625.2, "bids": [{"price": 33350.2, "size": 11.2}, {
        "price": 33351.2, "size": 22.2}], "asks": [{"price": 33359.2, "size": 12.3}, {"price": 33358.2, "size": 0.0}]}
    bitflyer_board.board_update(test_board_1)
    bitflyer_board.board_update(test_board_2)


def file_read_run():
    bitflyer_board = FullBoard()
    board_update_list = []

    with open('board_info.txt') as json_list_file:
        json_string = ""
        for line in json_list_file:
            json_string += line
            if line == "}\n":
                # print("Find new json string!")
                board_update_info = json.loads(json_string)
                json_string = ""
                board_update_list.append(board_update_info)

    for board_update_info in board_update_list:
        bitflyer_board.board_update(board_update_info)
        # print(bitflyer_board.get_last_update_time_jp_tz())
    for board_snapshot in bitflyer_board.board_snapshot_list:
        board_snapshot.snapshot_pprint()


def run_ts():
    bitflyer_board = FullBoard()
    bitflyer_board.last_update_ts = time.time()
    print(get_last_update_time_jp_tz(bitflyer_board.last_update_ts))
    print(get_last_update_time_utc_tz(bitflyer_board.last_update_ts))


# deprecated
def run_board_difference():
    bitflyer_board = FullBoard()
    test_board_1 = {"mid_price": 35625.2, "ts": 1514122458.3816898, "bids": [{"price": 33350.2, "size": 11.2}, {
        "price": 33351.2, "size": 22.2}], "asks": [{"price": 33359.2, "size": 12.3}, {"price": 33358.2, "size": 0.0}]}
    test_board_2 = {"mid_price": 35625.2, "ts": 1514122458.3816898, "bids": [{"price": 33350.2, "size": 11.2}, {
        "price": 33351.2, "size": 22.2}], "asks": [{"price": 33359.2, "size": 12.3}, {"price": 33358.2, "size": 0.0}]}
    test_board_3 = {"mid_price": 35625.2, "ts": 1514122468.3816898, "bids": [{"price": 33350.2, "size": 11.2}, {
        "price": 33351.2, "size": 22.2}], "asks": [{"price": 33359.2, "size": 10.3}, {"price": 33358.2, "size": 0.0}]}

    for board_update in [test_board_1, test_board_2, test_board_3]:
        bitflyer_board.board_update(board_update)

    for board_snapshot in bitflyer_board.board_snapshot_list:
        board_snapshot.snapshot_pprint()

    for index, item in enumerate(bitflyer_board.board_snapshot_list):
        if index == len(bitflyer_board.board_snapshot_list) - 1:
            continue
        else:
            print(f"now compare {item.update_number} with {item.update_number+1}")
            item.board_difference(bitflyer_board.board_snapshot_list[index + 1])


def board_difference_with_file():
    bitflyer_board = FullBoard()

    board_update_list = []
    # board_1_11560.txt contains 903 update
    with open('board_1_11560.txt') as json_list_file:
        json_string = ""
        for line in json_list_file:
            json_string += line
            if line == "}\n":
                # print("Find new json string!")
                board_update_info = json.loads(json_string)
                json_string = ""
                board_update_list.append(board_update_info)
    for board_update_info in board_update_list:
        bitflyer_board.board_update(board_update_info)
        # print(bitflyer_board.get_last_update_time_jp_tz())

    inited_update_number = len(bitflyer_board.board_snapshot_list)
    # print(inited_update_number)

    board_update_list = []
    # board_1_11560.txt contains 903 update
    with open('board_11561_12661.txt') as json_list_file:
        json_string = ""
        for line in json_list_file:
            json_string += line
            if line == "}\n":
                # print("Find new json string!")
                board_update_info = json.loads(json_string)
                json_string = ""
                board_update_list.append(board_update_info)
    for board_update_info in board_update_list:
        bitflyer_board.board_update(board_update_info)
        # print(bitflyer_board.get_last_update_time_jp_tz())

    for index in range(inited_update_number, len(bitflyer_board.board_snapshot_list)):
        # bitflyer_board.snapshot_pprint(bitflyer_board.board_snapshot_list[index])

        if index == inited_update_number:
            continue
        else:
            print(f"---------------- Looking at the compare of {index } to {index + 1}.")
            old = bitflyer_board.board_snapshot_list[index - 1]
            new = bitflyer_board.board_snapshot_list[index]
            board_difference = BoardDifference(old, new)
            print(board_difference.pattern)
            # import sys
            # sys.exit()


def main():
    bitflyer_board = FullBoard()
    INIT_REQUIED_ROUND = 6000
    SNAPSHOT_NUMBER_TO_HOLD = 100
    REQUIRED_CONTINUOUS_VALIDATE = 10
    VALIDATE_ENOUGH = False
    validated_snapshot = 0

    # board_1_11560.txt contains 903 update
    with open('board_from_20171226-231500.txt') as json_list_file:
        json_string = ""
        for line in json_list_file:
            json_string += line
            if line == "}\n":
                # print("Find new json string!")
                board_update_info = json.loads(json_string)
                json_string = ""
                bitflyer_board.board_update(board_update_info)

                # print(board_update_info)
                # bitflyer_board.get_current_snapshot().snapshot_pprint()
                # print(bitflyer_board.get_current_snapshot().is_validate())
                # if bitflyer_board.update_number > 10:
                #     sys.exit()

                # 打印出未通过检查的snapshot
                if not bitflyer_board.get_current_snapshot().is_validate():
                    if bitflyer_board.update_number > 5000:
                        sys.exit()
                    # sys.exit()

                # 控制储存的snapshot的长度
                if bitflyer_board.update_number % 35 == 0:
                    if len(bitflyer_board.board_snapshot_list) > SNAPSHOT_NUMBER_TO_HOLD:
                        del bitflyer_board.board_snapshot_list[0:-1 * SNAPSHOT_NUMBER_TO_HOLD]

                # 获取进展
                if bitflyer_board.update_number > 0 and bitflyer_board.update_number % 200 == 0:
                    print(f"Updating on {bitflyer_board.update_number}", f"VALIDATE_ENOUGH is {VALIDATE_ENOUGH}"
                          , f"validated_snapshot is {validated_snapshot}")

                # 初步初始化:至少消耗数千个update来作为初始化的一部分
                if bitflyer_board.update_number <= INIT_REQUIED_ROUND:
                    if bitflyer_board.update_number % 200 == 0:
                        # print(f"Still initing, updating on {bitflyer_board.update_number}")
                        # print(f"Current board_snapshot_list len is {len(bitflyer_board.board_snapshot_list)}")
                        pass
                    continue

                # 初步初始化后,判断是否有连续的数十个经过检验的snapshot
                current_snapshot = bitflyer_board.get_current_snapshot()
                if bitflyer_board.update_number > INIT_REQUIED_ROUND and (not VALIDATE_ENOUGH):
                    if current_snapshot.is_validate():
                        validated_snapshot += 1
                    else:
                        validated_snapshot = 0

                    if validated_snapshot > REQUIRED_CONTINUOUS_VALIDATE:
                        VALIDATE_ENOUGH = True
                        print(f"VALIDATE_ENOUGH at update{bitflyer_board.update_number}")

                if VALIDATE_ENOUGH:
                    print(validated_snapshot)
                    index = bitflyer_board.update_number

                    old = bitflyer_board.get_snapshot_from_update_number(index - 1)
                    new = bitflyer_board.get_snapshot_from_update_number(index)
                    board_difference = BoardDifference(old, new)
                    pattern_string = board_difference.pattern

                    if re.match(r'^[A-Z]+', pattern_string):
                        print(f"---------------- Looking at the compare of {index - 1} to {index}.")
                        print(pattern_string)
                        print("update_info: ", board_update_info)
                        print("update_delta: ", board_difference.update_delta)

                        board_difference.pprint()
                        old.snapshot_pprint()
                        new.snapshot_pprint()
                        sys.exit()
                    # pass
                    # sys.exit()

                # if bitflyer_board.update_number > 10:
                #     bitflyer_board.get_current_snapshot().snapshot_pprint()
                #     sys.exit()


if __name__ == '__main__':
    # bitflyer_board = FullBoard()
    #    bitflyer_board.get_current_board()
    # local_test()
    # test_board_difference()
    # test_ts()
    # board_difference_with_file()
    main()
