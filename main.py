import streamlit as st
import random
import time

# --- 資料設定 ---
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
    'Hard': 7
}

def get_pair_count():
    return LEVELS[st.session_state['level']]

def get_card_count():
    return get_pair_count() * 2

# --- 初始化 Session State ---
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

def generate_paired_cards():
    myNumbers = random.sample(range(1, 11), get_pair_count())
    myNumbers_union = myNumbers + myNumbers
    random.shuffle(myNumbers_union)
    return [EMOJI_MAP[i] for i in myNumbers_union]

if 'cards' not in st.session_state:
    st.session_state['cards'] = generate_paired_cards()
    st.session_state['flipped'] = [False] * get_card_count()
    st.session_state['matches'] = [False] * get_card_count()
    st.session_state['first_card'] = None
    st.session_state['second_card'] = None
    st.session_state['attempts'] = 0
    st.session_state['step'] = None
    st.session_state['game_over'] = False

# --- 初始畫面 ---
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
        st.rerun()
    st.stop()

# --- 遊戲畫面 ---
st.title("Flip Card Game 🎮 / 翻牌遊戲")
st.write("Find all matching pairs before time runs out! / 在時間內找出所有配對卡牌！")
st.write(f"🔖 Current Level: {st.session_state['level']} / 當前難度：{st.session_state['level']}")

# --- 側欄設定：只保留主題切換 ---
st.sidebar.subheader("Choose Emoji Theme")
selected_theme = st.sidebar.radio("Theme", list(EMOJI_THEMES.keys()), index=list(EMOJI_THEMES.keys()).index(st.session_state['theme']))

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

# 主題變更時重新開始遊戲並重設難度
if selected_theme != st.session_state['theme']:
    st.session_state['theme'] = selected_theme
    st.session_state['level'] = 'Easy'
    EMOJI_MAP = EMOJI_THEMES[selected_theme]
    restart_game()

# 計時器
time_left = st.session_state['time_limit'] - int(time.time() - st.session_state['start_time'])
if time_left <= 0 and not all(st.session_state['matches']):
    st.session_state['game_over'] = True

if st.session_state['game_over']:
    st.error("⏰ Time's up! Game Over. / 時間到，遊戲結束！")
    if st.button("Try Again / 再玩一次"):
        st.session_state['level'] = 'Easy'
        restart_game()
    st.stop()

# 側欄顯示剩餘時間
with st.sidebar:
    timer_slot = st.empty()
    time_left = st.session_state['time_limit'] - int(time.time() - st.session_state['start_time'])
    if time_left <= 0 and not all(st.session_state['matches']):
        st.session_state['game_over'] = True
        st.rerun()
    timer_slot.markdown(f"⏱ Time left: **{time_left} sec**")

# --- 翻牌邏輯 ---
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

# --- 顯示卡牌 ---
cols = st.columns(len(st.session_state['cards']))
for i, col in enumerate(cols):
    if st.session_state['matches'][i]:
        col.success(f"✓ {st.session_state['cards'][i]}")
    elif st.session_state['flipped'][i]:
        col.button(f"{st.session_state['cards'][i]}", key=f"card_{i}", on_click=lambda i=i: flip_card(i))
    else:
        col.button("❓", key=f"card_{i}", on_click=lambda i=i: flip_card(i))

# --- 判斷配對 ---
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

# --- 通關判定 ---
if all(st.session_state['matches']):
    st.balloons()
    stars = "⭐" * (3 if st.session_state['attempts'] <= get_card_count() else 2 if st.session_state['attempts'] <= get_card_count() + 3 else 1)
    st.success(f"""
You won in {st.session_state['attempts']} attempts! / 你用了 {st.session_state['attempts']} 次配對成功！
Score: {stars} / 星級評分：{stars}
""")
    if st.session_state['level'] == 'Hard':
        st.success("🎉 You finished all levels! / 你已完成所有關卡！")
        if st.button("🔄 Restart Game / 重新開始"):
            st.session_state['level'] = 'Easy'
            st.session_state['game_started'] = False
            st.rerun()
        st.stop()
    else:
        if st.button("Play Next Round / 下一關"):
            next_level = {'Easy': 'Medium', 'Medium': 'Hard', 'Hard': 'Hard'}[st.session_state['level']]
            st.session_state['level'] = next_level
            restart_game()
else:
    st.write(f"Attempts: {st.session_state['attempts']} / 嘗試次數")
