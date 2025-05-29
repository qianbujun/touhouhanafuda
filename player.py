# player.py
from card import card
import random

class Player:
    def __init__(self, name):
        self.name = name          # 玩家名称
        self.hand = []            # 手牌
        self.collected = []       # 收集的牌
        self.score = 0            # 得分
        self.yizhong = []  # 已得到的役
        
    def draw(self, deck, num = 8):
        """从牌堆抽取指定数量的牌"""
        for _ in range(num):
            if deck:
                self.hand.append(deck.pop(0))
    
    def initial_draw(self, deck):
        """初始发牌：抽取8张手牌"""
        self.draw(deck, 8)
    
    def discard(self, card_index, field):
        """打出指定索引的手牌到场上"""
        
        if 0 <= card_index < len(self.hand):
            print(f"{self.name} 打出 {self.hand[card_index].name} 到场上")
            field.append(self.hand.pop(card_index))


