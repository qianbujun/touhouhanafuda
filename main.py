# main.py
from card import card
from player import Player
import random

predefined_cps = {
    # 预定义的 CP 组合（按 card_id 匹配）
    ("博丽灵梦", "雾雨魔理沙"),
    ("雾雨魔理沙", "东风谷早苗"),
    ("博丽灵梦", "东风谷早苗"),
    ("博丽灵梦", "八云紫"),
    ("蓬莱山辉夜", "藤原妹红"),
    ("铃仙","八意永琳"),
    ("古明地觉","蕾米莉亚"),
    ("泄矢诹访子","琪露诺"),
    ("藤原妹红", "琪露诺"),
}

cp_combinations = {
        # 主角组
        "主角组1": {
            "chars": ["博丽灵梦", "雾雨魔理沙"],
            "scenes": ["妖怪之山的红叶", "博丽神社的祭典", "幽灵客船之旅", "盛开的樱花树"]
        },
        "主角组2": {
            "chars": ["雾雨魔理沙", "东风谷早苗"],
            "scenes": ["幽灵客船之旅"]
        },
        "主角组3": {
            "chars": ["博丽灵梦", "东风谷早苗"],
            "scenes": ["幽灵客船之旅"]
        },
        
        # 其他组合
        "巫女组": {
            "chars": ["博丽灵梦", "东风谷早苗"],
            "scenes": ["妖怪之山的红叶", "博丽神社的祭典"]
        },
        "守矢组": {
            "chars": ["泄矢诹访子", "东风谷早苗"],
            "scenes": ["妖怪之山的红叶"]
        },
        "白村组": {
            "chars": ["村纱水蜜", "圣白莲"],
            "scenes": ["幽灵客船之旅"]
        },
        "青蛙组": {
            "chars": ["琪露诺", "泄矢诹访子"],
            "spots": ["雾之湖"]  # 雾之湖是 spot 类型
        },
        "八云家组": {
            "chars": ["橙", "八云蓝", "八云紫"],
            "scenes": []
        },
        "幽冥组": {
            "chars": ["魂魄妖梦", "西行寺幽幽子"],
            "scenes": ["盛开的樱花树"]
        },
        "冰火组": {
            "chars": ["藤原妹红", "琪露诺"],
            "scenes": ["迷失竹林的月圆之夜"]
        },
}

    # 永夜组单独定义
yrn_combinations = {
        "结界组": {
            "chars": ["博丽灵梦", "八云紫"],
            "scenes": ["迷失竹林的月圆之夜"]
        },
        "咏唱组": {
            "chars": ["雾雨魔理沙", "爱丽丝"],
            "scenes": ["迷失竹林的月圆之夜"]
        },
        "红魔组": {
            "chars": ["蕾米莉亚", "十六夜咲夜"],
            "scenes": ["迷失竹林的月圆之夜"]
        },
        "幽冥组": {
            "chars": ["魂魄妖梦", "西行寺幽幽子"],
            "scenes": ["迷失竹林的月圆之夜"]
        },
        "永远组": {
            "chars": ["八意永琳", "蓬莱山辉夜"],
            "scenes": ["迷失竹林的月圆之夜"]
        },
        "不死组": {
            "chars": ["蓬莱山辉夜", "藤原妹红"],
            "scenes": ["迷失竹林的月圆之夜"]
        }
    }




def build_pair_matrix(hand):
    """
    构建 8x8 配对矩阵，matrix[i][j] = 1 表示第 i 张牌与第 j 张牌可以配对
    Args:
        hand: 玩家的初始手牌（已确保全为角色牌）
    Returns:
        list[list[int]]: 8x8 的配对矩阵
    """
    matrix = [[0]*8 for _ in range(8)]  # 初始化 8x8 矩阵
    # 填充矩阵
    for i in range(8):
        for j in range(i+1 , 8):
            if hand[i].card_id == hand[j].card_id and i!= j :
                # 同 card_id
                matrix[i][j] = 1
                matrix[j][i] = 1
                
                
            else:
                # 检查是否属于预定义的 CP 组合（按 card_id 判断）
                pair = tuple([hand[i].name, hand[j].name])
                if pair in predefined_cps:
                    matrix[i][j] = 1
                    matrix[j][i] = 1
    return matrix





def can_form_perfect_match(matrix):
    """
    检测是否存在完美匹配（4 对互不重叠的有效配对）
    Args:
        matrix: 8x8 的配对矩阵
    Returns:
        bool: 是否存在完美匹配
    """
    n = len(matrix)
    used = [False] * n  # 标记哪些牌已被使用

    def backtrack(pairs):
        if len(pairs) == 4:
            return True  # 找到 4 对有效配对

        for i in range(n):
            if not used[i]:
                for j in range(i + 1, n):
                    if not used[j] and matrix[i][j] == 1:
                        # 尝试配对 (i, j)
                        used[i] = used[j] = True
                        pairs.append((i, j))
                        if backtrack(pairs):
                            return True
                        # 回溯
                        pairs.pop()
                        used[i] = used[j] = False
                break  # 只需尝试第一个未使用的牌
        return False

    return backtrack([])


def checkhandcp(hand):
    """
    检测初始手牌中是否存在 CP 天胡（4 对有效 CP 组合）
    Args:
        hand: 玩家的初始手牌（已确保全为角色牌）
    Returns:
        int: 1 表示满足天胡条件，0 表示不满足
    """
    # 构建配对矩阵
    matrix = build_pair_matrix(hand)
    # 检测是否存在完美匹配
    return 1 if can_form_perfect_match(matrix) else 0


def checkhand(list1):
    # 手牌是否天和
    
    # 检查是否全是地点牌
    num = 8
    for item in list1:
        if item.card_type == 'character':
            num -= 1
        if item.card_type == 'spot':
            num += 1
    if num == 16: # 全是地点牌
        return 3
    if num == 0: # 全是角色牌
        return checkhandcp(list1)
    
    
    list2 = [0,0,0,0,0,0,0,0,0,0,0,0]
    for item in list1:
        list2[item.card_id-1] += 1
        
    list2.sort(reverse=True)
    
    # 手四和双手四
    if list2[0] == 4:
        if list2[1] == 4 :
            return 2
        return 1
    
    
    
    return 0



def checkdeck(list1):
    # 场札是否合规
    list2 = [0,0,0,0,0,0,0,0,0,0,0,0]
    for item in list1:
        list2[item.card_id-1] += 1
    list2.sort(reverse=True)
    if list2[0] == 4:
        if list2[1] == 4 :
            return 2
        return 1
    return 0



def get_card(field, player, deck):
    """
    处理玩家取牌逻辑，正确维护场上牌堆状态
    Args:
        field: 场上牌列表
        player: 当前操作玩家
        deck: 牌堆
    Returns:
        None
    """
    # 处理场上最后一张牌与已有牌的匹配
    if field:  # 确保场上还有牌
        target_card = field[-1]
        get_id = target_card.card_id
        
        # 收集匹配牌
        matched_cards = [card for card in field[:-1] if card.card_id == get_id]
        
        if matched_cards:
            print(f"\033[0;31;42m场上有 {len(matched_cards)} 张与新牌相同的牌，是 {[card.name for card in matched_cards]}\033[0m")
            
            # 根据匹配数量处理不同情况
            if len(matched_cards) == 1:
                chosen_card = matched_cards[0]
                print(f"\033[0;31;47m{player.name} 拿走了 {chosen_card.name} 牌\033[0m")
                player.collected.append(chosen_card)
                field.remove(chosen_card)  # 从列表中移除指定牌
                
            elif len(matched_cards) == 2:
                # 提供选择界面
                choice = int(input(f"\033[0;31;47m{player.name} 请选择要收集的牌的索引 (0-1): \033[0m"))
                chosen_card = matched_cards[choice]
                print(f"\033[0;31;47m{player.name} 选择了 {chosen_card.name} 牌\033[0m")
                player.collected.append(chosen_card)
                field.remove(chosen_card)  # 从列表中移除指定牌
                
            elif len(matched_cards) >= 3:
                # 收集所有匹配牌
                for matched_card in matched_cards:
                    print(f"\033[0;31;47m{player.name} 拿走了 {matched_card.name} 牌\033[0m")
                    player.collected.append(matched_card)
                    field.remove(chosen_card)  # 从列表中移除指定牌
            
            # 收集目标牌
            player.collected.append(target_card)
            field.pop()  # 移除最后一张牌（目标牌）

    # 从牌堆抽取新牌补充到场上
    if deck:
        new_card = deck.pop(0)
        field.append(new_card)
        print(f"\033[0;30;42m牌堆翻出了 {new_card.name} 牌，场上的牌现在是: {[card.name for card in field]}\033[0m")
    
    # 处理新牌的匹配逻辑（重复上面的流程）
    if len(field) >= 1:  # 确保场上还有牌
        target_card = field[-1]
        get_id = target_card.card_id
        
        matched_cards = [card for card in field[:-1] if card.card_id == get_id]
        
        if matched_cards:
            print(f"\033[0;31;42m场上有 {len(matched_cards)} 张与新牌相同的牌，是 {[card.name for card in matched_cards]}\033[0m")
            
            if len(matched_cards) == 1:
                chosen_card = matched_cards[0]
                print(f"\033[0;31;47m{player.name} 拿走了 {chosen_card.name} 牌\033[0m")
                player.collected.append(chosen_card)
                field.remove(chosen_card)
                
            elif len(matched_cards) == 2:
                choice = int(input(f"\033[0;31;47m{player.name} 请选择要收集的牌的索引 (0-{len(matched_cards)-1}): \033[0m"))
                chosen_card = matched_cards[choice]
                print(f"\033[0;31;47m{player.name} 选择了 {chosen_card.name} 牌\033[0m")
                player.collected.append(chosen_card)
                field.remove(chosen_card)
                
            elif len(matched_cards) >= 3:
                for matched_card in matched_cards:
                    print(f"\033[0;31;47m{player.name} 拿走了 {matched_card.name} 牌\033[0m")
                    player.collected.append(matched_card)
                field[:] = [card for card in field[:-1] if card.card_id != get_id]
            
            player.collected.append(target_card)
            field.pop()  # 正确移除最后一张牌

    return field  # 返回修改后的场牌状态


def check_cp_combinations(collected_cards):
    """
    检查玩家收集的牌中满足的 CP 组合数量
    Args:
        collected_cards: 玩家收集的所有牌列表
    Returns:
        tuple: (普通CP组合数量, 普通组合役种列表, 永夜组是(1)否(0)含有)
    """
    # 提取角色、场景、地点
    char_set = set(c.name for c in collected_cards if c.card_type == 'character')
    scene_set = set(c.name for c in collected_cards if c.card_type == 'scene')
    spot_set = set(c.name for c in collected_cards if c.card_type == 'spot')

    yizhong_cp = []  # 用于记录满足的组合名称
    cp_count = 0
    yrn_count = 0

    # 检查普通 CP 组合
    for combo_name, combo in cp_combinations.items():
        # 检查角色是否齐全
        if not all(char in char_set for char in combo["chars"]):
            continue

        # 场景条件（scene 类型）
        if "scenes" in combo and combo["scenes"]:
            if not any(scene in scene_set for scene in combo["scenes"]):
                continue

        # 地点条件（spot 类型）
        if "spots" in combo and combo["spots"]:
            if not any(spot in spot_set for spot in combo["spots"]):
                continue

        # 满足条件，计数并记录组合名称
        cp_count += 1
        yizhong_cp.append(combo_name)

    # 检查永夜组组合（添加这部分）
    
    for combo_name, combo in yrn_combinations.items():
        # 检查角色是否齐全
        if not all(char in char_set for char in combo["chars"]):
            continue
            
        # 场景条件
        if "scenes" in combo and combo["scenes"]:
            if not any(scene in scene_set for scene in combo["scenes"]):
                continue
                
        # 满足永夜组条件
        cp_count += 1
        yizhong_cp.append('永夜组')
        break  # 只需满足一个永夜组组合

    return cp_count, yizhong_cp

    

# def check_cp_combinations(collected_cards):
#     """
#     检查玩家收集的牌中满足的 CP 组合数量
#     Args:
#         collected_cards: 玩家收集的所有牌列表
#     Returns:
#         tuple: (普通CP组合数量, 普通组合役种列表, 永夜组是(1)否(0)含有)
#     """
#     # 提取角色、场景、地点
#     char_set = set(c.name for c in collected_cards if c.card_type == 'character')
#     scene_set = set(c.name for c in collected_cards if c.card_type == 'scene')
#     spot_set = set(c.name for c in collected_cards if c.card_type == 'spot')

#     yizhong_cp = []  # 用于记录满足的组合名称

#     # 定义普通 CP 组合（不包含永夜组）
#     cp_count = 0
#     for combo_name, combo in cp_combinations.items():
#         # 检查角色是否齐全
#         if not all(char in char_set for char in combo["chars"]):
#             continue

#         # 场景条件（scene 类型）
#         if "scenes" in combo and combo["scenes"]:
#             if not any(scene in scene_set for scene in combo["scenes"]):
#                 continue

#         # 地点条件（spot 类型）
#         if "spots" in combo and combo["spots"]:
#             if not any(spot in spot_set for spot in combo["spots"]):
#                 continue

#         # 满足条件，计数并记录组合名称
#         cp_count += 1
#         yizhong_cp.append(combo_name)

#     # 检查永夜组（最多只计1个）
#     yrn_count = 0
#     for combo in yrn_combinations.values():
#         if all(char in char_set for char in combo["chars"]):
#             if not combo["scenes"] or any(scene in scene_set for scene in combo["scenes"]):
#                 yrn_count = 1
#                 break
#     return cp_count, yizhong_cp, yrn_count



def score(player,ids):
    # 计算玩家得分，如果玩家有新的役并选择结束游戏返回1
    """
    计算玩家得分
    Args:
        player: 玩家对象
        field: 场上的牌列表
    Returns:
        int: 玩家总得分
    """
    collected = player.collected
    total_score = 0
    rm = False  # 用于标记是否移除迷失竹林的月圆之夜
    yizhong = []
    # 转换为名称列表便于判断
    scene_names = [c.name for c in collected if c.card_type == 'scene']
    item_names = [c.name for c in collected if c.card_type == 'item']
    spot_names = [c.name for c in collected if c.card_type == 'spot']
    char_names = [c.name for c in collected if c.card_type == 'character']
    
    yyc_chars = ["博丽灵梦", "八云紫", "雾雨魔理沙", "爱丽丝", "蕾米莉亚", "十六夜咲夜", "西行寺幽幽子", "魂魄妖梦" ]
    
    
    # 检查景色牌
    if len(scene_names) == 5:
        # 五景：集齐五张景色牌
        total_score += 10
        yizhong.append("五景")
        
    # 如果不为五景，在无永夜抄自机的情况下，移除迷失竹林的月圆之夜
    elif "迷失竹林的月圆之夜" in scene_names:
        # 检查永夜抄自机
        if any(c in char_names for c in yyc_chars):
            pass
        else :
            # scene 移除 迷失竹林的月圆之夜
            rm = True
            scene_names.remove("迷失竹林的月圆之夜")
    
    
    if len(scene_names) >= 3 and len(scene_names) != 5:
        # 四景：集齐四张景色牌
        if len(scene_names) == 4:
            total_score += 8
            yizhong.append("四景")
        # 三景：集齐三张景色牌
        if len(scene_names) == 3:
            total_score += 5
            yizhong.append("三景")
    
    # 判断完三四景后需将迷失竹林的月圆之夜加回
    if rm :
        scene_names.append("迷失竹林的月圆之夜")
    
    
    # CP组合役种
    cp_count, yizhong_cp = check_cp_combinations(collected)
    yizhong += yizhong_cp
    total_score += cp_count*3
    
    # 合札检测
    if ids != []:
        list2 = [0,0,0,0,0,0,0,0,0,0,0,0]
        num = 8
        for item in collected:
            list2[item.card_id-1] += 1
        
        for hezha in ids:
            if list2[hezha-1] == 4:
                total_score += 4
                for hespcard in collected:
                    if hespcard.card_id == hezha and hespcard.card_type == 'spot':
                        yizhong.append(f"合札{hespcard.name}")
    
    
    # 武器库：三张武器牌
    weapon_items = ["灵梦的御币", "早苗的御币", "楼观剑和白楼剑"]
    if all(item in item_names for item in weapon_items):
        total_score += 5
        yizhong.append("武器库")
        
    
    # 信仰战争：博丽神社、守矢神社、命莲寺
    faith_spots = ["博丽神社", "守矢神社", "命莲寺"]
    if all(spot in spot_names for spot in faith_spots):
        total_score += 5
        yizhong.append("信仰战争")
        if "巫女组" in yizhong :
            yizhong.remove("巫女组")
    
    
    
    # 物品牌：收集5张后每多1张加1分
    item_count = len(item_names)
    if item_count >= 5:
        total_score += item_count - 5 + 1
        yizhong.append(f"物品牌{item_count}张")
    
    # 地点牌：收集5张后每多1张加1分
    spot_count = len(spot_names)
    if spot_count >= 5:
        total_score += spot_count - 5 + 1
        yizhong.append(f"地点牌{spot_count}张")
    
    # 角色牌：收集10张后每多1张加1分
    char_count = len(char_names)
    if char_count >= 10:
        total_score += char_count - 10 + 1
        yizhong.append(f"角色牌{char_count}张")

    if yizhong != player.yizhong :
        print(f"\033[0;31;47m{player.name} 的役种: {', '.join(yizhong)}\033[0m")
        # 选择继续或者结束
        choice = input(f"\033[0;31;47m{player.name} 是否继续游戏？1.继续 2.结束: \033[0m")
        
        if choice == '2':
            player.yizhong = yizhong
            player.score += total_score
            return 1
        else:
            print(f"\033[0;31;47m{player.name} 选择继续游戏\033[0m")
            player.yizhong = yizhong
            return 0
    return 0



def test_once_play(player1name, player2name):

    card_list = card.initialize_cards()
    deck = card_list.copy()
    random.shuffle(deck)
    s1 = 0
    flag = 0
    # 创建玩家
    player1 = Player(player1name)
    player2 = Player(player2name)
    # 初始发牌
    player1.initial_draw(deck)
    player2.initial_draw(deck)
    print(f"\033[0;31;47m{player1.name} 的初始手牌: {[str(card.name) for card in player1.hand]}\033[0m")
    s1 =  checkhand(player1.hand)
    if s1==1 or s1==2:
        player1.score = s1*4
        print(f"\033[0;31;47m{player1.name} 天和，获得 {player1.score} 分，结束游戏\033[0m")
    elif s1 == 3:
        player1.score = 10
        print(f"\033[0;31;47m{player1.name} 天和，获得 {player1.score} 分，结束游戏\033[0m")
    #@#print(f"{player2.name} 的初始手牌: {[str(card.name) for card in player2.hand]}")
    s1 =  checkhand(player2.hand)
    if s1==1 or s1==2:
        player2.score = s1*4
        print(f"\033[0;31;47m{player2.name} 天和，获得 {player2.score} 分，结束游戏\033[0m")
    elif s1 == 3:
        player2.score = 10
        print(f"\033[0;31;47m{player2.name} 天和，获得 {player2.score} 分，结束游戏\033[0m")
    # 场札
    field = deck[:8]
    ids = []
    deck = deck[8:]
    print(f"\033[0;30;42m场上的牌: {[str(card.name) for card in field]}\033[0m")
    if(checkdeck(field)):
            print("\033[0;30;47m场上有四张相同的牌，流局\033[0m")
            
            
            
    
    #记录场上的地点牌
    ids.extend((int(card.card_id)) for card in field if card.card_type == 'spot')
    
    # 游戏正式开始
    while player2.hand != []:
        s1 += 1
        print("\033[0;31;47m================================+++++++++++=================================\033[0m")
        print("\033[0;31;47m================================第   "+ str(s1) +"   轮=================================\033[0m")
        print("\033[0;31;47m================================+++++++++++=================================\033[0m")
        # player1回合
        # 玩家1打出手牌
        print(f"\033[0;30;47m{player1.name} 的手牌: {[f'{idx+1}.{card.name}' for idx, card in enumerate(player1.hand)]}\033[0m")
        player1.discard(int(input("\033[0;30;47m输入手牌序号\033[0m"))-1, field)
        print(f"\033[0;30;42m场上的牌: {[str(card.name) for card in field]}\033[0m")
        get_card(field, player1, deck)
        #打印玩家1的收集牌
        print(f"\033[0;32;47m{player1.name} 的收集牌: {[str(card.name) for card in player1.collected]}\033[0m")
        flag = score(player1,ids)
        if flag :
            print(f"\033[0;31;47m{player1.name} 选择结束游戏\033[0m")
            flag = 1
            break
        print(f"\033[0;30;42m场上的牌: {[str(card.name) for card in field]}\033[0m")
        
        
        
        
        # player2回合
        # 玩家2打出手牌
        player2.discard(0, field)
        #@#print(f"\033[0;30;47m{player2.name} 的手牌: {[f'{idx+1}.{card.name}' for idx, card in enumerate(player2.hand)]}\033[0m")
        #@#print(f"\033[0;30;42m场上的牌: {[str(card.name) for card in field]}\033[0m")
        get_card(field, player2, deck)
        #打印玩家2的收集牌
        print(f"\033[0;32;47m{player2.name} 的收集牌: {[str(card.name) for card in player2.collected]}\033[0m")
        flag = score(player2,ids)
        if flag :
            print(f"\033[0;31;47m{player2.name} 选择结束游戏\033[0m")
            flag = 2
            break
        print(f"\033[0;30;42m场上的牌: {[str(card.name) for card in field]}\033[0m")
        
        
        
    # 游戏结束
    if flag == 0 :
        print("\033[0;31;47m流局，没有人获胜\033[0m")
        print(f"\033[0;32;47m{player1.name} 的收集牌: {[str(card.name) for card in player1.collected]}\033[0m")
        print(f"\033[0;32;47m{player2.name} 的收集牌: {[str(card.name) for card in player2.collected]}\033[0m")
    elif flag == 1 :
        print(f"\033[0;32;47m{player1.name} 的收集牌: {[str(card.name) for card in player1.collected]}\033[0m")
        print("\033[0;31;47m" + player1.name + " 获胜\033[0m")
        print("\033[0;31;47m" + player1.name + " 的得分: " + str(player1.score) + "\033[0m")
    elif flag == 2 :
        print(f"\033[0;32;47m{player2.name} 的收集牌: {[str(card.name) for card in player2.collected]}\033[0m")
        print("\033[0;31;47m" + player2.name + " 获胜\033[0m")
        print("\033[0;31;47m" + player2.name + " 的得分: " + str(player2.score)+ "\033[0m")
        print("\033[0;31;47m" + player2.name + " 的役种: " + str(player2.yizhong)+ "\033[0m")



if __name__ == "__main__":
    # 测试一次游戏
    
    print("#### 玩家 VS baka ####")
    print("baka永远只会打自己手牌的第一张")
    test_once_play("玩家", "baka")