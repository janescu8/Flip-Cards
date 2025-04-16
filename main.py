import streamlit as st
import random
import time

EMOJI_THEMES = {
    'fruits': {
        1: "🍎", 2: "🍌", 3: "🍇", 4: "🍒", 5: "🍓",
        6: "🍍", 7: "🥝", 8: "🍑", 9: "🍉", 10: "🍋"
    },
    'animals': {
        1: "🐶", 2: "🐱", 3: "🐭", 4: "🐹", 5: "🐻",
        6: "🐼", 7: "🐰", 8: "🐸", 9: "🐯", 10: "🐺"
    },
    'faces': {
        1: "😊", 2: "😂", 3: "😜", 4: "😳", 5: "😮",
        6: "😠", 7: "😍", 8: "😭", 9: "😎", 10: "😡"
    }
}

LEVELS = {
    'Easy': 4,
    'Medium': 6,
    'Hard': 10
}

if 'theme' not in st.session_state:
    st.session_state['theme'] = 'fruits'
if 'level' not in st.session_state:
    st.session_state['level'] = 'Easy'
if 'time_limit' not in st.session_state:
    st.session_state['time_limit'] = 30
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = time.time()
if 'game_started' not in st.session_state:
    st.session_state['game_started'] = False

EMOJI_MAP = EMOJI_THEMES[st.session_state['theme']]
PAIR_COUNT = LEVELS[st.session_state['level']]
CARD_COUNT = PAIR_COUNT * 2

def generate_paired_cards():
    myNumbers = random.sample(range(1, 11), PAIR_COUNT)
    myNumbers_union = myNumbers + myNumbers
    random.shuffle(myNumbers_union)
    return [EMOJI_MAP[i] for i in myNumbers_union]

if 'cards' not in st.session_state:
    st.session_state['cards'] = generate_paired_cards()
    st.session_state['flipped'] = [False] * CARD_COUNT
    st.session_state['matches'] = [False] * CARD_COUNT
    st.session_state['first_card'] = None
    st.session_state['second_card'] = None
    st.session_state['attempts'] = 0
    st.session_state['step'] = None
    st.session_state['game_over'] = False

# 初始畫面 - 開始按鈕
if not st.session_state['game_started']:
    st.title("🎴 翻翻樂記憶遊戲 / Memory Flip Game")
    st.markdown("""
歡迎來到可愛的翻牌挑戰！ / Welcome to the Cute Flip Card Challenge!

- 選擇主題與難度 / Choose your theme and difficulty
- 在時間內找出所有配對卡牌 / Match all pairs before time runs out
- 點擊下方按鈕開始！ / Click the button below to start!
""")
    if st.button("🚀 開始遊戲"):
        st.session_state['game_started'] = True
        st.rerun()  # ⚠️ Fix for newer Streamlit versions
# 切換到 st.rerun() 以避免舊版 experimental_rerun() 出錯
# Switch to st.rerun() to avoid deprecated error in older environments
    st.stop()

# 遊戲正式畫面開始
st.title("Flip Card Game 🎮 / 翻牌遊戲")
st.write("Find all matching pairs before time runs out! / 在時間內找出所有配對卡牌！")
st.write(f"🔖 Current Level: {st.session_state['level']} / 當前難度：{st.session_state['level']}")

# Sidebar: settings
st.sidebar.subheader("Choose Emoji Theme")
selected_theme = st.sidebar.radio("Theme", list(EMOJI_THEMES.keys()), index=list(EMOJI_THEMES.keys()).index(st.session_state['theme']))
selected_level = st.sidebar.radio("Level", list(LEVELS.keys()), index=list(LEVELS.keys()).index(st.session_state['level']))

def flip_card(index):
    if st.session_state['flipped'][index] or st.session_state['matches'][index]:
        return

    if st.session_state['first_card'] is None:
        st.session_state['first_card'] = index
        st.session_state['flipped'][index] = True

    elif st.session_state['second_card'] is None:
        st.session_state['second_card'] = index
        st.session_state['flipped'][index] = True
        st.session_state['step'] = 'waiting'

def restart_game():
    st.session_state['cards'] = generate_paired_cards()
    st.session_state['flipped'] = [False] * len(st.session_state['cards'])
    st.session_state['matches'] = [False] * len(st.session_state['cards'])
    st.session_state['first_card'] = None
    st.session_state['second_card'] = None
    st.session_state['attempts'] = 0
    st.session_state['step'] = None
    st.session_state['start_time'] = time.time()
    st.session_state['game_over'] = False
    st.session_state['game_started'] = True

time_left = st.session_state['time_limit'] - int(time.time() - st.session_state['start_time'])
if time_left <= 0 and not all(st.session_state['matches']):
    st.session_state['game_over'] = True

if selected_theme != st.session_state['theme'] or selected_level != st.session_state['level']:
    st.session_state['theme'] = selected_theme
    st.session_state['level'] = selected_level
    EMOJI_MAP = EMOJI_THEMES[selected_theme]
    restart_game()

if st.session_state['game_over']:
    st.error("⏰ Time's up! Game Over. / 時間到，遊戲結束！")
    if st.button("Try Again / 再玩一次"):
        restart_game()
    st.stop()

with st.sidebar:
    timer_slot = st.empty()
    time_left = st.session_state['time_limit'] - int(time.time() - st.session_state['start_time'])
    if time_left <= 0 and not all(st.session_state['matches']):
        st.session_state['game_over'] = True
        st.rerun()
    timer_slot.markdown(f"⏱ Time left: **{time_left} sec**")

cols = st.columns(len(st.session_state['cards']))
for i, col in enumerate(cols):
    if st.session_state['matches'][i]:
        col.success(f"✓ {st.session_state['cards'][i]}")
    elif st.session_state['flipped'][i]:
        col.button(f"{st.session_state['cards'][i]}", key=f"card_{i}", on_click=lambda i=i: flip_card(i))
    else:
        col.button("❓", key=f"card_{i}", on_click=lambda i=i: flip_card(i))

if st.session_state.get('step') == 'waiting':
    time.sleep(0.5)
    first = st.session_state['first_card']
    second = st.session_state['second_card']
    st.session_state['attempts'] += 1
    if st.session_state['cards'][first] == st.session_state['cards'][second]:
        st.session_state['matches'][first] = True
        st.session_state['matches'][second] = True
    else:
        st.session_state['flipped'][first] = False
        st.session_state['flipped'][second] = False
    st.session_state['first_card'] = None
    st.session_state['second_card'] = None
    st.session_state['step'] = None

if all(st.session_state['matches']):
    st.balloons()
    stars = "⭐" * (3 if st.session_state['attempts'] <= CARD_COUNT else 2 if st.session_state['attempts'] <= CARD_COUNT + 3 else 1)
    st.success(f"""
You won in {st.session_state['attempts']} attempts! / 你用了 {st.session_state['attempts']} 次配對成功！
Score: {stars} / 星級評分：{stars}
""")
    if st.button("Play Next Round / 下一關"):
        next_level = {'Easy': 'Medium', 'Medium': 'Hard', 'Hard': 'Hard'}[st.session_state['level']]
        st.session_state['level'] = next_level
        restart_game()
else:
    st.write(f"Attempts: {st.session_state['attempts']} / 嘗試次數")
