import re

from mcdreforged.api.all import *
from join_motd_next.default_config import default_config
from daycount_nbt import getday


def send_message(server: PluginServerInterface, messages: RTextList, scope: str, player: str = None):
    if scope == "player":
        server.tell(player, messages)
    elif scope == "all":
        server.say(messages)


def create_and_send_message(server: PluginServerInterface, message_list: list[list[dict]], scope: str, player: str):
    for row in message_list:
        rtextlist = RTextList()
        for unit in row:
            tag_type = unit.get('tag_type')
            content = unit.get('content')
            value = unit.get('value')
            hover = unit.get('hover')
            content = content.format(player=player, date=str(getday())) if content is not None else content
            value = value.format(player=player, date=str(getday())) if value is not None else value
            hover = hover.format(player=player, date=str(getday())) if hover is not None else hover
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


# 插件载入
def on_load(server: PluginServerInterface, old_module):
    global config
    global join_info
    global left_info
    # 读取配置文件
    config = server.load_config_simple('join_motd_next.json', default_config)
    join_info = extract_tag_info(config["player_join"]["message"])
    left_info = extract_tag_info(config["player_left"]["message"])
