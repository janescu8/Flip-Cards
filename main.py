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
    'Easy': 4,     # 2 pairs
    'Medium': 6,   # 3 pairs
    'Hard': 10     # 5 pairs
}

if 'theme' not in st.session_state:
    st.session_state['theme'] = 'fruits'
if 'level' not in st.session_state:
    st.session_state['level'] = 'Easy'
if 'time_limit' not in st.session_state:
    st.session_state['time_limit'] = 30
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = time.time()

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

# Load background music
with open("background_music.mp3", "rb") as bgm:
    st.audio(bgm.read(), format="audio/mp3", loop=True)

def play_sound(effect):
    sound_files = {
        'match': "match_sound.mp3",
        'fail': "fail_sound.mp3",
        'win': "win_sound.mp3",
        'lose': "lose_sound.mp3"
    }
    if effect in sound_files:
        with open(sound_files[effect], "rb") as s:
            st.audio(s.read(), format="audio/mp3")

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

st.title("Flip Card Game 🎮")
st.write("Find all matching pairs before time runs out!")

# Sidebar: settings
st.sidebar.title("Settings")
st.sidebar.subheader("Choose Emoji Theme")
selected_theme = st.sidebar.radio("Theme", list(EMOJI_THEMES.keys()), index=list(EMOJI_THEMES.keys()).index(st.session_state['theme']))
selected_level = st.sidebar.radio("Level", list(LEVELS.keys()), index=list(LEVELS.keys()).index(st.session_state['level']))

time_left = st.session_state['time_limit'] - int(time.time() - st.session_state['start_time'])
if time_left <= 0 and not all(st.session_state['matches']):
    st.session_state['game_over'] = True
    play_sound('lose')

# Reset if theme or level changes
if selected_theme != st.session_state['theme'] or selected_level != st.session_state['level']:
    st.session_state['theme'] = selected_theme
    st.session_state['level'] = selected_level
    EMOJI_MAP = EMOJI_THEMES[selected_theme]
    restart_game()

if st.session_state['game_over']:
    st.error("⏰ Time's up! Game Over.")
    if st.button("Try Again"):
        restart_game()
    st.stop()

st.sidebar.markdown(f"⏱ Time left: **{time_left} sec**")

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
        play_sound('match')
    else:
        st.session_state['flipped'][first] = False
        st.session_state['flipped'][second] = False
        play_sound('fail')
    st.session_state['first_card'] = None
    st.session_state['second_card'] = None
    st.session_state['step'] = None

if all(st.session_state['matches']):
    st.balloons()
    play_sound('win')
    stars = "⭐" * (3 if st.session_state['attempts'] <= CARD_COUNT else 2 if st.session_state['attempts'] <= CARD_COUNT + 3 else 1)
    st.success(f"You won in {st.session_state['attempts']} attempts! Score: {stars}")
    if st.button("Play Next Round"):
        next_level = {'Easy': 'Medium', 'Medium': 'Hard', 'Hard': 'Hard'}[st.session_state['level']]
        st.session_state['level'] = next_level
        restart_game()
else:
    st.write(f"Attempts: {st.session_state['attempts']}")
