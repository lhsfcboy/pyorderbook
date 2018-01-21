#!/usr/bin/env python
#  coding: utf-8
import json
import pprint


def file_read_test():
    execution_list = []
    child_executions_list = []
    jsonlist_string_list = []
    jsonlist_string = ""
    json_string = ""

    # with open('execution_40882.txt') as json_list_file:
    with open('lightning_executions_BTC_JPY.txt') as json_list_file:
        for line in json_list_file:
            if line == "[\n":
                # print("Find jsonlist string start.")
                continue
            elif line == "]\n":
                jsonlist_string_list.append(jsonlist_string)
                # print("Find jsonlist string: ", jsonlist_string)
                jsonlist_string = ""
            else:
                jsonlist_string += line

    # print(len(jsonlist_string_list))
    # print(jsonlist_string_list[0])

    for jsonlist_string in jsonlist_string_list:
        for line in jsonlist_string.split():
            if line == "},":
                line = "}"
            json_string += line
            if line == "}":
                # print("Find new json string!", json_string)
                child_execution = json.loads(json_string)
                child_executions_list.append(child_execution)
                json_string = ""
        execution_list.append(child_executions_list)
        child_executions_list = []

    for child_executions in execution_list:
        # print(len(child_executions))
        exec_date_list = []
        side_list = []
        side_acceptance_id_list = []

        side = child_executions[0]["side"]
        for child_execution in child_executions:
            # print(child_execution["exec_date"], child_execution["side"])
            exec_date_list.append(child_execution["exec_date"])
            side_list.append(child_execution['side'])

            if side == "SELL":
                acceptance_id = side_acceptance_id_list.append(child_execution["sell_child_order_acceptance_id"])
            if side == "BUY":
                acceptance_id = side_acceptance_id_list.append(child_execution["buy_child_order_acceptance_id"])
        exec_date_number = len(set(exec_date_list))
        side_number = len(set(side_list))
        acceptance_id_number = len(set(side_acceptance_id_list))
        # print(exec_date_number, side_number)
        if exec_date_number != 1:
            # print("exec_date_number!!!!!!!!!!!!!!!!!!!!!!")
            pass
        if acceptance_id_number != 1:
            print("acceptance_id_number!!!!!!!!!!!!!!!!!!!!!!")
            print(side_acceptance_id_list)
            print(child_executions[0]["exec_date"])

    print(jsonlist_string_list[1])
if __name__ == '__main__':
    file_read_test()
