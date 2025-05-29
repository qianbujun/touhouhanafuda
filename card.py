# card.py
card_types = ('scene','item','spot','character')
class card:
    def __init__(self, name, card_type, card_id):
        self.name = name
        self.card_type = card_type
        self.card_id = card_id
    def initialize_cards():
        card_list = [
            # 景色牌 (scene) - 共5张
            card("博丽神社的祭典", "scene",1),
            card("迷失竹林的月圆之夜", "scene",2),
            card("妖怪之山的红叶", "scene",4),
            card("幽灵客船之旅", "scene",8),
            card("盛开的樱花树", "scene",11),

            # 物品牌 (item) - 共9张
            card("灵梦的御币", "item",1),
            card("早苗的御币", "item",3),
            card("隙间", "item",5),
            card("小石子帽子", "item",6),
            card("国士无双之药", "item",7),
            card("致幻蘑菇", "item",9),
            card("魔导书", "item",10),
            card("楼观剑和白楼剑", "item",11),
            card("琪露诺的战书", "item",12),

            # 地点牌 (spot) - 共10张
            card("博丽神社", "spot",1),
            card("迷失竹林", "spot",2),
            card("守矢神社", "spot",3),
            card("妖怪之山", "spot",4),
            card("地灵殿", "spot",6),
            card("永远亭", "spot",7),
            card("命莲寺", "spot",8),
            card("魔法森林", "spot",9),
            card("红魔馆", "spot",10),
            card("雾之湖", "spot",12),

            # 人物牌 (character) - 共24张
            card("博丽灵梦", "character",1),
            card("藤原妹红", "character",2),
            card("铃仙", "character",2),
            card("东风谷早苗", "character",3),
            card("泄矢诹访子", "character",3),
            card("射命丸文", "character",4),
            card("键山雏", "character",4),
            card("橙", "character",5),
            card("八云蓝", "character",5),
            card("八云紫", "character",5),
            card("古明地恋", "character",6),
            card("古明地觉", "character",6),
            card("八意永琳", "character",7),
            card("蓬莱山辉夜", "character",7),
            card("圣白莲", "character",8),
            card("村纱水蜜", "character",8),
            card("爱丽丝", "character",9),
            card("雾雨魔理沙", "character",9),
            card("蕾米莉亚", "character",10),
            card("十六夜咲夜", "character",10),
            card("魂魄妖梦", "character",11),
            card("西行寺幽幽子", "character",11),
            card("琪露诺", "character",12),
            card("大妖精", "character",12)
        ]
        return card_list


if __name__ == "__main__":
    card_list = card.initialize_cards()
    print("Card list initialized with {} cards.".format(len(card_list)))
    # sort by cards_id
    card_list.sort(key=lambda x: x.cards_id)
    for card_item in card_list:
        print("Card ID: {}, Name: {}, Type: {}".format(card_item.cards_id, card_item.name, card_item.card_type))
        

