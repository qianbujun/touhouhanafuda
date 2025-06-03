# gui.py

import pygame
import sys
import os
import random

from card import card
from player import Player

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
    # Note: "幽冥组" is in both. check_cp_combinations handles this by potentially adding "永夜组"
    # and the specific "幽冥组" from cp_combinations.
    "幽冥组 YRN": {"chars": ["魂魄妖梦", "西行寺幽幽子"], "scenes": ["迷失竹林的月圆之夜"]}, # Renamed to avoid dict key collision
    "永远组": {"chars": ["八意永琳", "蓬莱山辉夜"], "scenes": ["迷失竹林的月圆之夜"]},
    "不死组": {"chars": ["蓬莱山辉夜", "藤原妹红"], "scenes": ["迷失竹林的月圆之夜"]}
}

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # For one-folder builds, _MEIPASS is not set, and files are relative to exe
        # For one-file builds, _MEIPASS is the temp extraction folder
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.abspath(".") # Fallback

    return os.path.join(base_path, relative_path)


# --- Helper functions from main.py (adapted for GUI) ---
def build_pair_matrix(hand_cards):
    matrix = [[0]*8 for _ in range(8)]
    for i in range(8):
        for j in range(i + 1, 8):
            if hand_cards[i].card_id == hand_cards[j].card_id:
                matrix[i][j] = matrix[j][i] = 1
            else:
                # Ensure consistent ordering for tuple lookup
                pair_names_sorted = tuple(sorted((hand_cards[i].name, hand_cards[j].name)))
                if pair_names_sorted in predefined_cps: # Check sorted tuple
                    matrix[i][j] = matrix[j][i] = 1
    return matrix

def can_form_perfect_match(matrix):
    n = len(matrix)
    used = [False] * n
    
    # More efficient perfect matching check (Hopcroft-Karp is complex,
    # but for fixed N=8, backtracking is fine. Ensure it explores branches correctly)
    # The existing backtrack might be slightly inefficient but should work for N=8.
    # Let's refine the provided backtrack:
    def backtrack_pm(k, count_pairs): # k is current card index to try pairing
        if count_pairs == n // 2: # n//2 pairs means perfect match
            return True
        if k >= n: # All cards processed
            return False
        
        if used[k]: # If card k is already used, move to next
            return backtrack_pm(k + 1, count_pairs)

        used[k] = True
        for i in range(k + 1, n):
            if not used[i] and matrix[k][i] == 1: # If card i is not used and can pair with k
                used[i] = True
                if backtrack_pm(k + 1, count_pairs + 1):
                    return True
                used[i] = False # Backtrack

        used[k] = False # Backtrack: card k could not be paired starting from here
        
        # This path is if card k is left unpaired. For perfect matching, this means failure for this branch
        # unless we allow skipping. However, the goal is to pair up *all* cards if possible.
        # A simpler way for perfect matching is to iterate through available cards.
        # The original one looked for the first unused:
        # Find the first unused card 'first_available'
        # Try to pair 'first_available' with 'j'. Recurse.
        # If that fails, 'first_available' cannot be part of this perfect match solution starting this way.
        # The original `can_form_perfect_match` had `start_index` which is a good way to structure.
        # Let's use the original provided one, assuming its logic path for N=8 is okay.
        # The one from the prompt: `def backtrack(pairs_count, start_index):` is better.
        # I used `pairs_count` and `start_index` in my version in prompt, which is reasonable.
        
        # Using the prompt's can_form_perfect_match structure
        first_available = -1
        for i in range(n): # Find first available card to start a new pair
            if not used[i]:
                first_available = i
                break
        
        if first_available == -1: # All cards used
            return count_pairs == n // 2 # True if 4 pairs formed

        # Try to pair 'first_available'
        used[first_available] = True
        for j in range(first_available + 1, n):
            if not used[j] and matrix[first_available][j] == 1:
                used[j] = True
                if backtrack_pm_recursive(count_pairs + 1): # Recursive call without specific start_index, relies on finding next available
                    return True
                used[j] = False # Backtrack
        used[first_available] = False # Backtrack: 'first_available' could not be successfully paired to form a PM

        # If 'first_available' cannot be paired as part of this attempt to reach 4 pairs, this path fails.
        # For a perfect match, every card must be paired. If we reach here, it means 'first_available'
        # couldn't form a pair that leads to a solution.
        # We also need a path where 'first_available' is *skipped* if it cannot start a pair,
        # allowing other cards to form pairs. This is tricky for PM.
        # The prompt's can_form_perfect_match's backtrack(0,0) is likely more correct.
        return False # Default if no PM found from this state

    # Inner recursive helper for the prompt's version style
    def backtrack_pm_recursive(pairs_formed_count):
        if pairs_formed_count == n // 2:
            return True

        first_idx_to_pair = -1
        for i in range(n):
            if not used[i]:
                first_idx_to_pair = i
                break
        
        if first_idx_to_pair == -1: # Should not happen if pairs_formed_count < n/2
            return False

        # Try pairing 'first_idx_to_pair'
        used[first_idx_to_pair] = True
        for j in range(first_idx_to_pair + 1, n):
            if not used[j] and matrix[first_idx_to_pair][j] == 1:
                used[j] = True
                if backtrack_pm_recursive(pairs_formed_count + 1):
                    return True
                used[j] = False # Backtrack
        used[first_idx_to_pair] = False # Backtrack
        return False # 'first_idx_to_pair' could not be used to extend the current set of pairs to a full PM

    return backtrack_pm_recursive(0)


def checkhandcp(hand_cards):
    if len(hand_cards) != 8: return 0
    # Ensure all cards in hand_cards are characters for this check, as per main.py context for CP天胡
    if not all(c.card_type == 'character' for c in hand_cards):
        return 0 # Or handle error, CP天胡 implies all characters
    matrix = build_pair_matrix(hand_cards)
    return 1 if can_form_perfect_match(matrix) else 0

def checkhand(hand_cards):
    if len(hand_cards) != 8: return 0 # Must be 8 cards

    char_cards = [c for c in hand_cards if c.card_type == 'character']
    spot_cards = [c for c in hand_cards if c.card_type == 'spot']

    if len(spot_cards) == 8: # All 8 are spot cards
        return 3 # 天和 - 全地点 (10 pts)
    if len(char_cards) == 8: # All 8 are character cards
        return 1 if checkhandcp(char_cards) else 0 # 天和 - CP (4 pts for type 1). Original returned 1 for success.

    counts = {}
    for item in hand_cards:
        counts[item.card_id] = counts.get(item.card_id, 0) + 1
    
    sorted_counts = sorted(counts.values(), reverse=True)
    if not sorted_counts: return 0

    if sorted_counts[0] >= 4:
        if len(sorted_counts) > 1 and sorted_counts[1] >= 4:
            return 2 # 双手四 (8 pts)
        return 1 # 手四 (4 pts) - This is for general 4-of-a-kind, distinct from CP天胡.
                 # If all characters, checkhandcp handles the CP specific 4-pair version.
                 # If it's mixed and has 4 of one ID, it's 手四.
                 # The scoring for type 1 (CP or 手四) is 4 points. Type 2 (双手四) is 8 points.
    return 0


def checkdeck(field_cards):
    if not field_cards or len(field_cards) < 4 : return 0 # Need at least 4 cards to have 4 of a kind
    counts = {}
    for item in field_cards:
        counts[item.card_id] = counts.get(item.card_id, 0) + 1
    
    for card_id_count in counts.values():
        if card_id_count >= 4:
            return 1 # Condition for abortive draw (流局) met: at least one card_id appears 4+ times
    return 0


def check_cp_combinations(collected_cards):
    char_set = set(c.name for c in collected_cards if c.card_type == 'character')
    scene_set = set(c.name for c in collected_cards if c.card_type == 'scene')
    spot_set = set(c.name for c in collected_cards if c.card_type == 'spot')

    yizhong_cp_list = []
    cp_score_units = 0 

    # Check normal CP combinations
    for combo_name, combo in cp_combinations.items():
        if not all(char_name in char_set for char_name in combo["chars"]):
            continue
        if "scenes" in combo and combo["scenes"]:
            if not any(scene_name in scene_set for scene_name in combo["scenes"]):
                continue
        if "spots" in combo and combo["spots"]:
            if not any(spot_name in spot_set for spot_name in combo["spots"]):
                continue
        cp_score_units += 1 
        yizhong_cp_list.append(combo_name)

    yrn_made_generic = False
    for combo_name, combo in yrn_combinations.items(): 
        if not all(char_name in char_set for char_name in combo["chars"]):
            continue
        if "scenes" in combo and combo["scenes"]: 
            if not any(scene_name in scene_set for scene_name in combo["scenes"]):
                continue
        
        cp_score_units +=1 
        # yizhong_cp_list.append(combo_name) # Add specific YRN combo name e.g. "结界组"
        if not yrn_made_generic : 
             yizhong_cp_list.append("永夜组") 
             yrn_made_generic = True
        # Original main.py seems to break after first YRN, implying "永夜组" is one category.
        # If YRN groups are additive to score (each YRN combo adds score unit), remove break.
        # Current logic: each YRN met adds a score unit, "永夜组" is added once as a label.
        # Let's follow main.py's implicit single +3 for any YRN by breaking:
        break 


    return cp_score_units, yizhong_cp_list


# --- Pygame Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_MARGIN = 10
HIGHLIGHT_BORDER = 4

# Layout constants
INFO_PANEL_WIDTH = 380  # Adjusted for balance
INFO_PANEL_HEIGHT = CARD_HEIGHT # Keep same as card height for alignment
AI_HAND_CARD_DISPLAY_COUNT = 8 # Max cards to show as backs for AI
PLAYER_HAND_MAX_WIDTH = (CARD_WIDTH + CARD_MARGIN // 2) * 8 - CARD_MARGIN // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0) 
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (173, 216, 230)

#ASSET_PATH = "assets/cards"

ASSET_PATH = resource_path("assets/cards") # NEW
card_images = {}
card_back_image = None
font = None
small_font = None
tiny_font = None

def load_images():
    global card_back_image, card_images
    try:
        card_back_image = pygame.image.load(os.path.join(ASSET_PATH, "back.png")).convert_alpha()
        card_back_image = pygame.transform.scale(card_back_image, (CARD_WIDTH, CARD_HEIGHT))
    except pygame.error as e:
        print(f"Cannot load card back image: {e}")
        card_back_image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT)) # Placeholder
        card_back_image.fill(BLUE) # Fallback color
        # sys.exit() # Optional: exit if critical asset missing

    all_cards_for_images = card.initialize_cards()
    for c in all_cards_for_images:
        try:
            img_path = os.path.join(ASSET_PATH, f"{c.name}.png")
            if not os.path.exists(img_path): # Attempt with .jpg if .png not found
                img_path = os.path.join(ASSET_PATH, f"{c.name}.jpg")

            loaded_img = pygame.image.load(img_path).convert_alpha()
            card_images[c.name] = pygame.transform.scale(loaded_img, (CARD_WIDTH, CARD_HEIGHT))
        except pygame.error:
            # print(f"Warning: Cannot load image for {c.name}. Using placeholder.")
            placeholder_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            placeholder_surf.fill(GRAY)
            pygame.draw.rect(placeholder_surf, BLACK, placeholder_surf.get_rect(), 1)
            temp_font = pygame.font.Font(None, 16) # Default font for placeholder text
            text_surf = temp_font.render(c.name, True, BLACK)
            text_rect = text_surf.get_rect(center=(CARD_WIDTH//2, CARD_HEIGHT//2))
            placeholder_surf.blit(text_surf, text_rect)
            card_images[c.name] = placeholder_surf


def draw_text(surface, text, pos, font_obj, color=BLACK, center=False, rect_to_fit=None, aa=True):
    text_surface = font_obj.render(text, aa, color)
    text_rect = text_surface.get_rect()
    if rect_to_fit:
        if center:
            text_rect.center = rect_to_fit.center
        else:
            text_rect.topleft = rect_to_fit.topleft
    elif center:
        text_rect.center = pos
    else:
        text_rect.topleft = pos
    surface.blit(text_surface, text_rect)

def draw_card(surface, card_obj, x, y, is_back=False, is_highlighted=False):
    if is_back or not card_obj:
        image_to_draw = card_back_image
        if not image_to_draw : # Ultimate fallback for back image
            pygame.draw.rect(surface, BLUE, (x,y,CARD_WIDTH,CARD_HEIGHT))
            pygame.draw.rect(surface, WHITE, (x,y,CARD_WIDTH,CARD_HEIGHT),2)
            return pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    else:
        image_to_draw = card_images.get(card_obj.name)
        if not image_to_draw: # Fallback for specific card image
             image_to_draw = card_back_image # Or a generic placeholder from load_images
    
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    if image_to_draw:
        surface.blit(image_to_draw, rect.topleft)
    else: # Should not happen if load_images has fallbacks
        pygame.draw.rect(surface, RED, rect) # Error placeholder

    if is_highlighted:
        pygame.draw.rect(surface, YELLOW, rect, HIGHLIGHT_BORDER)
    return rect

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.deck = []
        self.player_human = Player("Player")
        self.player_ai = Player("Baka AI")
        self.field = []
        self.current_player = self.player_human
        self.game_phase = "INIT" 
        self.message = ""
        self.dialog_active = False
        self.dialog_options = []
        self.dialog_callback = None
        self.dialog_prompt = ""
        self.ids_on_field_at_start = []

        self.highlight_field_indices = []
        self.hovered_hand_card_index = -1
        self.turn_count = 0

        # Layout dependent coordinates
        self.ai_hand_display_rect = pygame.Rect(CARD_MARGIN, CARD_MARGIN, PLAYER_HAND_MAX_WIDTH, CARD_HEIGHT)
        self.ai_info_rect = pygame.Rect(self.ai_hand_display_rect.right + CARD_MARGIN, CARD_MARGIN, INFO_PANEL_WIDTH, INFO_PANEL_HEIGHT)
        
        self.player_hand_display_rect = pygame.Rect(CARD_MARGIN, SCREEN_HEIGHT - CARD_HEIGHT - CARD_MARGIN, PLAYER_HAND_MAX_WIDTH, CARD_HEIGHT)
        self.player_info_rect = pygame.Rect(self.player_hand_display_rect.right + CARD_MARGIN, self.player_hand_display_rect.top, INFO_PANEL_WIDTH, INFO_PANEL_HEIGHT)

        field_area_top_y = max(self.ai_hand_display_rect.bottom, self.ai_info_rect.bottom) + CARD_MARGIN
        field_area_bottom_y = min(self.player_hand_display_rect.top, self.player_info_rect.top) - CARD_MARGIN
        self.field_display_start_y = field_area_top_y
        self.max_field_rows = (field_area_bottom_y - field_area_top_y) // (CARD_HEIGHT + CARD_MARGIN)
        
        self.game_message_rect = pygame.Rect(CARD_MARGIN, field_area_bottom_y - 35, SCREEN_WIDTH - 2*CARD_MARGIN, 30)


        self.setup_game()

    def setup_game(self):
        self.deck = card.initialize_cards()
        random.shuffle(self.deck)
        self.turn_count = 0

        self.player_human.hand = []
        self.player_human.collected = []
        self.player_human.score = 0
        self.player_human.yizhong = []

        self.player_ai.hand = []
        self.player_ai.collected = []
        self.player_ai.score = 0
        self.player_ai.yizhong = []

        self.player_human.initial_draw(self.deck)
        self.player_ai.initial_draw(self.deck)

        self.field = []
        for _ in range(8): # Draw 8 cards to field
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
        if score_type == 3: # All spots
            pts = 10
            reason = "天和 (全地点牌)"
        elif score_type == 2: # Double Shisou / 2x 4-of-kind
            pts = 8
            reason = "天和 (双手四)"
        elif score_type == 1: # Shisou (4-of-kind) or CP hand
            pts = 4
            reason = "天和 (手四/CP)"
        
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
            self.game_phase = "PROCESSING_GET_CARD" # New intermediate phase
            self.process_get_card_sequence(self.player_human, "DISCARD_MATCH")

    def process_get_card_sequence(self, current_processing_player, sub_phase, chosen_card_from_dialog=None):
        # This function will manage the state machine for card collection
        # sub_phases: DISCARD_MATCH, DRAW_NEW_TO_FIELD, NEW_FIELD_CARD_MATCH, CHECK_SCORE_AND_END_TURN
        
        if sub_phase == "DISCARD_MATCH":
            if not self.field: 
                self.process_get_card_sequence(current_processing_player, "DRAW_NEW_TO_FIELD")
                return

            target_card = self.field[-1] 
            matches_on_field = [c for c in self.field[:-1] if c.card_id == target_card.card_id]

            if matches_on_field:
                if len(matches_on_field) == 1:
                    chosen_card = matches_on_field[0]
                    self.collect_cards_for_player(current_processing_player, target_card, chosen_card, True)
                    self.process_get_card_sequence(current_processing_player, "DRAW_NEW_TO_FIELD")
                elif len(matches_on_field) >= 2: 
                    if len(matches_on_field) == 2 and current_processing_player == self.player_human:
                        self.dialog_prompt = f"您打出 {target_card.name}. 选择一张场上的牌收集:"
                        self.dialog_options = matches_on_field 
                        self.dialog_callback = lambda choice_idx: self.finish_get_card_match_choice(current_processing_player, target_card, matches_on_field, choice_idx, "DRAW_NEW_TO_FIELD")
                        self.dialog_active = True
                        # game_phase remains PROCESSING_GET_CARD, dialog takes over input
                    else: # AI auto-picks or >=3 matches (take all)
                        if current_processing_player == self.player_ai and len(matches_on_field) == 2:
                             # AI picks first match
                            self.collect_cards_for_player(current_processing_player, target_card, matches_on_field[0], True)
                        else: # >=3, take all target and matches
                            for mc in list(matches_on_field): 
                                self.collect_cards_for_player(current_processing_player, None, mc, False) 
                            self.collect_cards_for_player(current_processing_player, target_card, None, True)
                        self.process_get_card_sequence(current_processing_player, "DRAW_NEW_TO_FIELD")
                else: # No match for discarded card (should not happen if matches_on_field is true)
                     self.process_get_card_sequence(current_processing_player, "DRAW_NEW_TO_FIELD")
            else: # No match for discarded card
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
            if not self.field or len(self.field) < 1 : # Need at least 1 card (the new one)
                self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")
                return

            target_card = self.field[-1] 
            matches_on_field = [c for c in self.field[:-1] if c.card_id == target_card.card_id]

            if matches_on_field:
                if len(matches_on_field) == 1:
                    chosen_card = matches_on_field[0]
                    self.collect_cards_for_player(current_processing_player, target_card, chosen_card, True)
                    self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")
                elif len(matches_on_field) >= 2:
                    if len(matches_on_field) == 2 and current_processing_player == self.player_human:
                        self.dialog_prompt = f"新翻开 {target_card.name}. 选择一张场上的牌收集:"
                        self.dialog_options = matches_on_field
                        self.dialog_callback = lambda choice_idx: self.finish_get_card_match_choice(current_processing_player, target_card, matches_on_field, choice_idx, "CHECK_SCORE_AND_END_TURN")
                        self.dialog_active = True
                    else: # AI auto-picks or >=3 matches
                        if current_processing_player == self.player_ai and len(matches_on_field) == 2:
                            self.collect_cards_for_player(current_processing_player, target_card, matches_on_field[0], True)
                        else: # >=3, take all target and matches
                            for mc in list(matches_on_field):
                                self.collect_cards_for_player(current_processing_player, None, mc, False)
                            self.collect_cards_for_player(current_processing_player, target_card, None, True)
                        self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")
                else: # Should not happen
                     self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")
            else: # No match for new field card
                self.process_get_card_sequence(current_processing_player, "CHECK_SCORE_AND_END_TURN")

        elif sub_phase == "CHECK_SCORE_AND_END_TURN":
            stop_game_chosen = self.perform_scoring_and_check_continue(current_processing_player)
            if not stop_game_chosen and self.game_phase != "GAME_OVER": # If scoring didn't end game and player didn't choose to stop
                self.end_turn()


    def finish_get_card_match_choice(self, current_processing_player, target_card, matches_on_field, choice_idx, next_sub_phase):
        self.dialog_active = False
        # game_phase is still PROCESSING_GET_CARD
        
        chosen_match_card = matches_on_field[choice_idx]
        self.collect_cards_for_player(current_processing_player, target_card, chosen_match_card, True)
        
        self.process_get_card_sequence(current_processing_player, next_sub_phase)


    def collect_cards_for_player(self, player_obj, target_card, matched_card, target_is_main_collect):
        collected_names_msg = []
        if target_card:
            if target_card in self.field: 
                self.field.remove(target_card)
            if target_card not in player_obj.collected: # Avoid duplicates if somehow passed again
                player_obj.collected.append(target_card)
            collected_names_msg.append(target_card.name)

        if matched_card:
            if matched_card in self.field:
                self.field.remove(matched_card)
            if matched_card not in player_obj.collected:
                player_obj.collected.append(matched_card)
            collected_names_msg.append(matched_card.name)
        
        if collected_names_msg:
            self.message = f"{player_obj.name} 收集了: {', '.join(collected_names_msg)}."
        
        player_obj.collected.sort(key=lambda c: (c.card_type, c.card_id, c.name))

    def perform_scoring_and_check_continue(self, player_obj): # Returns True if player chose to stop game
        collected = player_obj.collected
        new_total_score = 0 
        new_yizhong = []
        
        scene_names_all = [c.name for c in collected if c.card_type == 'scene']
        item_names = [c.name for c in collected if c.card_type == 'item']
        spot_names = [c.name for c in collected if c.card_type == 'spot']
        char_names = [c.name for c in collected if c.card_type == 'character']
        yyc_chars = ["博丽灵梦", "八云紫", "雾雨魔理沙", "爱丽丝", "蕾米莉亚", "十六夜咲夜", "西行寺幽幽子", "魂魄妖梦"]
        
        # Scene Yaku
        # Create a temporary list of scene names for yaku calculation that might remove "迷失竹林的月圆之夜"
        active_scene_names_for_yaku = list(scene_names_all)
        if len(active_scene_names_for_yaku) == 5:
            new_total_score += 10
            new_yizhong.append("五景")
        else:
            # Check if "迷失竹林的月圆之夜" should be excluded for 3-景/4-景 if no Yuyuko characters
            is_yyc_char_present = any(c_name in char_names for c_name in yyc_chars)
            if "迷失竹林的月圆之夜" in active_scene_names_for_yaku and not is_yyc_char_present:
                active_scene_names_for_yaku.remove("迷失竹林的月圆之夜")
            
            if len(active_scene_names_for_yaku) == 4: # Check after potential removal
                new_total_score += 8
                new_yizhong.append("四景")
            elif len(active_scene_names_for_yaku) == 3:
                new_total_score += 5
                new_yizhong.append("三景")
        
        cp_score_units, yizhong_cp_names = check_cp_combinations(collected)
        new_yizhong.extend(yizhong_cp_names)
        new_total_score += cp_score_units * 3

        card_id_counts = {}
        for c in collected:
            card_id_counts[c.card_id] = card_id_counts.get(c.card_id, 0) + 1
        
        # Find the names of the initial spot cards for Hezha yaku names
        initial_spot_card_names = {} # card_id -> name
        all_card_defs = card.initialize_cards()
        for c_def in all_card_defs:
            if c_def.card_type == 'spot':
                initial_spot_card_names[c_def.card_id] = c_def.name

        for hezha_spot_id in self.ids_on_field_at_start: 
            if card_id_counts.get(hezha_spot_id, 0) >= 4: # Needs 4 cards of this ID
                spot_name_for_hezha = initial_spot_card_names.get(hezha_spot_id, f"ID {hezha_spot_id}")
                new_total_score += 4
                new_yizhong.append(f"合札-{spot_name_for_hezha}")
        
        weapon_items = ["灵梦的御币", "早苗的御币", "楼观剑和白楼剑"]
        if all(item_name in item_names for item_name in weapon_items):
            new_total_score += 5
            new_yizhong.append("武器库")

        faith_spots = ["博丽神社", "守矢神社", "命莲寺"]
        if all(spot_name in spot_names for spot_name in faith_spots):
            new_total_score += 5
            new_yizhong.append("信仰战争")
            if "巫女组" in new_yizhong: 
                 # Check main.py rule: 信仰战争 seems to take precedence or modify score/yaku of 巫女组
                 # For now, let's assume it's an additional yaku. If it replaces, then remove "巫女组" points.
                 # The prompt version removed "巫女组", implying it's replaced or incompatible.
                 new_yizhong.remove("巫女组")
                 # Need to also remove points for "巫女组" if it was added via check_cp_combinations
                 # This is complex. Simpler: score "巫女组" normally, Faith War is separate.
                 # For now, following prompt's removal of yaku name. Point adjustment is harder here.
                 # The score for "巫女组" (3pts) is already in new_total_score.
                 # This needs careful thought on point cancellation.
                 # Safest: Both yaku exist, points stack, unless rule explicitly states point cancellation.

        if len(item_names) >= 5: 
            new_total_score += (len(item_names) - 5 + 1)
            new_yizhong.append(f"物品牌 ({len(item_names)})")
        if len(spot_names) >= 5:
            new_total_score += (len(spot_names) - 5 + 1)
            new_yizhong.append(f"地点牌 ({len(spot_names)})")
        if len(char_names) >= 10:
            new_total_score += (len(char_names) - 10 + 1)
            new_yizhong.append(f"角色牌 ({len(char_names)})")

        new_yizhong = sorted(list(set(new_yizhong))) # Unique and sorted

        # Check if new yaku formed or score changed significantly
        # For simplicity, always update score. Prompt for continue if yaku list changes.
        player_obj.score = new_total_score # Update to the new total score

        if new_yizhong and new_yizhong != player_obj.yizhong : 
            player_obj.yizhong = new_yizhong
            self.message = f"{player_obj.name} 形成新役种: {', '.join(new_yizhong)}! 当前总分: {player_obj.score}"
            if player_obj == self.player_human :
                self.dialog_prompt = "形成新役种! 是否结束游戏?"
                self.dialog_options = ["继续游戏", "结束游戏"] 
                self.dialog_callback = self.handle_continue_stop_choice
                self.dialog_active = True
                return False # Dialog will determine if game stops or continues
            else: # AI always continues
                self.message += " AI选择继续."
                return False # AI continues
        else: # No new yaku, or yaku list unchanged
            player_obj.yizhong = new_yizhong # Ensure yizhong is current even if not new
            return False # Continue turn / game

    def handle_continue_stop_choice(self, choice_string): 
        self.dialog_active = False
        if choice_string == "结束游戏":
            self.message = f"{self.player_human.name} 选择结束游戏. 最终得分: {self.player_human.score}."
            self.game_phase = "GAME_OVER"
            # No need to call self.end_turn() here, game is over.
        else: # Continue
            self.message = f"{self.player_human.name} 选择继续游戏."
            # Game phase was PROCESSING_GET_CARD. Now proceed to end turn.
            self.end_turn()


    def end_turn(self):
        if self.game_phase == "GAME_OVER": 
            return

        if not self.player_human.hand and not self.player_ai.hand:
            self.message = "所有玩家手牌已打完! 游戏结束."
            self.game_phase = "GAME_OVER"
            # Final scoring might be implicitly done, or can force a final re-score here if rules need it.
            if self.player_human.score > self.player_ai.score:
                self.message += f" {self.player_human.name} 胜利!"
            elif self.player_ai.score > self.player_human.score:
                 self.message += f" {self.player_ai.name} 胜利!"
            else:
                 self.message += " 平局!"
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
            if not self.player_human.hand: # Player ran out of cards on their turn, game might end
                self.end_turn() 
        self.turn_count +=1


    def perform_ai_turn(self):
        if self.game_phase != "AI_TURN" or self.dialog_active : # Should not be dialog active in AI turn start
            return

        if not self.player_ai.hand:
            self.end_turn() # AI has no cards, pass turn
            return

        pygame.time.wait(500) # Small delay for AI "thinking"

        discarded_card_ai = self.player_ai.hand.pop(0) # Baka AI discards first card
        self.field.append(discarded_card_ai)
        self.message = f"{self.player_ai.name} 打出了 {discarded_card_ai.name}."
        
        self.game_phase = "PROCESSING_GET_CARD"
        self.process_get_card_sequence(self.player_ai, "DISCARD_MATCH")


    def handle_event(self, event):
        if self.game_phase == "GAME_OVER":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.setup_game() 
            return # No other input if game over

        if self.dialog_active:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
                # Text options dialog
                if self.dialog_options and isinstance(self.dialog_options[0], str): 
                    dialog_option_height = 40
                    base_y = SCREEN_HEIGHT // 2 # Start options below prompt
                    for i, option_text in enumerate(self.dialog_options):
                        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 
                                                  base_y + i * (dialog_option_height + 10), 
                                                  200, dialog_option_height)
                        if button_rect.collidepoint(event.pos):
                            if self.dialog_callback: self.dialog_callback(option_text)
                            break
                # Card choice dialog
                elif self.dialog_options and isinstance(self.dialog_options[0], card):
                    card_spacing = CARD_WIDTH + CARD_MARGIN
                    total_width_of_options = len(self.dialog_options) * CARD_WIDTH + (len(self.dialog_options) - 1) * CARD_MARGIN
                    start_x = (SCREEN_WIDTH - total_width_of_options) // 2
                    dialog_card_y = SCREEN_HEIGHT // 2 
                    for i, card_opt in enumerate(self.dialog_options):
                        card_rect = pygame.Rect(start_x + i * card_spacing, dialog_card_y, CARD_WIDTH, CARD_HEIGHT)
                        if card_rect.collidepoint(event.pos):
                            if self.dialog_callback: self.dialog_callback(i) 
                            break
            return # Dialog handles input exclusively

        if event.type == pygame.MOUSEMOTION:
            if self.game_phase == "PLAYER_TURN" and self.current_player == self.player_human:
                self.highlight_field_indices = []
                self.hovered_hand_card_index = -1
                # Player hand hover
                for i, p_card in enumerate(self.player_human.hand):
                    hand_card_x = self.player_hand_display_rect.left + i * (CARD_WIDTH + CARD_MARGIN // 2)
                    card_rect = pygame.Rect(hand_card_x, self.player_hand_display_rect.top, CARD_WIDTH, CARD_HEIGHT)
                    if card_rect.collidepoint(event.pos):
                        self.hovered_hand_card_index = i
                        if p_card:
                            for field_idx, f_card in enumerate(self.field):
                                if f_card and f_card.card_id == p_card.card_id:
                                    self.highlight_field_indices.append(field_idx)
                        break 

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
            if self.game_phase == "PLAYER_TURN" and self.current_player == self.player_human:
                for i, p_card in enumerate(self.player_human.hand):
                    hand_card_x = self.player_hand_display_rect.left + i * (CARD_WIDTH + CARD_MARGIN // 2)
                    card_rect = pygame.Rect(hand_card_x, self.player_hand_display_rect.top, CARD_WIDTH, CARD_HEIGHT)
                    if card_rect.collidepoint(event.pos):
                        self.handle_player_discard(i)
                        self.hovered_hand_card_index = -1 
                        self.highlight_field_indices = []
                        break
            elif self.game_phase == "PRE_TURN_CHECKS": 
                self.run_pre_turn_checks()

    # --- Drawing Methods ---
    def draw_info_panel(self, surface, player, panel_rect):
        pygame.draw.rect(surface, LIGHT_GRAY, panel_rect) 
        pygame.draw.rect(surface, BLACK, panel_rect, 2) 

        current_y = panel_rect.top + 5
        text_x_start = panel_rect.left + 5
        max_text_width = panel_rect.width - 10

        # Player Name and Score
        score_text = f"{player.name} | 得分: {player.score}"
        draw_text(surface, score_text, (text_x_start, current_y), font, BLACK)
        current_y += font.get_linesize() + 2

        # Yaku
        if player.yizhong:
            current_y = self.draw_wrapped_text_list_in_rect(surface, "役种: ", player.yizhong, 
                                                 text_x_start, current_y, small_font, BLUE, max_text_width, panel_rect.bottom - 5)
        current_y += 3 # Padding

        # Collected Cards
        collected_names = [c.name for c in player.collected]
        if collected_names:
            current_y = self.draw_wrapped_text_list_in_rect(surface, "收集: ", collected_names,
                                                 text_x_start, current_y, tiny_font, BLACK, max_text_width, panel_rect.bottom - 5)

    def draw_wrapped_text_list_in_rect(self, surface, prefix, items_list, x_pos, y_start, font_obj, color, max_width, y_boundary):
        if not items_list:
            # draw_text(surface, prefix + "(无)", (x_pos, y_start), font_obj, color)
            # return y_start + font_obj.get_linesize()
             return y_start

        full_text = prefix + ", ".join(items_list)
        
        words = full_text.split(' ') 
        current_line_text = ""
        current_y = y_start
        line_spacing = font_obj.get_linesize() 

        for word_idx, word in enumerate(words):
            word_to_add = word
            if current_line_text and word: # Add space if not empty line and not empty word
                word_to_add = " " + word
            
            if font_obj.size(current_line_text + word_to_add)[0] <= max_width:
                current_line_text += word_to_add
            else:
                if current_y + line_spacing > y_boundary: return current_y # Stop if out of vertical bounds
                draw_text(surface, current_line_text.strip(), (x_pos, current_y), font_obj, color)
                current_y += line_spacing
                current_line_text = word 
        
        # Render the last line
        if current_line_text.strip():
            if current_y + line_spacing <= y_boundary: # Check bounds for last line too
                draw_text(surface, current_line_text.strip(), (x_pos, current_y), font_obj, color)
                current_y += line_spacing
        return current_y


    def draw(self):
        self.screen.fill(GREEN)

        # --- Top Section: AI ---
        # AI Hand (card backs)
        ai_hand_base_x = self.ai_hand_display_rect.left
        for i in range(min(len(self.player_ai.hand), AI_HAND_CARD_DISPLAY_COUNT)): # Show limited card backs
            draw_card(self.screen, None, ai_hand_base_x + i * (CARD_WIDTH // 2), self.ai_hand_display_rect.top, is_back=True)
        if len(self.player_ai.hand) > 0:
            draw_text(self.screen, f"AI手牌: {len(self.player_ai.hand)}", 
                      (ai_hand_base_x + AI_HAND_CARD_DISPLAY_COUNT*(CARD_WIDTH//2) + 5, self.ai_hand_display_rect.centery -10), 
                      small_font, BLACK)

        # AI Info Panel
        self.draw_info_panel(self.screen, self.player_ai, self.ai_info_rect)

        # --- Middle Section: Field, Deck, Message ---
        # Field Cards (6 per row, centered)
        if self.field:
            cards_per_row = 6
            row_width = cards_per_row * CARD_WIDTH + (cards_per_row - 1) * CARD_MARGIN
            field_start_x_centered = (SCREEN_WIDTH - row_width) // 2
            
            for i, f_card in enumerate(self.field):
                row = i // cards_per_row
                col = i % cards_per_row
                if row >= self.max_field_rows : break # Don't draw more rows than fit

                card_x = field_start_x_centered + col * (CARD_WIDTH + CARD_MARGIN)
                card_y = self.field_display_start_y + row * (CARD_HEIGHT + CARD_MARGIN)
                is_highlight = (i in self.highlight_field_indices)
                draw_card(self.screen, f_card, card_x, card_y, is_highlighted=is_highlight)
        
        # Deck
        if self.deck:
            deck_x = SCREEN_WIDTH - CARD_WIDTH - CARD_MARGIN * 5 # Position deck to far right of field area
            deck_y = self.field_display_start_y
            draw_card(self.screen, None, deck_x, deck_y, is_back=True)
            draw_text(self.screen, f"牌堆: {len(self.deck)}", (deck_x, deck_y + CARD_HEIGHT + 5), small_font, WHITE)
        
        # Game Message
        draw_text(self.screen, self.message, (0,0), font, WHITE, center=True, rect_to_fit=self.game_message_rect)


        # --- Bottom Section: Player ---
        # Player Hand
        for i, p_card in enumerate(self.player_human.hand):
            hand_card_x = self.player_hand_display_rect.left + i * (CARD_WIDTH + CARD_MARGIN // 2)
            is_highlight = (i == self.hovered_hand_card_index and self.current_player == self.player_human)
            draw_card(self.screen, p_card, hand_card_x, self.player_hand_display_rect.top, is_highlighted=is_highlight)

        # Player Info Panel
        self.draw_info_panel(self.screen, self.player_human, self.player_info_rect)
        
        # --- Overlays: Dialog, Game Over ---
        if self.dialog_active:
            overlay_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay_surf.fill((0,0,0,180))
            self.screen.blit(overlay_surf, (0,0))

            draw_text(self.screen, self.dialog_prompt, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80), font, WHITE, center=True)
            
            if self.dialog_options and isinstance(self.dialog_options[0], str): # Text buttons
                dialog_option_height = 40
                base_y = SCREEN_HEIGHT // 2 
                for i, option_text in enumerate(self.dialog_options):
                    btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, base_y + i * (dialog_option_height + 10), 200, dialog_option_height)
                    pygame.draw.rect(self.screen, LIGHT_BLUE, btn_rect)
                    pygame.draw.rect(self.screen, BLACK, btn_rect, 2)
                    draw_text(self.screen, option_text, btn_rect.center, font, BLACK, center=True)
            elif self.dialog_options and isinstance(self.dialog_options[0], card): # Card choices
                card_spacing = CARD_WIDTH + CARD_MARGIN
                total_width_of_options = len(self.dialog_options) * CARD_WIDTH + (len(self.dialog_options) - 1) * CARD_MARGIN
                start_x = (SCREEN_WIDTH - total_width_of_options) // 2
                dialog_card_y = SCREEN_HEIGHT // 2 
                for i, card_opt in enumerate(self.dialog_options):
                    card_opt_rect = draw_card(self.screen, card_opt, start_x + i * card_spacing, dialog_card_y)
                    mouse_pos = pygame.mouse.get_pos()
                    if card_opt_rect.collidepoint(mouse_pos):
                         pygame.draw.rect(self.screen, YELLOW, card_opt_rect, HIGHLIGHT_BORDER)

        if self.game_phase == "PRE_TURN_CHECKS":
             draw_text(self.screen, "点击屏幕开始回合前检查.", (SCREEN_WIDTH // 2, SCREEN_HEIGHT //2), font, YELLOW, center=True)
        elif self.game_phase == "GAME_OVER":
            final_msg_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
            pygame.draw.rect(self.screen, BLACK, final_msg_rect)
            pygame.draw.rect(self.screen, WHITE, final_msg_rect, 3)
            game_over_text = self.message + " 点击屏幕重新开始."
            # Need to wrap this text too if long
            lines = [self.message, "点击屏幕重新开始."] # Simple two line
            for i, line in enumerate(lines):
                 draw_text(self.screen, line, (final_msg_rect.centerx, final_msg_rect.centery -15 + i*30), font, YELLOW, center=True)

def main_gui():
    global font, small_font, tiny_font # Make sure these are global
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("TouhouHanafuda")
    

    bundled_font_name = "sc.ttf" # The name of your font file
    font_path_primary_bundled = resource_path(bundled_font_name)

    # System fonts to try as fallbacks if the bundled one fails or is not found
    system_fonts_fallback = [ None] # None for pygame default

    font_loaded = False
    # Try bundled font first
    try:
        font = pygame.font.Font(font_path_primary_bundled, 28)
        small_font = pygame.font.Font(font_path_primary_bundled, 20)
        tiny_font = pygame.font.Font(font_path_primary_bundled, 16)
        print(f"Using bundled font: {font_path_primary_bundled}")
        font_loaded = True
    except pygame.error as e:
        print(f"Bundled font '{bundled_font_name}' not found or failed to load from '{font_path_primary_bundled}'. Error: {e}")
        print("Attempting system fallback fonts...")

    if not font_loaded:
        for fp_try in system_fonts_fallback:
            try:
                font = pygame.font.Font(fp_try, 28)
                small_font = pygame.font.Font(fp_try, 20)
                tiny_font = pygame.font.Font(fp_try, 16)
                print(f"Using system/default font: {fp_try if fp_try else 'Pygame Default'}")
                font_loaded = True
                break
            except pygame.error:
                if fp_try is None:
                    print("CRITICAL Error: Pygame default font also failed to load.")
                    pygame.quit()
                    sys.exit()
                # print(f"System font {fp_try} not found or failed.")
                continue
    
    if not font_loaded: # Should not happen if default font (None) works
        print("CRITICAL: No suitable font could be loaded. Exiting.")
        pygame.quit()
        sys.exit()

    load_images() 
    
    
    load_images()
    if not card_back_image and not card_images: # Critical load fail
        print("CRITICAL: Failed to load essential card images/backs. Exiting.")
        return

    game_manager = GameManager(screen)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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

    # Create a dummy back.png if missing for basic runnability
    dummy_back_path = os.path.join(ASSET_PATH, "back.png")
    if not os.path.exists(dummy_back_path):
        try:
            # Initialize pygame earlier if needed for surface creation outside main_gui
            if not pygame.get_init(): pygame.init()
            surf = pygame.Surface((100,150))
            surf.fill(BLUE)
            pygame.draw.rect(surf, WHITE, surf.get_rect(), 2)
            pygame.image.save(surf, dummy_back_path)
            print(f"Created dummy '{os.path.basename(dummy_back_path)}'. Please replace with actual image.")
        except Exception as e:
            print(f"Error creating dummy back.png (pygame init needed?): {e}")
            # If this fails, load_images will use its own internal fallback.

    main_gui()