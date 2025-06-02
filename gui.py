# gui.py
'''
目前问题
1.流局会报错
2.收集的牌会显示框且过长记得换行
3.翻开的牌6个一排
4.注意不要让字和手牌重叠，其他的也不要重叠
'''


import pygame
import sys
import os
import random

# Assuming card.py, player.py, and parts of main.py are in the same directory or accessible
from card import card
from player import Player
# Import necessary functions and data from your main.py
# We'll need to be careful about what we import to avoid circular dependencies
# or re-running __main__ blocks if main.py also has one.
# It's better to put shared data like cp_combinations in a separate data.py if possible.
# For now, I'll copy them or assume they are accessible.

# --- Data from main.py (or a shared data module) ---
predefined_cps = {
    ("博丽灵梦", "雾雨魔理沙"), ("雾雨魔理沙", "东风谷早苗"), ("博丽灵梦", "东风谷早苗"),
    ("博丽灵梦", "八云紫"), ("蓬莱山辉夜", "藤原妹红"), ("铃仙","八意永琳"),
    ("古明地觉","蕾米莉亚"), ("泄矢诹访子","琪露诺"), ("藤原妹红", "琪露诺"),
}

cp_combinations = {
    "主角组1": {"chars": ["博丽灵梦", "雾雨魔理沙"], "scenes": ["妖怪之山的红叶", "博丽神社的祭典", "幽灵客船之旅", "盛开的樱花树"]},
    "主角组2": {"chars": ["雾雨魔理沙", "东风谷早苗"], "scenes": ["幽灵客船之旅"]},
    "主角组3": {"chars": ["博丽灵梦", "东风谷早苗"], "scenes": ["幽灵客船之旅"]},
    "巫女组": {"chars": ["博丽灵梦", "东风谷早苗"], "scenes": ["妖怪之山的红叶", "博丽神社的祭典"]},
    "守矢组": {"chars": ["泄矢诹访子", "东风谷早苗"], "scenes": ["妖怪之山的红叶"]},
    "白村组": {"chars": ["村纱水蜜", "圣白莲"], "scenes": ["幽灵客船之旅"]},
    "青蛙组": {"chars": ["琪露诺", "泄矢诹访子"], "spots": ["雾之湖"]},
    "八云家组": {"chars": ["橙", "八云蓝", "八云紫"], "scenes": []},
    "幽冥组": {"chars": ["魂魄妖梦", "西行寺幽幽子"], "scenes": ["盛开的樱花树"]},
    "冰火组": {"chars": ["藤原妹红", "琪露诺"], "scenes": ["迷失竹林的月圆之夜"]},
}

yrn_combinations = {
    "结界组": {"chars": ["博丽灵梦", "八云紫"], "scenes": ["迷失竹林的月圆之夜"]},
    "咏唱组": {"chars": ["雾雨魔理沙", "爱丽丝"], "scenes": ["迷失竹林的月圆之夜"]},
    "红魔组": {"chars": ["蕾米莉亚", "十六夜咲夜"], "scenes": ["迷失竹林的月圆之夜"]},
    "幽冥组": {"chars": ["魂魄妖梦", "西行寺幽幽子"], "scenes": ["迷失竹林的月圆之夜"]}, # Note: Duplicates key in main.py, Py dicts don't allow this
    "永远组": {"chars": ["八意永琳", "蓬莱山辉夜"], "scenes": ["迷失竹林的月圆之夜"]},
    "不死组": {"chars": ["蓬莱山辉夜", "藤原妹红"], "scenes": ["迷失竹林的月圆之夜"]}
}
# Ensure '幽冥组' in yrn_combinations has a unique interaction if needed, or consolidate
# For now, let's assume the last definition of "幽冥组" under yrn_combinations is intended for it.
# If "幽冥组" should be in both cp_combinations and yrn_combinations with different scenes,
# the logic in check_cp_combinations needs to handle that.
# The provided check_cp_combinations might double count or pick one.
# For simplicity, I'll assume yrn_combinations are distinct or additive.

# --- Helper functions from main.py (adapted for GUI) ---
def build_pair_matrix(hand_cards): # hand_cards is a list of card objects
    matrix = [[0]*8 for _ in range(8)]
    for i in range(8):
        for j in range(i + 1, 8):
            if hand_cards[i].card_id == hand_cards[j].card_id:
                matrix[i][j] = matrix[j][i] = 1
            else:
                pair_names = tuple(sorted((hand_cards[i].name, hand_cards[j].name)))
                # Check both (a,b) and (b,a) if predefined_cps is not consistently sorted
                if pair_names in predefined_cps or \
                   (pair_names[1],pair_names[0]) in predefined_cps :
                    matrix[i][j] = matrix[j][i] = 1
    return matrix

def can_form_perfect_match(matrix):
    n = len(matrix)
    used = [False] * n
    def backtrack(pairs_count, start_index):
        if pairs_count == 4:
            return True
        if start_index >= n -1: # Not enough cards left to form more pairs
            return False

        # Find the first unused card
        first_available = -1
        for i in range(start_index, n):
            if not used[i]:
                first_available = i
                break
        
        if first_available == -1: # No unused cards left, but haven't formed 4 pairs
             return False

        used[first_available] = True
        for j in range(first_available + 1, n):
            if not used[j] and matrix[first_available][j] == 1:
                used[j] = True
                if backtrack(pairs_count + 1, first_available + 1):
                    return True
                used[j] = False # backtrack
        used[first_available] = False # backtrack
        
        # Try skipping the current 'first_available' card if it couldn't form a pair
        # This ensures we explore all possibilities even if a card cannot be paired from its current position
        if backtrack(pairs_count, first_available + 1):
             return True
             
        return False
    return backtrack(0,0)


def checkhandcp(hand_cards):
    if len(hand_cards) != 8: return 0 # Must be 8 cards
    matrix = build_pair_matrix(hand_cards)
    return 1 if can_form_perfect_match(matrix) else 0

def checkhand(hand_cards): # list1 is hand_cards
    char_cards = [c for c in hand_cards if c.card_type == 'character']
    spot_cards = [c for c in hand_cards if c.card_type == 'spot']

    if len(spot_cards) == 8 and len(hand_cards) == 8: # All 8 are spot cards
        return 3 # 天和 - 全地点
    if len(char_cards) == 8 and len(hand_cards) == 8: # All 8 are character cards
        return checkhandcp(char_cards) # 天和 - CP

    # 手四和双手四 (Si-he in hand, Double Si-he in hand)
    # This logic applies if not all character or all spot.
    # It seems to imply that hand can contain mixed types for this check.
    # Original logic: list2 = [0]*12; for item in list1: list2[item.card_id-1]+=1
    # This counts card_id occurrences across ALL types in hand.
    
    counts = {}
    for item in hand_cards:
        counts[item.card_id] = counts.get(item.card_id, 0) + 1
    
    sorted_counts = sorted(counts.values(), reverse=True)
    
    if not sorted_counts: return 0

    if sorted_counts[0] >= 4:
        if len(sorted_counts) > 1 and sorted_counts[1] >= 4:
            return 2 # 双手四 (8 points)
        return 1 # 手四 (4 points)
    return 0


def checkdeck(field_cards): # list1 is field_cards
    if not field_cards: return 0
    counts = {}
    for item in field_cards:
        counts[item.card_id] = counts.get(item.card_id, 0) + 1
    sorted_counts = sorted(counts.values(), reverse=True)
    if not sorted_counts: return 0
    if sorted_counts[0] >= 4:
        # Original code implies if two different card_ids have 4 cards each on field, it's still 2.
        # This seems unlikely for a "流局" (draw) condition.
        # Usually, 4 of the *same* card_id on field is the issue.
        # Let's stick to the original interpretation: if the highest count is 4,
        # and the second highest is also 4 (meaning two sets of 4), it returns 2.
        # For a "流局" (redraw/abort game), usually it's just any 4 of the same card.
        # Re-interpreting "流局" to mean if ANY single card_id has 4 cards.
        if len(field_cards) >=4 and sorted_counts[0] >=4: # If any card appears 4 times
             # The original checkdeck returns 1 for one set of 4, 2 for two sets of 4.
             # This is usually for scoring, not "流局".
             # For "流局" if 4 identical cards on field at start:
             return 1 # Indicate a "流局" condition exists.
    return 0


def check_cp_combinations(collected_cards):
    char_set = set(c.name for c in collected_cards if c.card_type == 'character')
    scene_set = set(c.name for c in collected_cards if c.card_type == 'scene')
    spot_set = set(c.name for c in collected_cards if c.card_type == 'spot')

    yizhong_cp_list = []
    cp_score_count = 0 # Using this to sum scores, not just count combos

    # Check normal CP combinations
    for combo_name, combo in cp_combinations.items():
        if not all(char in char_set for char in combo["chars"]):
            continue
        if "scenes" in combo and combo["scenes"]:
            if not any(scene in scene_set for scene in combo["scenes"]):
                continue
        if "spots" in combo and combo["spots"]:
            if not any(spot in spot_set for spot in combo["spots"]):
                continue
        cp_score_count += 1 # Each combo worth 1 point base, then scaled in score()
        yizhong_cp_list.append(combo_name)

    # Check YRN combinations
    # If a YRN combo is made, it might be exclusive or additive.
    # Original code adds 1 to cp_count and appends '永夜组' if ANY yrn_combo is met.
    yrn_made = False
    for combo_name, combo in yrn_combinations.items(): # combo_name is like "结界组"
        if not all(char in char_set for char in combo["chars"]):
            continue
        if "scenes" in combo and combo["scenes"]: # YRN all have scenes
            if not any(scene in scene_set for scene in combo["scenes"]): # Needs specific scene "迷失竹林的月圆之夜"
                continue
        
        # If one YRN combo is made, it counts as '永夜组'
        # and adds to score. Does it also add the specific yrn_combo_name like "结界组"?
        # Original logic just adds '永夜组' and breaks.
        cp_score_count +=1 # Counts as one more CP combo
        if not yrn_made : # Add '永夜组' only once
             yizhong_cp_list.append("永夜组") # Generic name for any YRN combo made
             yrn_made = True
        # yizhong_cp_list.append(combo_name) # Optionally add specific yrn combo name too
        # break # Original code breaks after one YRN match

    return cp_score_count, yizhong_cp_list


    def draw_wrapped_text_list(self, surface, prefix, items_list, y_start, font_obj, color, max_width):
        """辅助函数，用于绘制带前缀的、可换行的项目列表"""
        if not items_list:
            return y_start # 如果列表为空，不绘制任何内容，返回原始y坐标

        full_text = prefix + ", ".join(items_list)
        
        words = full_text.split(' ') # 按空格分词，以便更好地控制换行
        lines = []
        current_line = ""
        
        line_spacing = font_obj.get_linesize() 
        current_y = y_start

        for word in words:
            # 检查添加下一个词是否会超出宽度
            test_line = current_line + word + " "
            if font_obj.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                # 渲染当前行
                draw_text(surface, current_line.strip(), (CARD_MARGIN, current_y), font_obj, color)
                current_y += line_spacing
                current_line = word + " " # 开始新行
        
        # 渲染最后一行
        if current_line.strip():
            draw_text(surface, current_line.strip(), (CARD_MARGIN, current_y), font_obj, color)
            current_y += line_spacing
            
        return current_y # 返回下一行开始的y坐标

# --- Pygame Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_MARGIN = 10
HIGHLIGHT_BORDER = 4

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0) # Darker green for background
GRAY = (200, 200, 200)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (173, 216, 230)

# Asset Path
ASSET_PATH = "assets/cards"

# --- Global Variables / Game State (will be managed by a class) ---
card_images = {}
card_back_image = None
font = None
small_font = None

# --- Helper GUI Functions ---
def load_images():
    global card_back_image, card_images
    try:
        card_back_image = pygame.image.load(os.path.join(ASSET_PATH, "back.png")).convert_alpha()
        card_back_image = pygame.transform.scale(card_back_image, (CARD_WIDTH, CARD_HEIGHT))
    except pygame.error as e:
        print(f"Cannot load card back image: {e}")
        sys.exit()

    all_cards_for_images = card.initialize_cards() # Get all card definitions
    for c in all_cards_for_images:
        try:
            img_path = os.path.join(ASSET_PATH, f"{c.name}.png")
            loaded_img = pygame.image.load(img_path).convert_alpha()
            card_images[c.name] = pygame.transform.scale(loaded_img, (CARD_WIDTH, CARD_HEIGHT))
        except pygame.error:
            print(f"Warning: Cannot load image for {c.name}. Using back image.")
            card_images[c.name] = card_back_image # Fallback

def draw_text(surface, text, pos, font_obj, color=BLACK, center=False):
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = pos
    else:
        text_rect.topleft = pos
    surface.blit(text_surface, text_rect)

def draw_card(surface, card_obj, x, y, is_back=False, is_highlighted=False):
    if is_back or not card_obj: # card_obj can be None for placeholders
        image = card_back_image
    else:
        image = card_images.get(card_obj.name, card_back_image) # Fallback if name not found
    
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    surface.blit(image, rect.topleft)
    
    if is_highlighted:
        pygame.draw.rect(surface, YELLOW, rect, HIGHLIGHT_BORDER)
    return rect

# --- Game Manager Class ---
class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.deck = []
        self.player_human = Player("Player")
        self.player_ai = Player("Baka AI")
        self.field = []
        self.current_player = self.player_human # Human starts
        self.game_phase = "INIT" # INIT, PLAYER_TURN, AI_TURN, DIALOG, GAME_OVER
        self.message = ""
        self.dialog_active = False
        self.dialog_options = [] # For choices like "pick card" or "continue"
        self.dialog_callback = None # Function to call after dialog choice
        self.dialog_prompt = ""
        self.ids_on_field_at_start = [] # For "合札" scoring

        self.highlight_field_indices = [] # Indices of field cards to highlight
        self.hovered_hand_card_index = -1

        self.setup_game()

    def setup_game(self):
        self.deck = card.initialize_cards()
        random.shuffle(self.deck)

        self.player_human.hand = []
        self.player_human.collected = []
        self.player_human.score = 0
        self.player_human.yizhong = []

        self.player_ai.hand = []
        self.player_ai.collected = []
        self.player_ai.score = 0
        self.player_ai.yizhong = []

        # Initial draw for both players
        self.player_human.initial_draw(self.deck)
        self.player_ai.initial_draw(self.deck)

        # Initial field cards
        self.field = self.deck[:8]
        self.deck = self.deck[8:]
        self.ids_on_field_at_start = [c.card_id for c in self.field if c.card_type == 'spot']


        self.message = f"{self.player_human.name}'s turn."
        self.game_phase = "PRE_TURN_CHECKS" # Check for Tenhou before first turn

    def run_pre_turn_checks(self):
        # Check Tenhou (Heavenly Hand) for Human
        tenhou_human_score_type = checkhand(self.player_human.hand)
        if tenhou_human_score_type > 0:
            self.handle_tenhou(self.player_human, tenhou_human_score_type)
            return

        # Check Tenhou for AI
        tenhou_ai_score_type = checkhand(self.player_ai.hand)
        if tenhou_ai_score_type > 0:
            self.handle_tenhou(self.player_ai, tenhou_ai_score_type)
            return

        # Check field for Ryuukyoku (Abortive Draw due to 4 identical cards)
        if checkdeck(self.field) == 1: # 1 means condition for abortive draw met
            self.message = "Field has 4 identical cards at start! Abortive Draw (Ryuukyoku)."
            self.game_phase = "GAME_OVER"
            return
        
        self.game_phase = "PLAYER_TURN" # Proceed to normal play

    def handle_tenhou(self, player, score_type):
        if score_type == 3: # All spots
            player.score = 10
            self.message = f"{player.name} has Tenhou (All Spots)! Score: 10. Game Over."
        elif score_type == 2: # Double Shisou
            player.score = 8
            self.message = f"{player.name} has Tenhou (Double CP/4-of-a-kind)! Score: 8. Game Over."
        elif score_type == 1: # Shisou or CP
            player.score = 4
            self.message = f"{player.name} has Tenhou (CP/4-of-a-kind)! Score: 4. Game Over."
        self.game_phase = "GAME_OVER"


    def handle_player_discard(self, card_idx):
        if self.game_phase != "PLAYER_TURN" or self.dialog_active:
            return
        if 0 <= card_idx < len(self.player_human.hand):
            discarded_card = self.player_human.hand.pop(card_idx)
            self.field.append(discarded_card)
            self.message = f"{self.player_human.name} discarded {discarded_card.name}."
            # Start the get_card sequence
            self.process_get_card_phase(self.player_human, "DISCARD_MATCH")


    def process_get_card_phase(self, current_processing_player, sub_phase, chosen_card_from_dialog=None):
        # sub_phases: DISCARD_MATCH, DRAW_NEW_TO_FIELD, NEW_FIELD_CARD_MATCH, TURN_END_SCORE
        
        if sub_phase == "DISCARD_MATCH":
            if not self.field: 
                self.process_get_card_phase(current_processing_player, "DRAW_NEW_TO_FIELD")
                return

            target_card = self.field[-1] # The card just discarded or drawn
            matches_on_field = [c for c in self.field[:-1] if c.card_id == target_card.card_id]

            if matches_on_field:
                if len(matches_on_field) == 1:
                    chosen_card = matches_on_field[0]
                    self.collect_cards_for_player(current_processing_player, target_card, chosen_card)
                    self.process_get_card_phase(current_processing_player, "DRAW_NEW_TO_FIELD")
                elif len(matches_on_field) >= 2: # Includes the case of 3, where player takes all
                    if len(matches_on_field) == 2 :
                        self.dialog_prompt = f"您打出了 {target_card.name}. 请选择一张场上的牌来收集:"
                        self.dialog_options = matches_on_field 
                        self.dialog_callback = lambda choice_idx: self.finish_get_card_match_choice(current_processing_player, target_card, matches_on_field, choice_idx, "DRAW_NEW_TO_FIELD")
                        self.dialog_active = True
                        self.game_phase = "DIALOG"
                    else: # 3 or more matches, player takes them all + target
                        for mc in list(matches_on_field): # Iterate over copy for safe removal
                             self.collect_cards_for_player(current_processing_player, None, mc) # Collect match
                        self.collect_cards_for_player(current_processing_player, target_card, None) # Collect target
                        self.process_get_card_phase(current_processing_player, "DRAW_NEW_TO_FIELD")

            else: # No match for discarded card
                self.process_get_card_phase(current_processing_player, "DRAW_NEW_TO_FIELD")

        elif sub_phase == "DRAW_NEW_TO_FIELD":
            if self.deck:
                new_field_card = self.deck.pop(0)
                self.field.append(new_field_card)
                self.message = f"Drew {new_field_card.name} to field."
                self.process_get_card_phase(current_processing_player, "NEW_FIELD_CARD_MATCH")
            else: # No cards left in deck
                self.message = "Deck is empty."
                self.process_get_card_phase(current_processing_player, "TURN_END_SCORE")
        
        elif sub_phase == "NEW_FIELD_CARD_MATCH":
            if not self.field:
                self.process_get_card_phase(current_processing_player, "TURN_END_SCORE")
                return

            target_card = self.field[-1] # The newly drawn field card
            matches_on_field = [c for c in self.field[:-1] if c.card_id == target_card.card_id]

            if matches_on_field:
                if len(matches_on_field) == 1:
                    chosen_card = matches_on_field[0]
                    self.collect_cards_for_player(current_processing_player, target_card, chosen_card)
                    self.process_get_card_phase(current_processing_player, "TURN_END_SCORE")
                elif len(matches_on_field) >= 2:
                    if len(matches_on_field) == 2:
                        self.dialog_prompt = f"新翻开的 {target_card.name}. 请选择一张场上的牌来收集:"
                        self.dialog_options = matches_on_field
                        self.dialog_callback = lambda choice_idx: self.finish_get_card_match_choice(current_processing_player, target_card, matches_on_field, choice_idx, "TURN_END_SCORE")
                        self.dialog_active = True
                        self.game_phase = "DIALOG"
                    else: # 3 or more matches
                        for mc in list(matches_on_field):
                            self.collect_cards_for_player(current_processing_player, None, mc)
                        self.collect_cards_for_player(current_processing_player, target_card, None)
                        self.process_get_card_phase(current_processing_player, "TURN_END_SCORE")
            else: # No match for new field card
                self.process_get_card_phase(current_processing_player, "TURN_END_SCORE")

        elif sub_phase == "TURN_END_SCORE":
            self.perform_scoring(current_processing_player) # This might set dialog for continue/stop

    def finish_get_card_match_choice(self, current_processing_player, target_card, matches_on_field, choice_idx, next_sub_phase):
        self.dialog_active = False
        self.game_phase = "PROCESSING" # Temporary phase while logic runs
        
        chosen_match_card = matches_on_field[choice_idx]
        self.collect_cards_for_player(current_processing_player, target_card, chosen_match_card)
        
        self.process_get_card_phase(current_processing_player, next_sub_phase)


    def collect_cards_for_player(self, player_obj, target_card, matched_card):
        """ Helper to collect cards and remove from field.
            If target_card is None, only matched_card is collected (already on field).
            If matched_card is None, only target_card is collected (e.g. last card from field).
        """
        if target_card:
            if target_card in self.field: # Ensure it's actually on field before removing
                self.field.remove(target_card)
                player_obj.collected.append(target_card)
                self.message = f"{player_obj.name} collected {target_card.name}."
            else: # Safety, if target was already implicitly collected
                if target_card not in player_obj.collected:
                     player_obj.collected.append(target_card)
                     self.message = f"{player_obj.name} collected {target_card.name}."


        if matched_card:
            if matched_card in self.field:
                self.field.remove(matched_card)
                player_obj.collected.append(matched_card)
                self.message += f" and {matched_card.name}."
            else: # Safety
                if matched_card not in player_obj.collected:
                    player_obj.collected.append(matched_card)
                    self.message += f" and {matched_card.name}."
        
        # Sort collected cards for consistent display/scoring (optional)
        player_obj.collected.sort(key=lambda c: (c.card_type, c.card_id, c.name))


    def perform_scoring(self, player_obj):
        # Adapted from main.py's score function
        collected = player_obj.collected
        new_total_score = 0 # Calculate score from scratch based on current yaku
        new_yizhong = []
        
        scene_names = [c.name for c in collected if c.card_type == 'scene']
        item_names = [c.name for c in collected if c.card_type == 'item']
        spot_names = [c.name for c in collected if c.card_type == 'spot']
        char_names = [c.name for c in collected if c.card_type == 'character']
        yyc_chars = ["博丽灵梦", "八云紫", "雾雨魔理沙", "爱丽丝", "蕾米莉亚", "十六夜咲夜", "西行寺幽幽子", "魂魄妖梦"]
        
        temp_scene_names = list(scene_names) # Work with a copy
        removed_bamboo_moon = False
        
        if len(temp_scene_names) == 5:
            new_total_score += 10
            new_yizhong.append("五景")
        elif "迷失竹林的月圆之夜" in temp_scene_names:
            is_yyc_char_present = any(c_name in char_names for c_name in yyc_chars)
            if not is_yyc_char_present:
                if "迷失竹林的月圆之夜" in temp_scene_names :
                    temp_scene_names.remove("迷失竹林的月圆之夜")
                    removed_bamboo_moon = True
        
        if len(temp_scene_names) >= 3 and len(temp_scene_names) != 5: # Check after potential removal
            if len(temp_scene_names) == 4:
                new_total_score += 8
                new_yizhong.append("四景")
            elif len(temp_scene_names) == 3: # Must be exactly 3 for Sankei
                new_total_score += 5
                new_yizhong.append("三景")
        
        # CP Combinations
        cp_score_val, yizhong_cp_names = check_cp_combinations(collected)
        new_yizhong.extend(yizhong_cp_names)
        new_total_score += cp_score_val * 3 # Each CP combo unit worth 3 points

        # 合札 (Hezha - Matching Spot sets)
        # ids_on_field_at_start was stored at game setup
        card_id_counts = {}
        for c in collected:
            card_id_counts[c.card_id] = card_id_counts.get(c.card_id, 0) + 1
        
        for hezha_spot_id in self.ids_on_field_at_start: # Check against initial spot cards
            if card_id_counts.get(hezha_spot_id, 0) == 4:
                # Check if one of the collected cards with this ID is the specific spot card
                # This is a bit complex: need the name of the spot card with hezha_spot_id
                spot_card_for_hezha_name = ""
                for initial_spot_c in card.initialize_cards(): # Search all cards for the name
                    if initial_spot_c.card_id == hezha_spot_id and initial_spot_c.card_type == 'spot':
                        spot_card_for_hezha_name = initial_spot_c.name
                        break
                if spot_card_for_hezha_name:
                    new_total_score += 4
                    new_yizhong.append(f"合札-{spot_card_for_hezha_name}")
        
        # 武器库 (Weapon Arsenal)
        weapon_items = ["灵梦的御币", "早苗的御币", "楼观剑和白楼剑"]
        if all(item_name in item_names for item_name in weapon_items):
            new_total_score += 5
            new_yizhong.append("武器库")

        # 信仰战争 (Faith War)
        faith_spots = ["博丽神社", "守矢神社", "命莲寺"]
        if all(spot_name in spot_names for spot_name in faith_spots):
            new_total_score += 5
            new_yizhong.append("信仰战争")
            if "巫女组" in new_yizhong: # Specific interaction from original code
                 new_yizhong.remove("巫女组") # Assume this means 信仰战争 overrides/replaces score for 巫女组

        # Count-based scores
        if len(item_names) >= 5: 
            new_total_score += (len(item_names) - 5 + 1)
            new_yizhong.append(f"物品牌 ({len(item_names)})")
        if len(spot_names) >= 5:
            new_total_score += (len(spot_names) - 5 + 1)
            new_yizhong.append(f"地点牌 ({len(spot_names)})")
        if len(char_names) >= 10:
            new_total_score += (len(char_names) - 10 + 1)
            new_yizhong.append(f"角色牌 ({len(char_names)})")

        # Remove duplicate Yaku names, sort for consistent display
        new_yizhong = sorted(list(set(new_yizhong)))

        if new_yizhong != player_obj.yizhong and new_yizhong : # If new yaku formed
            player_obj.score = new_total_score # Update to the new total score
            player_obj.yizhong = new_yizhong
            
            self.message = f"{player_obj.name} formed new Yaku: {', '.join(new_yizhong)}! Score: {player_obj.score}"
            if player_obj == self.player_human :
                self.dialog_prompt = "New Yaku! Continue game or Stop?"
                self.dialog_options = ["Continue", "Stop"] # Represented by their strings
                self.dialog_callback = self.handle_continue_stop_choice
                self.dialog_active = True
                self.game_phase = "DIALOG"
            else: # AI always continues for simplicity, or add AI logic here
                self.message += " AI continues."
                self.end_turn() # AI continues
        else: # No new yaku, or no yaku at all
            player_obj.score = new_total_score # Still update score in case card counts changed point values
            player_obj.yizhong = new_yizhong
            self.end_turn()

    def handle_continue_stop_choice(self, choice_string): # choice is "Continue" or "Stop"
        self.dialog_active = False
        if choice_string == "Stop":
            self.message = f"{self.player_human.name} chose to stop. Final Score: {self.player_human.score}. Game Over."
            self.game_phase = "GAME_OVER"
        else: # Continue
            self.message = f"{self.player_human.name} continues."
            self.end_turn()
            self.game_phase = "PROCESSING" # Switch turn will set correct phase

    def end_turn(self):
        if self.game_phase == "GAME_OVER": # Already decided by scoring or dialog
            return

        # Check for game end by no cards in hand (after a full turn cycle)
        if not self.player_human.hand and not self.player_ai.hand:
            self.message = "All players out of cards! Game ends. Calculating final scores."
            # Potentially re-score both players here if needed, or assume current scores are final
            self.game_phase = "GAME_OVER"
            # Add logic to display final scores and winner
            if self.player_human.score > self.player_ai.score:
                self.message += f" {self.player_human.name} wins!"
            elif self.player_ai.score > self.player_human.score:
                 self.message += f" {self.player_ai.name} wins!"
            else:
                 self.message += " It's a tie!"
            return

        if self.current_player == self.player_human:
            self.current_player = self.player_ai
            self.game_phase = "AI_TURN"
            self.message = f"{self.player_ai.name}'s turn."
            self.perform_ai_turn() 
        else:
            self.current_player = self.player_human
            self.game_phase = "PLAYER_TURN"
            self.message = f"{self.player_human.name}'s turn."
            if not self.player_human.hand: # Player ran out of cards on their turn
                self.end_turn() # Effectively skips to AI or game over

    def perform_ai_turn(self):
        if self.game_phase != "AI_TURN" or not self.player_ai.hand:
            if not self.player_ai.hand: # AI ran out of cards
                self.end_turn()
            return

        # AI logic: "baka" always discards the first card
        discarded_card_ai = self.player_ai.hand.pop(0)
        self.field.append(discarded_card_ai)
        self.message = f"{self.player_ai.name} discarded {discarded_card_ai.name}."
        
        # AI processes its get_card phase (simplified: auto-picks first if choice)
        self.process_get_card_phase_ai(self.player_ai, "DISCARD_MATCH")


    def process_get_card_phase_ai(self, player_ai_obj, sub_phase):
        # Simplified version for AI - auto-picks first option
        if sub_phase == "DISCARD_MATCH":
            if not self.field:
                self.process_get_card_phase_ai(player_ai_obj, "DRAW_NEW_TO_FIELD")
                return
            target_card = self.field[-1]
            matches = [c for c in self.field[:-1] if c.card_id == target_card.card_id]
            if matches:
                # AI takes the first match, or all if >2
                if len(matches) >=3:
                     for mc in list(matches):
                         self.collect_cards_for_player(player_ai_obj, None, mc)
                     self.collect_cards_for_player(player_ai_obj, target_card, None)
                else:
                     self.collect_cards_for_player(player_ai_obj, target_card, matches[0])
            self.process_get_card_phase_ai(player_ai_obj, "DRAW_NEW_TO_FIELD")

        elif sub_phase == "DRAW_NEW_TO_FIELD":
            if self.deck:
                new_card = self.deck.pop(0)
                self.field.append(new_card)
                self.message = f"AI drew {new_card.name} to field."
                self.process_get_card_phase_ai(player_ai_obj, "NEW_FIELD_CARD_MATCH")
            else:
                self.process_get_card_phase_ai(player_ai_obj, "TURN_END_SCORE")
        
        elif sub_phase == "NEW_FIELD_CARD_MATCH":
            if not self.field:
                self.process_get_card_phase_ai(player_ai_obj, "TURN_END_SCORE")
                return
            target_card = self.field[-1]
            matches = [c for c in self.field[:-1] if c.card_id == target_card.card_id]
            if matches:
                if len(matches) >=3:
                     for mc in list(matches):
                         self.collect_cards_for_player(player_ai_obj, None, mc)
                     self.collect_cards_for_player(player_ai_obj, target_card, None)
                else: # Takes first match
                     self.collect_cards_for_player(player_ai_obj, target_card, matches[0])
            self.process_get_card_phase_ai(player_ai_obj, "TURN_END_SCORE")

        elif sub_phase == "TURN_END_SCORE":
            self.perform_scoring(player_ai_obj) # AI always continues if new yaku

    def handle_event(self, event):
        if self.game_phase == "GAME_OVER" and event.type == pygame.MOUSEBUTTONDOWN:
             # Option to restart game
             self.setup_game() # Restart
             return

        if self.dialog_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Simplified dialog: assume options are drawn as clickable regions
                # For text options like "Continue", "Stop"
                if isinstance(self.dialog_options[0], str): # Text button dialog
                    dialog_option_height = 40
                    for i, option_text in enumerate(self.dialog_options):
                        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 
                                                  SCREEN_HEIGHT // 2 + i * (dialog_option_height + 5), 
                                                  200, dialog_option_height)
                        if button_rect.collidepoint(event.pos):
                            self.dialog_callback(option_text) # Pass the string
                            break
                else: # Card choice dialog
                    card_spacing = CARD_WIDTH + CARD_MARGIN
                    total_width = len(self.dialog_options) * CARD_WIDTH + (len(self.dialog_options) - 1) * CARD_MARGIN
                    start_x = (SCREEN_WIDTH - total_width) // 2
                    dialog_card_y = SCREEN_HEIGHT // 2 
                    for i, card_opt in enumerate(self.dialog_options):
                        card_rect = pygame.Rect(start_x + i * card_spacing, dialog_card_y, CARD_WIDTH, CARD_HEIGHT)
                        if card_rect.collidepoint(event.pos):
                            self.dialog_callback(i) # Pass the index of chosen card
                            break
            return # Don't process other events if dialog is active

        if event.type == pygame.MOUSEMOTION:
            if self.game_phase == "PLAYER_TURN":
                self.highlight_field_indices = []
                self.hovered_hand_card_index = -1
                # Player hand hover
                hand_card_y = SCREEN_HEIGHT - CARD_HEIGHT - CARD_MARGIN
                for i, p_card in enumerate(self.player_human.hand):
                    hand_card_x = CARD_MARGIN + i * (CARD_WIDTH + CARD_MARGIN // 2)
                    card_rect = pygame.Rect(hand_card_x, hand_card_y, CARD_WIDTH, CARD_HEIGHT)
                    if card_rect.collidepoint(event.pos):
                        self.hovered_hand_card_index = i
                        # Highlight matching field cards
                        if p_card:
                            for field_idx, f_card in enumerate(self.field):
                                if f_card and f_card.card_id == p_card.card_id:
                                    self.highlight_field_indices.append(field_idx)
                        break 

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.game_phase == "PLAYER_TURN":
                # Player hand click
                hand_card_y = SCREEN_HEIGHT - CARD_HEIGHT - CARD_MARGIN
                for i, p_card in enumerate(self.player_human.hand):
                    hand_card_x = CARD_MARGIN + i * (CARD_WIDTH + CARD_MARGIN // 2)
                    if pygame.Rect(hand_card_x, hand_card_y, CARD_WIDTH, CARD_HEIGHT).collidepoint(event.pos):
                        self.handle_player_discard(i)
                        self.hovered_hand_card_index = -1 # Clear hover after click
                        self.highlight_field_indices = []
                        break
            elif self.game_phase == "PRE_TURN_CHECKS": # Click to advance past Tenhou checks if none
                self.run_pre_turn_checks()


    def draw(self):
        self.screen.fill(GREEN)

        # Draw Player Hand (Human)
        hand_card_y = SCREEN_HEIGHT - CARD_HEIGHT - CARD_MARGIN
        for i, p_card in enumerate(self.player_human.hand):
            hand_card_x = CARD_MARGIN + i * (CARD_WIDTH + CARD_MARGIN // 2) # Allow slight overlap if many
            is_highlight = (i == self.hovered_hand_card_index)
            draw_card(self.screen, p_card, hand_card_x, hand_card_y, is_highlighted=is_highlight)

        # Draw AI Hand (as backs)
        ai_hand_y = CARD_MARGIN
        for i in range(len(self.player_ai.hand)):
            ai_card_x = CARD_MARGIN + i * (CARD_WIDTH // 2) # Overlap more
            draw_card(self.screen, None, ai_card_x, ai_hand_y, is_back=True)
        draw_text(self.screen, f"AI Hand: {len(self.player_ai.hand)}", (ai_card_x + CARD_WIDTH + 20, ai_hand_y + CARD_HEIGHT // 3), small_font)


        # Draw Field Cards
        field_start_x = CARD_MARGIN
        field_start_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT - CARD_MARGIN # Upper part of center
        max_field_width = SCREEN_WIDTH - 2 * CARD_MARGIN
        current_x, current_y = field_start_x, field_start_y
        for i, f_card in enumerate(self.field):
            is_highlight = (i in self.highlight_field_indices)
            draw_card(self.screen, f_card, current_x, current_y, is_highlighted=is_highlight)
            current_x += CARD_WIDTH + CARD_MARGIN
            if current_x + CARD_WIDTH > max_field_width:
                current_x = field_start_x
                current_y += CARD_HEIGHT + CARD_MARGIN
        
        # Draw Deck
        if self.deck:
            draw_card(self.screen, None, SCREEN_WIDTH - CARD_WIDTH - CARD_MARGIN, field_start_y, is_back=True)
            draw_text(self.screen, f"Deck: {len(self.deck)}", (SCREEN_WIDTH - CARD_WIDTH - CARD_MARGIN, field_start_y + CARD_HEIGHT + 5), small_font)
        
        # Draw Collected Cards (Counts for simplicity)
        draw_text(self.screen, f"{self.player_human.name} Collected: {[c.name for c in self.player_ai.collected]} | Score: {self.player_human.score}", 
                  (CARD_MARGIN, SCREEN_HEIGHT - CARD_HEIGHT - CARD_MARGIN * 2 - 30), font)
        if self.player_human.yizhong:
            draw_text(self.screen, f"Yaku: {', '.join(self.player_human.yizhong)}",
                      (CARD_MARGIN, SCREEN_HEIGHT - CARD_HEIGHT - CARD_MARGIN * 2 - 60), small_font, color=BLUE)


        draw_text(self.screen, f"{self.player_ai.name} Collected: {[c.name for c in self.player_ai.collected]} | Score: {self.player_ai.score}",
                  (CARD_MARGIN, CARD_MARGIN + CARD_HEIGHT + 20), font)
        if self.player_ai.yizhong:
            draw_text(self.screen, f"AI Yaku: {', '.join(self.player_ai.yizhong)}",
                      (CARD_MARGIN, CARD_MARGIN + CARD_HEIGHT + 50), small_font, color=RED)
        
        # Draw Message / Status
        draw_text(self.screen, self.message, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30), font, color=WHITE, center=True)
        if self.game_phase == "PRE_TURN_CHECKS":
             draw_text(self.screen, "Click to start first turn checks.", (SCREEN_WIDTH // 2, SCREEN_HEIGHT //2), font, color=YELLOW, center=True)


        # Draw Dialog
        if self.dialog_active:
            # Simple overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180)) # Semi-transparent black
            self.screen.blit(overlay, (0,0))

            draw_text(self.screen, self.dialog_prompt, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60), font, color=WHITE, center=True)
            
            # Text options (Continue/Stop)
            if isinstance(self.dialog_options[0], str):
                dialog_option_height = 40
                for i, option_text in enumerate(self.dialog_options):
                    btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + i * (dialog_option_height + 10), 200, dialog_option_height)
                    pygame.draw.rect(self.screen, LIGHT_BLUE, btn_rect)
                    pygame.draw.rect(self.screen, BLACK, btn_rect, 2) # Border
                    draw_text(self.screen, option_text, btn_rect.center, font, BLACK, center=True)
            # Card options
            else:
                card_spacing = CARD_WIDTH + CARD_MARGIN
                total_width = len(self.dialog_options) * CARD_WIDTH + (len(self.dialog_options) - 1) * CARD_MARGIN
                start_x = (SCREEN_WIDTH - total_width) // 2
                dialog_card_y = SCREEN_HEIGHT // 2 
                for i, card_opt in enumerate(self.dialog_options):
                    # Highlight if mouse is over this dialog card option
                    card_opt_rect = draw_card(self.screen, card_opt, start_x + i * card_spacing, dialog_card_y)
                    mouse_pos = pygame.mouse.get_pos()
                    if card_opt_rect.collidepoint(mouse_pos):
                         pygame.draw.rect(self.screen, YELLOW, card_opt_rect, HIGHLIGHT_BORDER)


        if self.game_phase == "GAME_OVER":
            draw_text(self.screen, "GAME OVER. Click to restart.", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), font, color=YELLOW, center=True)


def main_gui():
    global font, small_font
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Touhou Card Game")
    
    font_path = "sc.ttf" # <--- 请将这里替换为您实际的字体文件名
    try:
        font = pygame.font.Font(font_path, 32) # 主字体，字号调小一点以容纳更多内容
        small_font = pygame.font.Font(font_path, 24) # 小字体
        tiny_font = pygame.font.Font(font_path, 18) # 更小的字体，用于收集的牌和役种列表
    except pygame.error as e:
        print(f"警告: 无法加载指定字体 '{font_path}'. 将使用默认字体 (可能不支持中文)。错误: {e}")
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)
        tiny_font = pygame.font.Font(None, 22) # 默认字体下的更小尺寸
        
    load_images()
    if not card_back_image or not card_images: # Critical load fail
        return

    game_manager = GameManager(screen)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_manager.handle_event(event)

        # Game logic updates (AI turn, phase changes not tied to direct input)
        if game_manager.game_phase == "AI_TURN" and not game_manager.dialog_active:
             # AI turn might involve drawing, scoring etc. which might trigger dialogs.
             # The perform_ai_turn and subsequent scoring should handle phase changes.
             pass # AI turn is mostly handled within its call sequence from end_turn or player action.
        
        game_manager.draw()
        pygame.display.flip()
        clock.tick(30) # FPS

    pygame.quit()

if __name__ == '__main__':
    # Create dummy assets folder and a few images if they don't exist, for quick testing
    if not os.path.exists(ASSET_PATH):
        os.makedirs(ASSET_PATH)
    
    # Create a dummy back.png and one card if missing for basic runnability
    # In a real scenario, user must provide these.
    try:
        if not os.path.exists(os.path.join(ASSET_PATH, "back.png")):
            surf = pygame.Surface((100,150))
            surf.fill(BLUE)
            pygame.image.save(surf, os.path.join(ASSET_PATH, "back.png"))
        
        # Example: Create a dummy for a card that might be in the list
        # This part is tricky as card names come from card.py
        # For now, assume user has their assets.
        # first_card_name_for_dummy = card.initialize_cards()[0].name
        # if not os.path.exists(os.path.join(ASSET_PATH, f"{first_card_name_for_dummy}.png")):
        #     surf = pygame.Surface((100,150))
        #     surf.fill(RED)
        #     pygame.image.save(surf, os.path.join(ASSET_PATH, f"{first_card_name_for_dummy}.png"))
        pass # User should have actual assets.

    except Exception as e:
        print(f"Error creating dummy assets (not critical if you have them): {e}")

    main_gui()