# -*- coding:utf-8 -*-
# Author: zyazlj
# Date: 2021-06-18
# Version: py38
import os
import re
import sys
import csv
import time
import getopt
import logging
from typing import MutableMapping
import demjson3 as demjson
import hashlib
import ujson as json
from jsoncomment import JsonComment
import timeit
import cudf.pandas as pd

json_parser = JsonComment(json)


class MeiyaParser():
    """
    Meiya doc parser, just extract all contents to csv file
    Before parse doc you need to start a http server with this html files and set the main directory
    """

    def __init__(self):
        self.html_home_dir = ""
        self.out_put_path = ""
        self.data_navigation = "data_navigation.json"
        self.url_online_main = ""
        self.online_doc_list = []
        self.max_json_size = 1000
        self.md5name = []
        self.id_to_tree = dict()
        self.name_to_tree = dict()
        self.meta_json = ("report_info", "case_info", "device_lists")
        self.black_list_tree = ("内容", "证据列表")
        self.logger = logging.getLogger(__name__)
        self.home_directory = ""

    def set_out_put_path(self, out_put_path):
        self.out_put_path = out_put_path
        if not os.path.exists(self.out_put_path):
            os.mkdir(self.out_put_path)

    def set_home_directory(self, home_directory):
        if home_directory.endswith("Data"):
            self.home_directory = home_directory.replace("Data", "")
        elif home_directory.endswith("data"):
            self.home_directory = home_directory.replace("data", "")
        else:
            self.home_directory = home_directory

    def set_url_online_main(self, url_online_main):
        self.url_online_main = url_online_main

    def json_load(self, json_data_file):
        json_object = None
        try:
            # IMPORTANT: the data json is encode with utf-8 bom signature
            with open(json_data_file, 'r', encoding='utf-8-sig') as json_file:
                json_data = json_file.read()
                # json_object = json.loads(json_data[clean_json(json_data.find('=') + 1 : len(json_data)])
                # json_object = json.load(self.clean_json(json_data[json_data.find('=') + 1 : len(json_data)]))
                try:
                    # json with comma
                    # https://stackoverflow.com/questions/201782/can-you-use-a-trailing-comma-in-a-json-object
                    # https://stackoverflow.com/questions/23705304/can-json-loads-ignore-trailing-commas
                    json_object = json_parser.loads(
                        json_data[json_data.find('=') + 1:len(json_data)])
                except Exception as e:
                    json_object = demjson.decode(
                        json_data[json_data.find('=') + 1:len(json_data)])
                    pass
        except Exception as e:
            # logging.getLogger(__name__).exception(e)
            print(e)
            pass
        return json_object

    def generate_ztree_list(self):
        # generate case tree node
        """
        Parse catalog with demjson library, you need to make a dict which use to connect the sons and parents and also you
        need to make a tree list as a iterator
        """
        ztree_file = os.path.join(self.home_directory, "data",
                                  self.data_navigation)
        print(ztree_file)
        json_navigation = self.json_load(ztree_file)
        if None == json_navigation:
            self.logger.info(
                "[generate_ztree_list] generate ztree failed: {0}".format(
                    ztree_file))
            return

        for element in json_navigation:
            element_id = element["id"] if element[
                                              "id"] not in self.meta_json else element["id"] + "_1xxei832"
            self.id_to_tree[element_id] = element
            self.name_to_tree[element["name"]] = element
        # handle data_report_info.json, data_case_info.json, data_device_lists.json

    def find_full_path_with_node(self, tree_node):
        full_path = tree_node['name']
        current_tree = tree_node
        while current_tree['pid'] in self.id_to_tree:
            current_tree = self.id_to_tree[current_tree['pid']]
            full_path = "\t".join((current_tree['name'], full_path))
        return full_path.replace("（", "(").replace("）", ")")

    # def save_catalog(self):
    #     try:
    #         csv_file_path = os.path.join(self.out_put_path, "index") + ".csv"
    #         with open(csv_file_path, "a+", newline='',
    #                   encoding='utf-8') as csv_file:
    #             csv_writer = csv.writer(csv_file,
    #                                     delimiter=',',
    #                                     quoting=csv.QUOTE_ALL)
    #             csv_writer.writerows(self.md5name)
    #             csv_file.close()
    #     except Exception as e:
    #         logging.getLogger(__name__).exception(e)
    #         pass

    def save_catalog(self):
        try:
            csv_file_path = os.path.join(self.out_put_path, "index") + ".csv"
            df = pd.DataFrame(self.md5name, columns=["File Name", "Parent Node Path"])
            df.to_csv(csv_file_path, mode="a+", index=False, header=False, encoding='utf-8',sep=',', quoting=csv.QUOTE_ALL)
        except Exception as e:
            logging.getLogger(__name__).exception(e)
            pass

    def save_csv_by_tree_node(self, row_list, tree):
        try:
            # replace the illegal string
            hm = hashlib.md5()
            pattern2 = re.compile("\r|\n")
            # pattern2 = re.compile("\"|\r|\n")
            parent_tree = self.find_full_path_with_node(tree)
            hm.update(parent_tree.encode('utf-8'))
            csv_file_path = os.path.join(self.out_put_path, hm.hexdigest()) + ".csv"

            if hm.hexdigest() == '043c20194f36fee063e07f0949b33474':
                pass

            # remove second header
            if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 4:
                row_list.pop(0)

            # Create a DataFrame from row_list
            df = pd.DataFrame(row_list)

            # Apply the replacement to each element in the DataFrame
            df = df.map(lambda element: str(pattern2.sub('', element).encode('utf-8'), encoding='utf-8'))

            # Append to the existing CSV file or create a new one
            df.to_csv(csv_file_path, mode="a+", index=False, header=False, sep='\t',
                      quoting=csv.QUOTE_ALL, encoding='utf-8')

            if [hm.hexdigest() + ".csv", parent_tree + ".csv"] not in self.md5name:
                self.md5name.append([hm.hexdigest() + ".csv", parent_tree + ".csv"])

        except Exception as e:
            logging.getLogger(__name__).exception(e)
            pass

    def extract_header_from_json(self, json_obj):
        csv_headers = []
        columns = json_obj["columns"]
        contents = json_obj["contents"]
        second_header_index = ""
        first_content = json_obj["contents"][0]

        # parse headers in columns
        for column in columns:
            if column["dataIndex"] not in first_content:
                # CHANGE 原数据里的type和mediaType不对应，导致数据丢失
                if column["dataIndex"] == "type" and "mediaType" in first_content:
                    tmp = 1  # print("type => mediaType") #跳过continue
                else:
                    continue
            if "render" not in column:
                csv_headers.append(column["title"])
            elif column["render"].lower() == "table":
                second_header_index = column["dataIndex"]
            else:  # column["render"] == "":
                csv_headers.append(column["title"])

        # parse headers in contents
        second_headers = []
        if second_header_index != "":
            for content in contents:
                if second_header_index not in content:
                    continue
                child_contents = content[second_header_index]
                for child_content in child_contents:
                    if child_content["title"] in second_headers:
                        continue
                    second_headers.append(child_content["title"])
        csv_headers = csv_headers + list(set(second_headers))

        # check deleted field
        if "isDelete" in first_content:
            csv_headers.append("是否删除")

        return csv_headers

    # CHANGE 获取无columns文件header
    def extract_header_from_content(self, json_obj):
        header_name_to_id = {
            "序号": "id",
            "好友账号": "sender",
            "好友昵称": "senderName",
            "好友备注": "senderRemark",
            "头像": "portrait",
            "时间": "time",
            "内容": "content",
            "文件路径": ["attach", "video", "path"],
            "消息类型": ["mediaType", "type"],
            "详细地址": "position",
            "经度": "longitude",
            "纬度": "latitude",
            "访客": "visits",
            "点赞数": "likeCount",
            "点赞好友": "likeFriend",
            "评论数": "commentCount",
            "评论": "comment",
            "是否删除": "isDelete",
        }
        csv_headers = []
        # 统一header
        for key in header_name_to_id:
            csv_headers.append(key)
        return csv_headers

    def flat_json_element(self, json_obj, column_obj, file_key):
        json_dict = {}

        # CHANGE 内部函数 减少代码量 防止key越界
        def set_value(key, value):
            if key in column_obj:
                json_dict[column_obj[key]] = value

        for key in json_obj:
            value = json_obj[key]
            if isinstance(value, list):
                for element in value:
                    # complicated
                    # "path" and "cont" both in value, you should use path
                    if "cont" not in element and "path" not in element:
                        # TODO
                        # 部分聊天记录、新闻推送、公众号等会出现处理异常
                        # 主要样式：
                        # 名片"content":{"account":"NJZXY-1228","bottomText":"个人名片","id":"wxid_eq9vexbwkn7522","name":"ZXY","portrait":"data\\MI 8美亚全\\xxxxx.png"},
                        # 聊天记录[{'attachment': '', 'content': '', 'mediaType': '02'}, {'attachment': '', 'content': '@诗琴画意 主管，我这样计算有问题？', 'mediaType': '01'}]
                        # 新闻[{'attachment': '', 'title': '英国政坛持续巨震 已有超40名官员辞职', 'url': 'http://wap.plus.yixin.im/wap/material/viewImageText?id=89892685'},...]
                        # 公众号聊天记录[{"attachment":"","des":"夏克立黄嘉千被曝离婚 结束16年婚姻","title":"夏克立黄嘉千被曝离婚 结束16年婚姻","url":"https://zx.sina.cn/e/2022-07-06/zx-imizirav2108656.d.html?HTTPS=1&wm=3049_0015&sxsj=4&gz_n=city1_20220706"},...]
                        if "title" in element:
                            json_dict[element["title"]] = ""
                        continue
                    else:
                        if "title" in element and "path" in element and "cont" in element:
                            if len(element) == 2:
                                json_dict[element["title"]] = element["cont"]
                            else:
                                json_dict[element["title"]] = element["path"]
                        elif "title" in element:
                            json_dict[element["title"]] = element["cont"]
                        else:
                            continue
                # 无法解析列表数据时，获取全部数据
                # 去除空列表
                set_value(key, json.dumps(value, ensure_ascii=False) if len(value) > 0 else "")
                # set_value(key,str(value) if len(value) > 0 else "")
            elif isinstance(value, dict):
                message_type = "type" if "type" in json_obj else "mediaType"
                # if file_key == "0CFF02AD6B4CC0EE":
                #         print(value,message_type)
                # complicated
                # "path" and "cont" both in value, you should use path
                if "path" in value:
                    # json_dict[column_obj[key]] = value["path"]
                    set_value(key, value["path"])
                elif "cont" in value:
                    # json_dict[column_obj[key]] = value["cont"]
                    set_value(key, value["cont"])
                elif "locationName" in value:
                    location = value["latitude"] if "latitude" in value else ""
                    location = location + "|" + value["longitude"] if "longitude" in value else ""
                    location = location + "|" + value["locationName"]
                    # json_dict[column_obj[key]] = value["latitude"] if "latitude" in value else ""
                    # json_dict[column_obj[key]] = json_dict[column_obj[key]] + "|" + value["longitude"] if "longitude" in value else ""
                    # json_dict[column_obj[key]] = json_dict[column_obj[key]] + "|" + value["locationName"]
                    set_value(key, location)
                elif "attachment" in value:
                    if value["attachment"] == "" and "title" in value:
                        # json_dict[column_obj[key]] = value["title"]
                        set_value(key, value["title"])
                    else:
                        # json_dict[column_obj[key]] = value["attachment"]
                        set_value(key, value["attachment"])
                # 针对转账数据处理
                elif "amount" in value:
                    # json_dict[column_obj[key]] = json.dumps(value)
                    set_value(key, json.dumps(value, ensure_ascii=False))
                # CHANGE 增加类型处理，适应不同版本
                elif json_obj[message_type] == "名片":
                    if "name" in value:
                        set_value(key, value["name"])
                    elif "account" in value:
                        # json_dict[column_obj[key]] = value["account"]
                        set_value(key, value["account"])
                    elif "uid" in value:
                        # json_dict[column_obj[key]] = value["uid"]
                        set_value(key, value["uid"])
                    elif "id" in value:
                        set_value(key, value["id"])
                    else:
                        # json_dict[column_obj[key]] = ""
                        set_value(key, "")
                elif json_obj[message_type] == "红包":
                    set_value(key, json.dumps(value, ensure_ascii=False))
                elif json_obj[message_type] == "合并聊天记录":
                    multi_msg = {}
                    try:
                        multi_msg["title"] = value["title"] if "title" in value else "转发消息"
                        multi_msg["chatList"] = []
                        for msg in json_obj[key]['Info']:
                            new_msg = {}
                            # TODO: msg type data
                            new_msg["iMsgType"] = "0" if msg[message_type] == "1" or msg[message_type] == "01" else "2"
                            new_msg["iMsgTime"] = msg["time"]
                            new_msg["wstrMessage"] = msg["content" if "content" in msg else "portrait"]
                            if "attach" in msg:
                                new_msg["wstrFilePath"] = msg["attach"]
                                new_msg["wstrFileName"] = msg["attach"]
                            elif "attachment" in msg:
                                new_msg["wstrFilePath"] = msg["attachment"]
                                new_msg["wstrFileName"] = msg["attachment"]
                            if "sendername" in msg:
                                new_msg["wstrSenderName"] = msg["sendername"]
                            elif "senderName" in msg:
                                new_msg["wstrSenderName"] = msg["senderName"]
                            new_msg["wstrSenderId"] = msg["sender"]
                            multi_msg["chatList"].append(new_msg)
                        # print(file_key)
                        # print(str(multi_msg))
                        # json_dict[column_obj[key]] = str(multi_msg) #json.dumps(multi_msg, ensure_ascii=False)
                        set_value(key, str(multi_msg))
                    except Exception as e:
                        # type 1 msg, type 2 attach
                        # print(json_obj["id"], ": ", json.dumps(json_obj["content"]))
                        # json_dict[column_obj[key]] = json.dumps(multi_msg, ensure_ascii=False)
                        set_value(key, json.dumps(multi_msg, ensure_ascii=False))
                        pass
                    # print("fuckyou")
                else:
                    full_text = ""
                    for child_key in value:
                        if not isinstance(value[child_key], str):
                            full_text = full_text + " " + " "
                        else:
                            full_text = full_text + " " + value[child_key]
                    # json_dict[column_obj[key]] = full_text
                    set_value(key, full_text)
            elif isinstance(value, str):
                if key == "isDelete":
                    value = "0" if value == "否" else "1"
                # if key in column_obj:
                #     json_dict[column_obj[key]] = value
                set_value(key, value)
                if key == "mediaType" and "type" in column_obj:
                    json_dict[column_obj["type"]] = value
            else:
                # json_dict[column_obj[key]] = ""
                set_value(key, "")
        return json_dict

        # parse 1 element in contents

    def convert_json(self, json_obj, header_list, key):
        csv_list = []
        column_dict_name_to_id = {}
        column_dict_id_to_name = {}
        columns = json_obj["columns"]
        for column in columns:
            column_dict_name_to_id[column["title"]] = column["dataIndex"]
            column_dict_id_to_name[column["dataIndex"]] = column["title"]
        column_dict_name_to_id["是否删除"] = "isDelete"
        column_dict_id_to_name["isDelete"] = "是否删除"

        contents = json_obj["contents"]
        for content in contents:
            element = []
            try:
                # DEBUG
                content_dict = self.flat_json_element(content, column_dict_id_to_name, key)
                for header in header_list:
                    if header not in content_dict:
                        element.append("")
                        continue
                    element.append(content_dict[header])
                csv_list.append(element)
            except Exception as e:
                print(e)
                if "type" in content:
                    print("content convert error", content["type"])
                pass
        return csv_list

    # CHANGE 获取无columns文件content
    def convert_content(self, json_obj, header_list, key):
        header_id_to_name = {
            "id": "序号",
            "sender": "好友账号",
            "senderName": "好友昵称",
            "senderRemark": "好友备注",
            "portrait": "头像",
            "time": "时间",
            "content": "内容",
            "attach": "文件路径",
            "video": "文件路径",
            "mediaType": "消息类型",
            "type": "消息类型",
            "position": "详细地址",
            "longitude": "经度",
            "latitude": "纬度",
            "visits": "访客",
            "likeCount": "点赞数",
            "likeFriend": "点赞好友",
            "commentCount": "评论数",
            "comment": "评论",
            "isDelete": "是否删除",
        }
        csv_list = []
        contents = json_obj["contents"]
        for content in contents:
            element = []
            try:
                # DEBUG
                content_dict = self.flat_json_element(content, header_id_to_name, key)
                for header in header_list:
                    if header not in content_dict:
                        element.append("")
                        continue
                    element.append(content_dict[header])
                csv_list.append(element)
            except Exception as e:
                print(e)
                if "type" in content:
                    print("content convert error", content["type"])
                pass
        return csv_list

    def main_parse_loop(self):
        print("start handler ===> ",
              time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        # initialize for parse html document
        self.generate_ztree_list()

        # parse meta json
        # main loop for parse all json data
        for key in self.id_to_tree:
            # filter meta data
            csv_header = None
            all_row_list = []
            element = self.id_to_tree[key]

            if key in ("report_info_1xxei832", "data_device_lists_1xxei832"):
                continue
            # self.logger.info("[main_parse_loop] id: {0}".format(key))
            # For debug
            # if key in ("64A058EECF45FF16", "5606D7895636F329", "5CDB7897EBBCAF75"
            #           "CA751A0B028D8C0F", "BCC3D08D1F18DA62", "682D36F5C4359F4A",
            #           "678A8D5FDB372271"):
            #    print("fu you\n")
            for index in range(1, self.max_json_size):
                try:
                    if key.replace("_1xxei832", "") in self.meta_json:
                        json_data_path = os.path.join(
                            self.home_directory, "data", "data_" + element["id"] + ".json")
                        if not os.path.exists(json_data_path):
                            json_data_path = os.path.join(
                                self.home_directory,
                                element["dataConfig"]["filePath"],
                                "data_" + element["id"] + ".json")
                            # self.logger.info("[main_parse_loop] json file path: {0} \n".format(json_data_path))
                        if not os.path.exists(json_data_path):
                            break
                        print("handle json path: ", json_data_path)
                        json_data_obj = self.json_load(json_data_path)
                        if json_data_obj == None:
                            break
                        csv_header = self.extract_header_from_json(
                            json_data_obj)
                        all_row_list.append(csv_header)
                        csv_content = self.convert_json(
                            json_data_obj, csv_header, key)
                        all_row_list = all_row_list + csv_content
                        break
                    else:

                        json_data_path = os.path.join(
                            self.home_directory, "data", "data_" +
                                                         element["id"] + "_" + str(index) + ".json")
                        if not os.path.exists(json_data_path):
                            json_data_path = os.path.join(
                                self.home_directory,
                                element["dataConfig"]["filePath"], "data_" +
                                                                   element["id"] + "_" + str(index) + ".json")
                            # self.logger.info("[main_parse_loop] json file path: {0} \n".format(json_data_path))
                        if not os.path.exists(json_data_path):
                            break

                        # print("handle json path: >>>  ", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) , "  ", json_data_path)
                        json_data_obj = self.json_load(json_data_path)
                        # if key == "BD5A961A61A973E9":
                        #     print("---------------------------------------------------------------------")
                        #     print("handle json path: <<<  ", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) , index, json_data_path)
                        if json_data_obj == None:
                            break
                        if index == 1:
                            # CHANGE 增加无columns文件处理
                            if "columns" not in json_data_obj:
                                csv_header = self.extract_header_from_content(
                                    json_data_obj)
                                all_row_list.append(csv_header)
                                csv_content = self.convert_content(
                                    json_data_obj, csv_header, key)
                                all_row_list = all_row_list + csv_content
                            else:
                                csv_header = self.extract_header_from_json(
                                    json_data_obj)
                                all_row_list.append(csv_header)
                                csv_content = self.convert_json(
                                    json_data_obj, csv_header, key)
                                all_row_list = all_row_list + csv_content
                            # all_row_list.append(csv_content)
                        else:
                            if "columns" not in json_data_obj:
                                csv_content = self.convert_content(
                                    json_data_obj, csv_header, key)
                                all_row_list = all_row_list + csv_content
                            else:
                                csv_content = self.convert_json(
                                    json_data_obj, csv_header, key)
                                all_row_list = all_row_list + csv_content
                except Exception as e:
                    # self.logger.info(
                    #     "[main_parse_loop] table name: {0} is initial failed\n"
                    #     .format(index))
                    pass
            # persistence the list data
            if len(all_row_list) > 1:
                # continue
                self.save_csv_by_tree_node(all_row_list, element)
        print("end handler <=== ",
              time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

def delete_files_in_directory(directory_path):
    try:
        # 确保目录存在
        if not os.path.exists(directory_path):
            print(f"目录 '{directory_path}' 不存在。")
            return

        # 获取目录中的所有文件和子目录
        files_and_dirs = os.listdir(directory_path)

        # 删除所有文件
        for item in files_and_dirs:
            item_path = os.path.join(directory_path, item)

            if os.path.isfile(item_path):
                os.remove(item_path)

        print(f"目录 '{directory_path}' 中的所有文件已被删除。")

    except Exception as e:
        print(f"发生错误: {e}")

def main(argv):
    urlpath = None
    root_path = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
    log_path = os.path.join(root_path, "logs")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    file_handler = logging.FileHandler(
        os.path.join(log_path, "meiya_json_parser.log"))
    file_handler.setFormatter(
        logging.Formatter(fmt='[%(asctime)s]: %(levelname)s %(message)s',
                          datefmt="%Y-%m-%d %H:%M:%S"))
    logging.getLogger(__name__).setLevel(logging.INFO)
    logging.getLogger(__name__).addHandler(file_handler)
    logging.getLogger(__name__).addHandler(logging.StreamHandler())

    try:
        opts, _ = getopt.getopt(argv, "f:u:o:",
                                ["htmlfile=", "urlpath=", "outputfile="])
    except getopt.GetoptError:
        print('meiya_html_parse.py -f <htmlfile> -u <urlpath> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -f <htmlfile> -u <urlpath> -o <outputfile>')
            sys.exit()
        elif opt in ("-f", "--htmfile"):
            htmlfile = arg
        elif opt in ("-u", "--urlpath"):
            urlpath = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    urlpath = urlpath if urlpath else "file:///" + htmlfile
    logging.getLogger(__name__).info(
        "[main] html_file: {0}, url_path: {1}, output: {2}".format(
            htmlfile, urlpath, outputfile))

    # start main loop
    meiya_parser = MeiyaParser()
    meiya_parser.set_home_directory(htmlfile)
    meiya_parser.set_out_put_path(outputfile)
    meiya_parser.main_parse_loop()
    meiya_parser.save_catalog()
    # test
    directory_to_delete = "C:\\Users\\Administrator\\Desktop\\新版_html\\新版_html\\output_csv"
    delete_files_in_directory(directory_to_delete)


if __name__ == "__main__":
    timer = timeit.Timer(lambda: main(sys.argv[1:]))
    execution_time = timer.timeit(number=10)  # 执行代码10次
    print(f"代码执行平均时间：{execution_time / 10} 秒")
    # main(sys.argv[1:])
