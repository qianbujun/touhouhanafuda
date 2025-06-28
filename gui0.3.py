# gui0.3.py

import pygame
import sys
import os
import random

from card import card
from player import Player

# --- Data from main.py (or a shared data module) ---
# (数据部分保持不变，此处省略以减少篇幅)
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
    # Note: "幽冥组" is in both. check_cp_combinations handles this by potentially adding "永夜组"
    # and the specific "幽冥组" from cp_combinations.
    "幽冥组 YRN": {"chars": ["魂魄妖梦", "西行寺幽幽子"], "scenes": ["迷失竹林的月圆之夜"]}, # Renamed to avoid dict key collision
    "永远组": {"chars": ["八意永琳", "蓬莱山辉夜"], "scenes": ["迷失竹林的月圆之夜"]},
    "不死组": {"chars": ["蓬莱山辉夜", "藤原妹红"], "scenes": ["迷失竹林的月圆之夜"]}
}


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.abspath(".") # Fallback

    return os.path.join(base_path, relative_path)

# --- Helper functions from main.py (adapted for GUI) ---
# (这部分函数不变，省略以减少篇幅)
def build_pair_matrix(hand_cards):
    matrix = [[0]*8 for _ in range(8)]
    predefined_cps_sorted = {tuple(sorted(p)) for p in predefined_cps}
    for i in range(8):
        for j in range(i + 1, 8):
            if hand_cards[i].card_id == hand_cards[j].card_id:
                matrix[i][j] = matrix[j][i] = 1
            else:
                pair_names_sorted = tuple(sorted((hand_cards[i].name, hand_cards[j].name)))
                if pair_names_sorted in predefined_cps_sorted:
                    matrix[i][j] = matrix[j][i] = 1
    return matrix

def can_form_perfect_match(matrix):
    n = len(matrix)
    used = [False] * n
    def backtrack_pm_recursive(pairs_formed_count):
        if pairs_formed_count == n // 2: return True
        first_idx_to_pair = -1
        for i in range(n):
            if not used[i]: first_idx_to_pair = i; break
        if first_idx_to_pair == -1: return False
        used[first_idx_to_pair] = True
        for j in range(first_idx_to_pair + 1, n):
            if not used[j] and matrix[first_idx_to_pair][j] == 1:
                used[j] = True
                if backtrack_pm_recursive(pairs_formed_count + 1): return True
                used[j] = False
        used[first_idx_to_pair] = False
        return False
    return backtrack_pm_recursive(0)

def checkhandcp(hand_cards):
    if len(hand_cards) != 8: return 0
    if not all(c.card_type == 'character' for c in hand_cards): return 0
    matrix = build_pair_matrix(hand_cards)
    return 1 if can_form_perfect_match(matrix) else 0

def checkhand(hand_cards):
    if len(hand_cards) != 8: return 0
    char_cards = [c for c in hand_cards if c.card_type == 'character']
    spot_cards = [c for c in hand_cards if c.card_type == 'spot']
    if len(spot_cards) == 8: return 3
    if len(char_cards) == 8: return 1 if checkhandcp(char_cards) else 0
    counts = {}
    for item in hand_cards: counts[item.card_id] = counts.get(item.card_id, 0) + 1
    sorted_counts = sorted(counts.values(), reverse=True)
    if not sorted_counts: return 0
    if sorted_counts[0] >= 4:
        if len(sorted_counts) > 1 and sorted_counts[1] >= 4: return 2
        return 1
    return 0

def checkdeck(field_cards):
    if not field_cards or len(field_cards) < 4 : return 0
    counts = {}
    for item in field_cards: counts[item.card_id] = counts.get(item.card_id, 0) + 1
    for card_id_count in counts.values():
        if card_id_count >= 4: return 1
    return 0

def check_cp_combinations(collected_cards):
    char_set = set(c.name for c in collected_cards if c.card_type == 'character')
    scene_set = set(c.name for c in collected_cards if c.card_type == 'scene')
    spot_set = set(c.name for c in collected_cards if c.card_type == 'spot')
    yizhong_cp_list = []
    cp_score_units = 0 
    for combo_name, combo in cp_combinations.items():
        if not all(char_name in char_set for char_name in combo["chars"]): continue
        if "scenes" in combo and combo["scenes"]:
            if not any(scene_name in scene_set for scene_name in combo["scenes"]): continue
        if "spots" in combo and combo["spots"]:
            if not any(spot_name in spot_set for spot_name in combo["spots"]): continue
        cp_score_units += 1 
        yizhong_cp_list.append(combo_name)
    yrn_made_generic = False
    for combo_name, combo in yrn_combinations.items(): 
        if not all(char_name in char_set for char_name in combo["chars"]): continue
        if "scenes" in combo and combo["scenes"]: 
            if not any(scene_name in scene_set for scene_name in combo["scenes"]): continue
        if not yrn_made_generic:
            cp_score_units += 1 
            yizhong_cp_list.append("永夜组") 
            yrn_made_generic = True
            break
    return cp_score_units, yizhong_cp_list


# --- NEW: UI and Asset Management ---

# --- Constants & Colors ---
INITIAL_SCREEN_WIDTH = 1280
INITIAL_SCREEN_HEIGHT = 720
CARD_ASPECT_RATIO = 2.0 / 3.0 # width / height

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND = (173, 216, 230)
GRAY = (200, 200, 200)
LIGHT_GRAY = (176,224,230)
RED = (230, 0, 0)
BLUE = (30, 144, 255)
YELLOW = (255, 153, 18)
LIGHT_BLUE = (255,255,255)

# --- Global Asset Storage ---
ASSET_PATH = resource_path("assets/cards")
original_card_images = {} # Store original loaded images
scaled_card_images = {}   # Store images scaled to current screen size
font_path = None
# --- Asset Loading and Scaling Functions ---

def load_all_assets():
    """Loads all assets like images and fonts from disk once."""
    global original_card_images, font_path
    
    # Load Font
    try:
        font_path = resource_path("sc.ttf")
        # Test if font can be loaded
        _ = pygame.font.Font(font_path, 10)
    except pygame.error:
        print("自定义字体加载失败，使用默认字体。")
        font_path = None

    # Load Card Images
    all_cards_for_images = card.initialize_cards()
    for c in all_cards_for_images:
        try:
            # Prefer PNG over JPG
            img_path = os.path.join(ASSET_PATH, f"{c.name}.png")
            if not os.path.exists(img_path):
                img_path = os.path.join(ASSET_PATH, f"{c.name}.jpg")

            original_card_images[c.name] = pygame.image.load(img_path).convert_alpha()
        except pygame.error:
            # Create a placeholder if image is missing
            placeholder_surf = pygame.Surface((200, 300)) # Use a higher base resolution
            placeholder_surf.fill(GRAY)
            pygame.draw.rect(placeholder_surf, BLACK, placeholder_surf.get_rect(), 2)
            temp_font = pygame.font.Font(None, 24)
            text_surf = temp_font.render(c.name, True, BLACK)
            text_rect = text_surf.get_rect(center=(100, 150))
            placeholder_surf.blit(text_surf, text_rect)
            original_card_images[c.name] = placeholder_surf
    
    # Load Card Back
    try:
        back_path = os.path.join(ASSET_PATH, "back.png")
        original_card_images['back'] = pygame.image.load(back_path).convert_alpha()
    except pygame.error:
        print(f"Cannot load card back image: {back_path}")
        back_surf = pygame.Surface((200, 300))
        back_surf.fill(BLUE)
        original_card_images['back'] = back_surf

def rescale_all_assets(layout):
    """Rescales all loaded images and fonts based on the current layout."""
    global scaled_card_images
    
    card_size = (layout.card_width, layout.card_height)
    for name, orig_img in original_card_images.items():
        scaled_card_images[name] = pygame.transform.smoothscale(orig_img, card_size)

# --- NEW: LayoutManager Class ---
class LayoutManager:
    """Handles all UI element sizing and positioning."""
    def __init__(self, width, height):
        self.update(width, height)

    def update(self, width, height):
        self.width = width
        self.height = height

        # --- Base Sizes ---
        self.card_height = int(self.height * 0.21) # Card height is 21% of screen height
        self.card_width = int(self.card_height * CARD_ASPECT_RATIO)
        self.card_margin = int(self.card_height * 0.07)
        self.highlight_border = int(self.card_height * 0.03)

        # --- Font Sizes ---
        self.font_size_main = int(self.height * 0.04)
        self.font_size_small = int(self.height * 0.028)
        self.font_size_tiny = int(self.height * 0.022)
        
        self.font_main = pygame.font.Font(font_path, self.font_size_main)
        self.font_small = pygame.font.Font(font_path, self.font_size_small)
        self.font_tiny = pygame.font.Font(font_path, self.font_size_tiny)

        # --- Dynamic Layout Rects ---
        player_hand_max_width = (self.card_width + self.card_margin // 2) * 8 - self.card_margin // 2
        info_panel_width = max(300, int(self.width * 0.3))

        self.ai_hand_display_rect = pygame.Rect(self.card_margin, self.card_margin, player_hand_max_width, self.card_height)
        self.ai_info_rect = pygame.Rect(self.width - info_panel_width - self.card_margin, self.card_margin, info_panel_width, self.card_height)
        
        self.player_hand_display_rect = pygame.Rect(self.card_margin, self.height - self.card_height - self.card_margin, player_hand_max_width, self.card_height)
        self.player_info_rect = pygame.Rect(self.width - info_panel_width - self.card_margin, self.player_hand_display_rect.top, info_panel_width, self.card_height)

        field_top_y = self.ai_hand_display_rect.bottom + self.card_margin
        field_bottom_y = self.player_hand_display_rect.top - self.card_margin
        self.field_display_start_y = field_top_y
        self.field_height = field_bottom_y - field_top_y
        self.max_field_rows = self.field_height // (self.card_height + self.card_margin)
        
        msg_height = int(self.height * 0.05)
        self.game_message_rect = pygame.Rect(self.card_margin, field_bottom_y - msg_height - 5, self.width - 2 * self.card_margin, msg_height)
        
        # Rescale assets after updating dimensions
        rescale_all_assets(self)


def draw_text(surface, text, pos, font_obj, color=BLACK, center=False, rect_to_fit=None, aa=True):
    # This function remains largely the same
    text_surface = font_obj.render(text, aa, color)
    text_rect = text_surface.get_rect()
    if rect_to_fit:
        if center: text_rect.center = rect_to_fit.center
        else: text_rect.topleft = rect_to_fit.topleft
    elif center: text_rect.center = pos
    else: text_rect.topleft = pos
    surface.blit(text_surface, text_rect)

def draw_card(surface, card_obj, x, y, layout, is_back=False, is_highlighted=False):
    card_key = 'back' if is_back or not card_obj else card_obj.name
    image_to_draw = scaled_card_images.get(card_key)
    
    rect = pygame.Rect(x, y, layout.card_width, layout.card_height)
    if image_to_draw:
        surface.blit(image_to_draw, rect.topleft)
    else:
        pygame.draw.rect(surface, RED, rect) # Fallback

    if is_highlighted:
        pygame.draw.rect(surface, YELLOW, rect, layout.highlight_border)
    return rect

class GameManager:
    def __init__(self, screen, ai_difficulty='baka'):
        self.screen = screen
        self.layout = LayoutManager(screen.get_width(), screen.get_height())
        self.ai_difficulty = ai_difficulty
        ai_name = "Baka AI" if ai_difficulty == 'baka' else "Daichan AI"
        
        self.deck = []
        self.player_human = Player("Player")
        self.player_ai = Player(ai_name)
        self.field = []
        self.current_player = self.player_human
        self.game_phase = "INIT" 
        self.message = ""
        self.dialog_active = False
        self.dialog_options = []
        self.dialog_callback = None
        self.dialog_prompt = ""
        self.ids_on_field_at_start = []
        self.game_ended_by_choice = False

        self.highlight_field_indices = []
        self.hovered_hand_card_index = -1
        self.turn_count = 0
        
        self.setup_game()

    def handle_resize(self, width, height):
        """Called when the window is resized."""
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.layout.update(width, height)

    # All other GameManager methods (setup_game, run_pre_turn_checks, etc.) remain.
    # We only need to adjust the drawing and event handling parts to use the LayoutManager.
    # (The logic methods don't need changes, so they are omitted here for brevity.
    # Paste them back from your original file.)
    def setup_game(self):
        self.deck = card.initialize_cards()
        random.shuffle(self.deck)
        self.turn_count = 0
        self.game_ended_by_choice = False # NEW: Reset on new game

        # Reset Human Player
        self.player_human.hand = []
        self.player_human.collected = []
        self.player_human.score = 0
        self.player_human.yizhong = []

        # Reset AI Player
        ai_name = "Baka AI" if self.ai_difficulty == 'baka' else "Daichan AI"
        self.player_ai.name = ai_name
        self.player_ai.hand = []
        self.player_ai.collected = []
        self.player_ai.score = 0
        self.player_ai.yizhong = []

        # Deal cards
        self.player_human.initial_draw(self.deck)
        self.player_ai.initial_draw(self.deck)

        self.field = []
        for _ in range(8):
            if self.deck: self.field.append(self.deck.pop(0))
        
        self.ids_on_field_at_start = [c.card_id for c in self.field if c.card_type == 'spot']
        
        self.current_player = self.player_human
        self.message = f"{self.player_human.name}'s turn to start."
        self.game_phase = "PRE_TURN_CHECKS"

    def run_pre_turn_checks(self):
        tenhou_human_score_type = checkhand(self.player_human.hand)
        if tenhou_human_score_type > 0:
            self.handle_tenhou(self.player_human, tenhou_human_score_type)
            return

        tenhou_ai_score_type = checkhand(self.player_ai.hand)
        if tenhou_ai_score_type > 0:
            self.handle_tenhou(self.player_ai, tenhou_ai_score_type)
            return

        if checkdeck(self.field) == 1:
            self.message = "场上初始有四张同ID牌! 流局 (Abortive Draw)."
            self.game_phase = "GAME_OVER"
            return
        
        self.game_phase = "PLAYER_TURN"
        self.message = f"{self.player_human.name}的回合."
        self.turn_count = 1

    def handle_tenhou(self, player, score_type):
        pts = 0
        reason = ""
        if score_type == 3:
            pts, reason = 10, "天和 (全地点牌)"
        elif score_type == 2:
            pts, reason = 8, "天和 (双手四)"
        elif score_type == 1:
            pts, reason = 4, "天和 (手四/CP)"
        
        player.score = pts
        self.message = f"{player.name} {reason}! 得分: {pts}. 游戏结束."
        self.game_phase = "GAME_OVER"

    def handle_player_discard(self, card_idx):
        if self.game_phase != "PLAYER_TURN" or self.dialog_active or self.current_player != self.player_human:
            return
        if 0 <= card_idx < len(self.player_human.hand):
            discarded_card = self.player_human.hand.pop(card_idx)
            self.field.append(discarded_card)
            self.message = f"{self.player_human.name} 打出了 {discarded_card.name}."
            self.game_phase = "PROCESSING_GET_CARD"
            self.process_get_card_sequence(self.player_human, "DISCARD_MATCH")
    
    def _ai_choose_match(self, matches_on_field):
        if self.ai_difficulty == 'baka' or len(matches_on_field) == 0:
            return matches_on_field[0]
        
        priority = ['scene', 'item', 'spot', 'character']
        for card_type in priority:
            for card_match in matches_on_field:
                if card_match.card_type == card_type:
                    return card_match
        
        return matches_on_field[0]

    def process_get_card_sequence(self, current_processing_player, sub_phase):
        if sub_phase == "DISCARD_MATCH":
            if not self.field: 
                self.process_get_card_sequence(current_processing_player, "DRAW_NEW_TO_FIELD")
                return

            target_card = self.field[-1] 
            matches_on_field = [c for c in self.field[:-1] if c.card_id == target_card.card_id]

            if not matches_on_field:
                self.process_get_card_sequence(current_processing_player, "DRAW_NEW_TO_FIELD")
            elif len(matches_on_field) == 1:
                self.collect_cards_for_player(current_processing_player, target_card, matches_on_field[0])
                self.process_get_card_sequence(current_processing_player, "DRAW_NEW_TO_FIELD")
            elif len(matches_on_field) >= 2:
                if len(matches_on_field) >= 3:
                    for mc in list(matches_on_field): self.collect_cards_for_player(current_processing_player, None, mc)
                    self.collect_cards_for_player(current_processing_player, target_card, None)
                    self.process_get_card_sequence(current_processing_player, "DRAW_NEW_TO_FIELD")
                elif current_processing_player == self.player_human:
                    self.dialog_prompt = f"您打出 {target_card.name}. 选择一张场上的牌收集:"
                    self.dialog_options = matches_on_field 
                    self.dialog_callback = lambda choice_idx: self.finish_get_card_match_choice(current_processing_player, target_card, matches_on_field, choice_idx, "DRAW_NEW_TO_FIELD")
                    self.dialog_active = True
                else:
                    chosen_match = self._ai_choose_match(matches_on_field)
                    self.collect_cards_for_player(current_processing_player, target_card, chosen_match)
                    self.process_get_card_sequence(current_processing_player, "DRAW_NEW_TO_FIELD")

        elif sub_phase == "DRAW_NEW_TO_FIELD":
            if self.deck:
                new_field_card = self.deck.pop(0)
                self.field.append(new_field_card)
                self.message = f"牌堆翻出 {new_field_card.name} 到场上."
                self.process_get_card_sequence(current_processing_player, "NEW_FIELD_CARD_MATCH")
            else: 
                self.message = "牌堆已空."
                self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")
        
        elif sub_phase == "NEW_FIELD_CARD_MATCH":
            if not self.field or len(self.field) < 1 :
                self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")
                return

            target_card = self.field[-1] 
            matches_on_field = [c for c in self.field[:-1] if c.card_id == target_card.card_id]

            if not matches_on_field:
                self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")
            elif len(matches_on_field) == 1:
                self.collect_cards_for_player(current_processing_player, target_card, matches_on_field[0])
                self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")
            elif len(matches_on_field) >= 2:
                if len(matches_on_field) >= 3:
                    for mc in list(matches_on_field): self.collect_cards_for_player(current_processing_player, None, mc)
                    self.collect_cards_for_player(current_processing_player, target_card, None)
                    self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")
                elif current_processing_player == self.player_human:
                    self.dialog_prompt = f"新翻开 {target_card.name}. 选择一张场上的牌收集:"
                    self.dialog_options = matches_on_field
                    self.dialog_callback = lambda choice_idx: self.finish_get_card_match_choice(current_processing_player, target_card, matches_on_field, choice_idx, "CHECK_SCORE_AND_END_TURN")
                    self.dialog_active = True
                else:
                    chosen_match = self._ai_choose_match(matches_on_field)
                    self.collect_cards_for_player(current_processing_player, target_card, chosen_match)
                    self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")

        elif sub_phase == "CHECK_SCORE_AND_END_TURN":
            stop_game_chosen = self.perform_scoring_and_check_continue(self.current_player)
            if not stop_game_chosen and self.game_phase != "GAME_OVER":
                self.end_turn()

    def finish_get_card_match_choice(self, current_processing_player, target_card, matches, choice_idx, next_sub_phase):
        self.dialog_active = False
        chosen_match_card = matches[choice_idx]
        self.collect_cards_for_player(current_processing_player, target_card, chosen_match_card)
        self.process_get_card_sequence(current_processing_player, next_sub_phase)


    def collect_cards_for_player(self, player_obj, target_card, matched_card):
        collected_names_msg = []
        if target_card:
            if target_card in self.field: self.field.remove(target_card)
            player_obj.collected.append(target_card)
            collected_names_msg.append(target_card.name)

        if matched_card:
            if matched_card in self.field: self.field.remove(matched_card)
            player_obj.collected.append(matched_card)
            collected_names_msg.append(matched_card.name)
        
        if collected_names_msg:
            self.message = f"{player_obj.name} 收集了: {', '.join(collected_names_msg)}."
        
        player_obj.collected.sort(key=lambda c: (c.card_type, c.card_id, c.name))

    def perform_scoring_and_check_continue(self, player_obj):
        collected = player_obj.collected
        new_total_score = 0 
        new_yizhong = []
        
        scene_names_all = [c.name for c in collected if c.card_type == 'scene']
        item_names = [c.name for c in collected if c.card_type == 'item']
        spot_names = [c.name for c in collected if c.card_type == 'spot']
        char_names = [c.name for c in collected if c.card_type == 'character']
        yyc_chars = ["博丽灵梦", "八云紫", "雾雨魔理沙", "爱丽丝", "蕾米莉亚", "十六夜咲夜", "西行寺幽幽子", "魂魄妖梦"]
        
        active_scene_names_for_yaku = list(scene_names_all)
        if len(active_scene_names_for_yaku) == 5:
            new_total_score += 10; new_yizhong.append("五景")
        else:
            is_yyc_char_present = any(c_name in char_names for c_name in yyc_chars)
            if "迷失竹林的月圆之夜" in active_scene_names_for_yaku and not is_yyc_char_present:
                active_scene_names_for_yaku.remove("迷失竹林的月圆之夜")
            if len(active_scene_names_for_yaku) == 4:
                new_total_score += 8; new_yizhong.append("四景")
            elif len(active_scene_names_for_yaku) == 3:
                new_total_score += 5; new_yizhong.append("三景")
        
        cp_score_units, yizhong_cp_names = check_cp_combinations(collected)
        new_yizhong.extend(yizhong_cp_names); new_total_score += cp_score_units * 3
        card_id_counts = {}
        for c in collected:
            card_id_counts[c.card_id] = card_id_counts.get(c.card_id, 0) + 1
        initial_spot_card_names = {c.card_id: c.name for c in card.initialize_cards() if c.card_type == 'spot'}
        for hezha_spot_id in self.ids_on_field_at_start: 
            if card_id_counts.get(hezha_spot_id, 0) >= 4:
                new_total_score += 4; new_yizhong.append(f"合札-{initial_spot_card_names.get(hezha_spot_id, f'ID {hezha_spot_id}')}")
        
        if all(item_name in item_names for item_name in ["灵梦的御币", "早苗的御币", "楼观剑和白楼剑"]):
            new_total_score += 5; new_yizhong.append("武器库")
        if all(spot_name in spot_names for spot_name in ["博丽神社", "守矢神社", "命莲寺"]):
            new_total_score += 5; new_yizhong.append("信仰战争")
        
        if len(item_names) >= 5: new_total_score += (len(item_names) - 4); new_yizhong.append(f"物品牌 ({len(item_names)})")
        if len(spot_names) >= 5: new_total_score += (len(spot_names) - 4); new_yizhong.append(f"地点牌 ({len(spot_names)})")
        if len(char_names) >= 10: new_total_score += (len(char_names) - 9); new_yizhong.append(f"角色牌 ({len(char_names)})")

        new_yizhong = sorted(list(set(new_yizhong)))
        player_obj.score = new_total_score

        if new_yizhong and new_yizhong != player_obj.yizhong: 
            player_obj.yizhong = new_yizhong
            self.message = f"{player_obj.name} 形成新役种: {', '.join(new_yizhong)}! 当前总分: {player_obj.score}"

            if len(player_obj.hand) == 0:
                self.message += " (最后一牌, 直接结束游戏)."
                self.game_phase = "GAME_OVER"
                return True

            if player_obj == self.player_human:
                self.dialog_prompt = "形成新役种! 是否结束游戏?"
                self.dialog_options = ["继续游戏", "结束游戏"] 
                self.dialog_callback = self.handle_continue_stop_choice
                self.dialog_active = True
                return True
            else:
                should_end_game = False
                if self.ai_difficulty == 'daichan' :
                    if len(player_obj.hand) <= 2 :
                        should_end_game = True
                    else:
                        probability_to_end = (8.0 - len(player_obj.hand)) / 8.0
                        if random.random() < probability_to_end :
                            should_end_game = True
                
                if should_end_game:
                    self.message += " AI选择结束游戏!"
                    self.game_ended_by_choice = True
                    self.game_phase = "GAME_OVER"
                    return True
                else:
                    self.message += " AI选择继续."
                    return False
        return False # Add this return for the case where no new yaku is formed.
                
    def handle_continue_stop_choice(self, choice_string): 
        self.dialog_active = False
        if choice_string == "结束游戏":
            self.message = f"{self.player_human.name} 选择结束游戏. 最终得分: {self.player_human.score}."
            self.game_ended_by_choice = True
            self.game_phase = "GAME_OVER"
        else:
            self.message = f"{self.player_human.name} 选择继续游戏."
            self.end_turn()

    def end_turn(self):
        if self.game_phase == "GAME_OVER": 
            return

        if not self.player_human.hand and not self.player_ai.hand:
            if self.game_ended_by_choice:
                self.message = "游戏结束."
            else:
                self.message = "流局! 无人通过役种获胜."
                self.player_human.score = 0
                self.player_ai.score = 0
            
            self.game_phase = "GAME_OVER"
            return

        if self.current_player == self.player_human:
            self.current_player = self.player_ai
            self.game_phase = "AI_TURN"
            self.message = f"{self.player_ai.name}的回合."
            self.perform_ai_turn() 
        else:
            self.current_player = self.player_human
            self.game_phase = "PLAYER_TURN"
            self.message = f"{self.player_human.name}的回合."
            if not self.player_human.hand:
                self.end_turn() 
        self.turn_count +=1

    def perform_ai_turn(self):
        if self.game_phase != "AI_TURN" or self.dialog_active:
            return
        if not self.player_ai.hand:
            self.end_turn()
            return

        pygame.time.wait(500)
        discarded_card_ai = self.player_ai.hand.pop(0) # Simple discard logic
        self.field.append(discarded_card_ai)
        self.message = f"{self.player_ai.name} 打出了 {discarded_card_ai.name}."
        
        self.game_phase = "PROCESSING_GET_CARD"
        self.process_get_card_sequence(self.player_ai, "DISCARD_MATCH")


    def handle_event(self, event):
        if self.game_phase == "GAME_OVER":
            if event.type == pygame.MOUSEBUTTONDOWN: self.setup_game()
            return
        
        # Use layout properties for all rect calculations
        l = self.layout 

        if self.dialog_active:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.dialog_options and isinstance(self.dialog_options[0], str): 
                    dialog_option_height = l.height * 0.07; base_y = l.height // 2
                    btn_width = l.width * 0.2
                    for i, option_text in enumerate(self.dialog_options):
                        button_rect = pygame.Rect(l.width // 2 - btn_width/2, base_y + i * (dialog_option_height + 10), btn_width, dialog_option_height)
                        if button_rect.collidepoint(event.pos):
                            if self.dialog_callback: self.dialog_callback(option_text); break
                elif self.dialog_options and isinstance(self.dialog_options[0], card):
                    card_spacing = l.card_width + l.card_margin; total_width = len(self.dialog_options) * card_spacing - l.card_margin
                    start_x = (l.width - total_width) // 2; dialog_card_y = l.height // 2 
                    for i, card_opt in enumerate(self.dialog_options):
                        card_rect = pygame.Rect(start_x + i * card_spacing, dialog_card_y, l.card_width, l.card_height)
                        if card_rect.collidepoint(event.pos):
                            if self.dialog_callback: self.dialog_callback(i); break
            return

        if event.type == pygame.MOUSEMOTION:
            if self.game_phase == "PLAYER_TURN" and self.current_player == self.player_human:
                self.highlight_field_indices = []
                self.hovered_hand_card_index = -1
                card_spacing = l.card_width + l.card_margin // 2
                for i in range(len(self.player_human.hand)):
                    card_rect = pygame.Rect(l.player_hand_display_rect.left + i * card_spacing, l.player_hand_display_rect.top, l.card_width, l.card_height)
                    if card_rect.collidepoint(event.pos):
                        self.hovered_hand_card_index = i
                        p_card = self.player_human.hand[i]
                        if p_card:
                            self.highlight_field_indices = [field_idx for field_idx, f_card in enumerate(self.field) if f_card and f_card.card_id == p_card.card_id]
                        break 

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.game_phase == "PLAYER_TURN" and self.current_player == self.player_human:
                card_spacing = l.card_width + l.card_margin // 2
                for i in range(len(self.player_human.hand)):
                    card_rect = pygame.Rect(l.player_hand_display_rect.left + i * card_spacing, l.player_hand_display_rect.top, l.card_width, l.card_height)
                    if card_rect.collidepoint(event.pos):
                        self.handle_player_discard(i); self.hovered_hand_card_index = -1; self.highlight_field_indices = []; break
            elif self.game_phase == "PRE_TURN_CHECKS": 
                self.run_pre_turn_checks()

    def draw_info_panel(self, surface, player, panel_rect):
        l = self.layout
        pygame.draw.rect(surface, LIGHT_GRAY, panel_rect); pygame.draw.rect(surface, BLACK, panel_rect, 2)
        current_y, text_x_start = panel_rect.top + 5, panel_rect.left + 5
        max_text_width = panel_rect.width - 10
        draw_text(surface, f"{player.name} | 得分: {player.score}", (text_x_start, current_y), l.font_main, BLACK)
        current_y += l.font_main.get_linesize() + 2
        if player.yizhong:
            current_y = self.draw_wrapped_text_list_in_rect(surface, "役种: ", player.yizhong, text_x_start, current_y, l.font_small, BLUE, max_text_width, panel_rect.bottom - 5)
        current_y += 3
        if player.collected:
            self.draw_wrapped_text_list_in_rect(surface, "收集: ", [c.name for c in player.collected], text_x_start, current_y, l.font_tiny, BLACK, max_text_width, panel_rect.bottom - 5)

    def draw_wrapped_text_list_in_rect(self, surface, prefix, items_list, x_pos, y_start, font_obj, color, max_width, y_boundary):
        if not items_list: return y_start
        full_text = prefix + ", ".join(items_list)
        words = full_text.split(' '); current_line_text = ""; current_y = y_start; line_spacing = font_obj.get_linesize()
        for word in words:
            word_to_add = (" " + word) if current_line_text else word
            if font_obj.size(current_line_text + word_to_add)[0] <= max_width:
                current_line_text += word_to_add
            else:
                if current_y + line_spacing > y_boundary: return current_y
                draw_text(surface, current_line_text.strip(), (x_pos, current_y), font_obj, color)
                current_y += line_spacing; current_line_text = word
        if current_line_text.strip() and current_y + line_spacing <= y_boundary:
            draw_text(surface, current_line_text.strip(), (x_pos, current_y), font_obj, color)
            current_y += line_spacing
        return current_y

    def draw(self):
        l = self.layout
        self.screen.fill(BACKGROUND)
        
        # AI Hand & Info
        ai_hand_base_x = l.ai_hand_display_rect.left
        ai_card_spacing = l.card_width // 2
        for i in range(len(self.player_ai.hand)):
            draw_card(self.screen, None, ai_hand_base_x + i * ai_card_spacing, l.ai_hand_display_rect.top, l, is_back=True)
        if len(self.player_ai.hand) > 0:
            text_pos = (ai_hand_base_x + len(self.player_ai.hand) * ai_card_spacing + 5, l.ai_hand_display_rect.centery -10)
            draw_text(self.screen, f"AI手牌: {len(self.player_ai.hand)}", text_pos, l.font_small, BLACK)
        self.draw_info_panel(self.screen, self.player_ai, l.ai_info_rect)

        # Field, Deck, Message
        if self.field:
            cards_per_row = (l.width - l.card_margin*4) // (l.card_width + l.card_margin)
            row_width = cards_per_row * (l.card_width + l.card_margin) - l.card_margin
            field_start_x = (l.width - row_width) // 2
            for i, f_card in enumerate(self.field):
                row, col = i // cards_per_row, i % cards_per_row
                if row < l.max_field_rows:
                    card_x = field_start_x + col * (l.card_width + l.card_margin)
                    card_y = l.field_display_start_y + row * (l.card_height + l.card_margin)
                    draw_card(self.screen, f_card, card_x, card_y, l, is_highlighted=(i in self.highlight_field_indices))
        
        if self.deck:
            deck_x = l.width - l.card_width - l.card_margin * 2
            deck_y = l.field_display_start_y
            draw_card(self.screen, None, deck_x, deck_y, l, is_back=True)
            draw_text(self.screen, f"牌堆: {len(self.deck)}", (deck_x, deck_y + l.card_height + 5), l.font_small, WHITE)
        
        draw_text(self.screen, self.message, (0,0), l.font_main, WHITE, center=True, rect_to_fit=l.game_message_rect)

        # Player Hand & Info
        player_card_spacing = l.card_width + l.card_margin // 2
        for i, p_card in enumerate(self.player_human.hand):
            is_highlight = (i == self.hovered_hand_card_index and self.current_player == self.player_human)
            draw_card(self.screen, p_card, l.player_hand_display_rect.left + i * player_card_spacing, l.player_hand_display_rect.top, l, is_highlighted=is_highlight)
        self.draw_info_panel(self.screen, self.player_human, l.player_info_rect)
        
        # Overlays
        if self.dialog_active:
            overlay_surf = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA); overlay_surf.fill((0,0,0,180)); self.screen.blit(overlay_surf, (0,0))
            draw_text(self.screen, self.dialog_prompt, (l.width // 2, l.height // 2 - l.card_height*0.7), l.font_main, WHITE, center=True)
            if self.dialog_options and isinstance(self.dialog_options[0], str):
                btn_h = l.height * 0.07; btn_w = l.width * 0.2
                for i, option_text in enumerate(self.dialog_options):
                    btn_rect = pygame.Rect(l.width // 2 - btn_w/2, l.height // 2 + i * (btn_h + 10), btn_w, btn_h)
                    pygame.draw.rect(self.screen, LIGHT_BLUE, btn_rect); pygame.draw.rect(self.screen, BLACK, btn_rect, 2)
                    draw_text(self.screen, option_text, btn_rect.center, l.font_main, BLACK, center=True)
            elif self.dialog_options and isinstance(self.dialog_options[0], card):
                card_spacing = l.card_width + l.card_margin; total_width = len(self.dialog_options) * card_spacing - l.card_margin
                start_x = (l.width - total_width) // 2; dialog_card_y = l.height // 2
                for i, card_opt in enumerate(self.dialog_options):
                    card_rect = draw_card(self.screen, card_opt, start_x + i * card_spacing, dialog_card_y, l)
                    if card_rect.collidepoint(pygame.mouse.get_pos()): pygame.draw.rect(self.screen, YELLOW, card_rect, l.highlight_border)

        if self.game_phase == "PRE_TURN_CHECKS":
             draw_text(self.screen, "点击屏幕开始回合前检查.", (l.width // 2, l.height //2), l.font_main, YELLOW, center=True)
        elif self.game_phase == "GAME_OVER":
            final_msg_rect = pygame.Rect(l.width // 4, l.height // 3, l.width // 2, l.height // 3)
            pygame.draw.rect(self.screen, BLACK, final_msg_rect); pygame.draw.rect(self.screen, WHITE, final_msg_rect, 3)
            lines = [self.message, "点击屏幕重新开始."]; 
            for i, line in enumerate(lines):
                 draw_text(self.screen, line, (final_msg_rect.centerx, final_msg_rect.centery -15 + i*l.font_main.get_linesize()), l.font_main, YELLOW, center=True)


def main_gui():
    pygame.init()
    # NEW: Set window to be resizable
    screen = pygame.display.set_mode((INITIAL_SCREEN_WIDTH, INITIAL_SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Touhou Hanafuda Koi-Koi")
    clock = pygame.time.Clock()

    # NEW: Load all assets once at the start
    load_all_assets()
    
    layout = LayoutManager(screen.get_width(), screen.get_height())

    # Pre-game loop for AI selection
    ai_difficulty = None
    selection_done = False
    while not selection_done:
        # Recalculate button rects every frame in case of resize during selection
        btn_w, btn_h = layout.width * 0.2, layout.height * 0.08
        baka_button = pygame.Rect(layout.width/2 - btn_w*1.1, layout.height/2 - btn_h/2, btn_w, btn_h)
        daichan_button = pygame.Rect(layout.width/2 + btn_w*0.1, layout.height/2 - btn_h/2, btn_w, btn_h)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE:
                layout.update(event.w, event.h)
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if baka_button.collidepoint(event.pos):
                    ai_difficulty = 'baka'; selection_done = True
                elif daichan_button.collidepoint(event.pos):
                    ai_difficulty = 'daichan'; selection_done = True
        
        screen.fill(BACKGROUND)
        draw_text(screen, "选择AI难度 (Choose AI Difficulty)", (layout.width/2, layout.height/2 - layout.height*0.2), layout.font_main, WHITE, center=True)
        
        pygame.draw.rect(screen, LIGHT_BLUE, baka_button); pygame.draw.rect(screen, BLACK, baka_button, 2)
        draw_text(screen, "Baka (新手)", baka_button.center, layout.font_main, BLACK, center=True)
        pygame.draw.rect(screen, LIGHT_BLUE, daichan_button); pygame.draw.rect(screen, BLACK, daichan_button, 2)
        draw_text(screen, "Daichan (普通)", daichan_button.center, layout.font_main, BLACK, center=True)
        
        pygame.display.flip()
        clock.tick(30)
    
    game_manager = GameManager(screen, ai_difficulty)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            # NEW: Handle window resize event
            if event.type == pygame.VIDEORESIZE:
                game_manager.handle_resize(event.w, event.h)
            
            game_manager.handle_event(event)
        
        game_manager.draw()
        pygame.display.flip()
        clock.tick(30) 

    pygame.quit()


if __name__ == '__main__':
    if not os.path.exists(ASSET_PATH):
        os.makedirs(ASSET_PATH)
        print(f"Created assets folder at: {os.path.abspath(ASSET_PATH)}")
        print("Please place card images (e.g., '博丽灵梦.png') and 'back.png' in this folder.")

    dummy_back_path = os.path.join(ASSET_PATH, "back.png")
    if not os.path.exists(dummy_back_path):
        try:
            if not pygame.get_init(): pygame.init()
            # Create a slightly higher resolution dummy image
            surf = pygame.Surface((200,300)); surf.fill(BLUE); pygame.draw.rect(surf, WHITE, surf.get_rect(), 3)
            pygame.image.save(surf, dummy_back_path)
            print(f"Created dummy '{os.path.basename(dummy_back_path)}'. Please replace with actual image.")
        except Exception as e:
            print(f"Error creating dummy back.png: {e}")
            
    main_gui()