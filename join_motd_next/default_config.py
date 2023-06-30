default_config = {
    # 假人前缀:具有此前缀的玩家将被认为是假人,自动过滤以此前缀开头的玩家
    "bot_prefix": "bot_",
    # 当玩家加入服务器时
    "player_join": {
        # 是否启用这个信息提示
        "enable": True,
        # 消息提示范围(个人:player/全服:all)
        "scope": "player",
        # 提示的信息
        "message": [
            "<text>§5{player}§r加入了游戏</text>",
            "<text>{hitokoto}</text>",
        ]
    },
    # 当玩家离开服务器时
    "player_left": {
        # 是否启用这个信息提示
        "enable": True,
        # 消息提示范围(个人:player/全服:all)
        "scope": "player",
        # 提示的信息
        "message": [
            "<text>§5{player}§r离开了游戏</text>"
        ]
    },
    # 随机文本
    "random_text": {
        "hitokoto": [
            "内心湛然，则无往而不乐",
            "§6万法缘生，皆系缘分§r",
        ]
    }
}
