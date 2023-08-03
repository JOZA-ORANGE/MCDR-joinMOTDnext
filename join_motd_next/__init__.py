import os
import random
import re
from typing import List, Dict
from mcdreforged.api.all import *
from join_motd_next.default_config import default_config

__mcdr_server: PluginServerInterface
CONFIG_FILE = os.path.join('config', 'join_motd_next.json')


def send_message(server: PluginServerInterface, messages: RTextList, scope: str, player: str = None):
    if scope == "player":
        server.tell(player, messages)
    elif scope == "all":
        server.say(messages)


def getDay() -> str:
    daycount_nbt = __mcdr_server.get_plugin_instance('daycount_nbt')
    return daycount_nbt.getday()


def format_message(message: str, player: str) -> str:
    if message is not None:
        placeholders = re.findall(r'\{(\w+)}', message)
        for placeholder in placeholders:
            if placeholder in random_text:
                value = random.choice(random_text[placeholder])
                message = message.replace("{" + placeholder + "}", value)
        message = message.format(player=player, date=str(getDay()))
    return message


def msg_to_rtextlist(row: List[Dict], player: str) -> RTextList:
    rtextlist = RTextList()

    for unit in row:
        tag_type = unit.get('tag_type')
        content = unit.get('content')
        value = unit.get('value')
        hover = unit.get('hover')
        content = format_message(content, player)
        value = format_message(value, player)
        hover = format_message(hover, player)
        if tag_type == "url" or tag_type == "u":
            rtext = RText(content).c(RAction.open_url, value)
        elif tag_type == "copy" or tag_type == "c":
            rtext = RText(content).c(RAction.copy_to_clipboard, value)
        elif tag_type == "command" or tag_type == "cmd":
            rtext = RText(content).c(RAction.run_command, value)
        elif tag_type == "fill" or tag_type == "f":
            rtext = RText(content).c(RAction.suggest_command, value)
        else:
            rtext = RText(content)
        if hover is not None:
            rtext.h(hover)
        rtextlist += rtext
    return rtextlist


def create_and_send_message(server: PluginServerInterface, message_list: List[List[Dict]], scope: str, player: str):
    for row in message_list:
        rtextlist = msg_to_rtextlist(row, player)
        send_message(server, rtextlist, scope, player)


# 玩家加入
def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    if player.startswith(config["bot_prefix"]) or not config["player_join"]["enable"]:
        return
    create_and_send_message(server,
                            join_info,
                            config["player_join"]["scope"],
                            player)


# 玩家离开
def on_player_left(server: PluginServerInterface, player: str):
    if player.startswith(config["bot_prefix"]) or not config["player_left"]["enable"]:
        return
    create_and_send_message(server,
                            left_info,
                            config["player_left"]["scope"],
                            player)


def extract_tag_info(cfg_msg) -> list:
    messages = []
    for message in cfg_msg:
        row = re.findall(r'<(\w+)\s*(.*?)>(.*?)</\1>', message)
        rows = []
        for unit in row:
            unit_dict = {"tag_type": unit[0], "content": unit[2], "value": None, "hover": None}
            if unit[1] != "":
                attributes = re.findall(r'\((\w+)=(.*?)\)', unit[1])
                for attribute in attributes:
                    if attribute[0] == "v":
                        unit_dict["value"] = attribute[1]
                    elif attribute[0] == "h":
                        unit_dict["hover"] = attribute[1]
                    else:
                        unit_dict[attribute[0]] = attribute[1]
            rows.append(unit_dict)
        messages.append(rows)
    return messages


def update_config(source: CommandSource):
    global config, join_info, left_info, random_text
    # 读取配置文件
    server = source.get_server()
    config = server.as_plugin_server_interface().load_config_simple(file_name=CONFIG_FILE,
                                                                    default_config=default_config, in_data_folder=False)
    join_info = extract_tag_info(config["player_join"]["message"])
    left_info = extract_tag_info(config["player_left"]["message"])
    random_text = config["random_text"]
    if source.is_player:
        source.reply("配置文件已重载")


def print_join(source: PlayerCommandSource):
    if source.is_console:
        source.reply("该指令只能由玩家执行")
        return
    server = source.get_server()
    create_and_send_message(server.as_plugin_server_interface(),
                            join_info,
                            config["player_join"]["scope"],
                            source.player)


def print_left(source: PlayerCommandSource):
    if source.is_console:
        source.reply("该指令只能由玩家执行")
        return
    server = source.get_server()
    create_and_send_message(server.as_plugin_server_interface(),
                            left_info,
                            config["player_left"]["scope"],
                            source.player)
    pass


# 插件载入
def on_load(server: PluginServerInterface, old_module):
    global config, join_info, left_info, random_text, __mcdr_server
    __mcdr_server = server
    # 读取配置文件
    config = server.load_config_simple(file_name=CONFIG_FILE, default_config=default_config, in_data_folder=False)
    join_info = extract_tag_info(config["player_join"]["message"])
    left_info = extract_tag_info(config["player_left"]["message"])
    random_text = config["random_text"]
    # 构建指令
    server.register_help_message('!!motd', '在玩家加入游戏时向其发送更加多样的信息')
    server.register_command(
        Literal("!!motd").
        then(
            Literal('reload').runs(lambda src: src.has_permission(3)).runs(update_config)
        ).
        then(
            Literal('test').
            then(
                Literal('join').requires(lambda src: src.has_permission(3)).runs(print_join)
            ).
            then(
                Literal('left').requires(lambda src: src.has_permission(3)).runs(print_left)
            )
        )
    )
