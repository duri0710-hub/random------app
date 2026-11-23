import streamlit as st
import random
from collections import deque

st.set_page_config(
    page_title="Battery Star Hunter",
    page_icon="⭐",
    layout="centered"
)

SIZE = 6
START = (5, 0)
GOAL = (0, 5)

st.title("⭐ BATTERY STAR HUNTER")
st.caption("배터리를 아끼면서 모든 별을 모아 목적지에 도착하세요!")

# 난이도 설정
def get_settings(level):
    if level == 1:
        return 3, 22, 5
    elif level == 2:
        return 4, 24, 7
    elif level == 3:
        return 5, 26, 9
    elif level == 4:
        return 5, 24, 11
    else:
        return 6, 28, min(8 + level * 2, 18)


# 게임 초기화
if "level" not in st.session_state:
    st.session_state.level = 1
    st.session_state.score = 0
    st.session_state.lives = 3
    st.session_state.game_over = False
    st.session_state.message = ""

def shortest_route(obstacles, stars):
    """모든 별을 모으고 목적지까지 가는 최소 이동 횟수"""
    star_list = list(stars)
    star_index = {pos: i for i, pos in enumerate(star_list)}
    full_mask = (1 << len(star_list)) - 1

    queue = deque([(START, 0, 0)])
    visited = {(START, 0)}

    while queue:
        pos, mask, steps = queue.popleft()

        if pos == GOAL and mask == full_mask:
            return steps

        r, c = pos

        for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)

            if not (0 <= nr < SIZE and 0 <= nc < SIZE):
                continue

            if nxt in obstacles:
                continue

            new_mask = mask

            if nxt in star_index:
                new_mask |= 1 << star_index[nxt]

            state = (nxt, new_mask)

            if state not in visited:
                visited.add(state)
                queue.append((nxt, new_mask, steps + 1))

    return 999


# 랜덤 맵 생성
def make_map():
    level = st.session_state.level
    star_count, battery_count, obstacle_count = get_settings(level)

    while True:
        obstacles = set()

        possible = [
            (r, c)
            for r in range(SIZE)
            for c in range(SIZE)
            if (r, c) not in [START, GOAL]
        ]

        obstacles = set(
            random.sample(
                possible,
                min(obstacle_count, len(possible) - star_count - 2)
            )
        )

        available = list(set(possible) - obstacles)

        stars = set(random.sample(available, star_count))

        route = shortest_route(obstacles, stars)

        if route <= battery_count:
            break

    st.session_state.obstacles = obstacles
    st.session_state.stars = stars
    st.session_state.player = START
    st.session_state.battery = battery_count


if "obstacles" not in st.session_state:
    make_map()


# 이동 기능
def move(dr, dc):
    if st.session_state.game_over:
        return

    r, c = st.session_state.player
    nr, nc = r + dr, c + dc
    pos = (nr, nc)

    # 맵 밖으로 이동 방지
    if not (0 <= nr < SIZE and 0 <= nc < SIZE):
        return

    # 장애물 충돌
    if pos in st.session_state.obstacles:
        st.session_state.lives -= 1
        st.session_state.message = "🧱 장애물에 막혔어요!"

        if st.session_state.lives <= 0:
            st.session_state.game_over = True
            st.session_state.message = "💥 게임 오버!"

        return

    # 배터리 감소
    st.session_state.battery -= 1
    st.session_state.player = pos

    # 별 획득
    if pos in st.session_state.stars:
        st.session_state.stars.remove(pos)
        st.session_state.score += 100
        st.session_state.message = "⭐ 별 획득! +100점"

    # 목적지 도착
    if pos == GOAL:
        if len(st.session_state.stars) == 0:
            st.session_state.score += 300
            st.session_state.level += 1

            st.session_state.message = (
                f"🎉 스테이지 클리어! "
                f"현재 {st.session_state.level}단계!"
            )

            make_map()
            return

        else:
            st.session_state.message = "⭐ 별을 모두 모아야 도착할 수 있어요!"

    # 배터리 소진
    if st.session_state.battery <= 0:
        if len(st.session_state.stars) > 0 or pos != GOAL:
            st.session_state.game_over = True
            st.session_state.message = "🔋 배터리가 모두 소진됐어요!"


# 게임 정보
star_count, battery_count, obstacle_count = get_settings(
    st.session_state.level
)

a, b = st.columns(2)

a.metric("🏆 점수", st.session_state.score)
b.metric("🎮 스테이지", st.session_state.level)

a, b = st.columns(2)

a.metric(
    "🔋 남은 배터리",
    st.session_state.battery
)

b.metric(
    "⭐ 남은 별",
    f"{len(st.session_state.stars)}개"
)

st.write("❤️ 목숨:", "❤️ " * st.session_state.lives)

st.divider()

# 게임 맵
st.subheader("🗺️ GAME MAP")

st.write(
    "🤖 로봇 | ⭐ 별 | 🧱 장애물 | 🏁 목적지"
)

for r in range(SIZE):
    cols = st.columns(SIZE)

    for c in range(SIZE):
        pos = (r, c)

        if pos == st.session_state.player:
            icon = "🤖"

        elif pos in st.session_state.stars:
            icon = "⭐"

        elif pos == GOAL:
            icon = "🏁"

        elif pos in st.session_state.obstacles:
            icon = "🧱"

        else:
            icon = "⬜"

        cols[c].markdown(
            f"<div style='text-align:center;"
            f"font-size:27px;padding:7px;"
            f"background:rgba(128,128,128,0.12);"
            f"border-radius:9px;'>{icon}</div>",
            unsafe_allow_html=True
        )

st.divider()

# 조작 버튼
st.subheader("🎮 ROBOT CONTROL")

disabled = st.session_state.game_over

_, up, _ = st.columns(3)

if up.button("⬆️", use_container_width=True, disabled=disabled):
    move(-1, 0)
    st.rerun()

left, down, right = st.columns(3)

if left.button("⬅️", use_container_width=True, disabled=disabled):
    move(0, -1)
    st.rerun()

if down.button("⬇️", use_container_width=True, disabled=disabled):
    move(1, 0)
    st.rerun()

if right.button("➡️", use_container_width=True, disabled=disabled):
    move(0, 1)
    st.rerun()

if st.session_state.message:
    st.info(st.session_state.message)

# 게임 종료
if st.session_state.game_over:
    st.error("💥 GAME OVER!")

    if st.button("🔄 다시 시작"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()

# 전기전자 관련 설명
with st.expander("⚡ 전기전자와 관련된 원리"):
    st.write("""
    이 게임은 배터리에 저장된 에너지를 사용한다는 개념을 활용했습니다.

    배터리의 에너지가 한정되어 있기 때문에
    이동할 때마다 에너지를 소비하도록 만들었습니다.

    실제 배터리도 전기 에너지를 저장하고
    전자기기에 전력을 공급하는 역할을 합니다.
    """)
