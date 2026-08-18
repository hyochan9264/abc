import streamlit as st
import time
import random

st.set_page_config(
    page_title="벽돌 깨기",
    page_icon="🧱",
    layout="centered"
)

# -----------------------------
# 게임 초기화
# -----------------------------
def init_game():
    st.session_state.ball_x = 0.5
    st.session_state.ball_y = 0.75

    st.session_state.ball_dx = random.choice([-0.012, 0.012])
    st.session_state.ball_dy = -0.012

    st.session_state.paddle_x = 0.5
    st.session_state.paddle_width = 0.18

    st.session_state.score = 0
    st.session_state.lives = 3
    st.session_state.level = 1

    st.session_state.bricks = create_bricks()
    st.session_state.game_over = False
    st.session_state.win = False
    st.session_state.running = True


def create_bricks():
    bricks = []

    rows = 5
    cols = 8

    brick_width = 0.105
    brick_height = 0.035

    gap_x = 0.015
    gap_y = 0.015

    start_x = 0.04
    start_y = 0.10

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (brick_width + gap_x)
            y = start_y + row * (brick_height + gap_y)

            bricks.append({
                "x": x,
                "y": y,
                "w": brick_width,
                "h": brick_height,
                "alive": True
            })

    return bricks


# -----------------------------
# 최초 실행
# -----------------------------
if "ball_x" not in st.session_state:
    init_game()


# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.title("🎮 게임 조작")

st.sidebar.write("### 패들 이동")

left = st.sidebar.button("⬅️ 왼쪽")
right = st.sidebar.button("오른쪽 ➡️")

if left:
    st.session_state.paddle_x -= 0.06

if right:
    st.session_state.paddle_x += 0.06

st.session_state.paddle_x = max(
    st.session_state.paddle_width / 2,
    min(
        1 - st.session_state.paddle_width / 2,
        st.session_state.paddle_x
    )
)

if st.sidebar.button("🔄 게임 재시작"):
    init_game()
    st.rerun()


# -----------------------------
# 게임 상태 업데이트
# -----------------------------
def update_game():

    if st.session_state.game_over or st.session_state.win:
        return

    # 공 이동
    st.session_state.ball_x += st.session_state.ball_dx
    st.session_state.ball_y += st.session_state.ball_dy

    bx = st.session_state.ball_x
    by = st.session_state.ball_y

    # 벽 충돌
    if bx <= 0:
        st.session_state.ball_x = 0
        st.session_state.ball_dx *= -1

    if bx >= 1:
        st.session_state.ball_x = 1
        st.session_state.ball_dx *= -1

    if by <= 0:
        st.session_state.ball_y = 0
        st.session_state.ball_dy *= -1

    # 패들 충돌
    paddle_left = (
        st.session_state.paddle_x
        - st.session_state.paddle_width / 2
    )

    paddle_right = (
        st.session_state.paddle_x
        + st.session_state.paddle_width / 2
    )

    paddle_y = 0.90
    paddle_height = 0.025

    if (
        by >= paddle_y - paddle_height
        and by <= paddle_y + paddle_height
        and paddle_left <= bx <= paddle_right
        and st.session_state.ball_dy > 0
    ):
        st.session_state.ball_dy *= -1

        # 패들의 맞은 위치에 따라 공의 방향 변경
        relative = (
            bx - st.session_state.paddle_x
        ) / (st.session_state.paddle_width / 2)

        st.session_state.ball_dx = relative * 0.018

    # 벽돌 충돌
    for brick in st.session_state.bricks:

        if not brick["alive"]:
            continue

        if (
            brick["x"] <= bx <= brick["x"] + brick["w"]
            and
            brick["y"] <= by <= brick["y"] + brick["h"]
        ):

            brick["alive"] = False

            st.session_state.ball_dy *= -1

            st.session_state.score += 10

            break

    # 모든 벽돌 제거
    if not any(
        brick["alive"]
        for brick in st.session_state.bricks
    ):
        st.session_state.win = True
        st.session_state.running = False

    # 공이 바닥으로 떨어짐
    if by > 1:

        st.session_state.lives -= 1

        if st.session_state.lives <= 0:

            st.session_state.game_over = True
            st.session_state.running = False

        else:

            st.session_state.ball_x = 0.5
            st.session_state.ball_y = 0.75

            st.session_state.ball_dx = random.choice(
                [-0.012, 0.012]
            )

            st.session_state.ball_dy = -0.012


# -----------------------------
# HTML 게임판
# -----------------------------
def create_board():

    html = """
    <div style="
        position:relative;
        width:100%;
        max-width:700px;
        height:600px;
        margin:auto;
        background:#111827;
        border:4px solid #374151;
        border-radius:12px;
        overflow:hidden;
    ">
    """

    # 벽돌
    for brick in st.session_state.bricks:

        if not brick["alive"]:
            continue

        left = brick["x"] * 100
        top = brick["y"] * 100

        width = brick["w"] * 100
        height = brick["h"] * 100

        html += f"""
        <div style="
            position:absolute;
            left:{left}%;
            top:{top}%;
            width:{width}%;
            height:{height}%;
            background:#ef4444;
            border:2px solid #fca5a5;
            border-radius:4px;
            box-sizing:border-box;
        "></div>
        """

    # 공
    ball_left = st.session_state.ball_x * 100
    ball_top = st.session_state.ball_y * 100

    html += f"""
    <div style="
        position:absolute;
        left:{ball_left}%;
        top:{ball_top}%;
        width:18px;
        height:18px;
        transform:translate(-50%,-50%);
        background:#facc15;
        border-radius:50%;
        box-shadow:0 0 10px #facc15;
    "></div>
    """

    # 패들
    paddle_left = (
        st.session_state.paddle_x
        - st.session_state.paddle_width / 2
    ) * 100

    paddle_width = st.session_state.paddle_width * 100

    html += f"""
    <div style="
        position:absolute;
        left:{paddle_left}%;
        bottom:7%;
        width:{paddle_width}%;
        height:20px;
        background:#3b82f6;
        border-radius:10px;
        box-shadow:0 0 8px #3b82f6;
    "></div>
    """

    html += "</div>"

    return html


# -----------------------------
# 게임 업데이트
# -----------------------------
update_game()


# -----------------------------
# 화면
# -----------------------------
st.title("🧱 벽돌 깨기 게임")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🏆 점수", st.session_state.score)

with col2:
    st.metric("❤️ 목숨", st.session_state.lives)

with col3:
    remaining = sum(
        brick["alive"]
        for brick in st.session_state.bricks
    )

    st.metric("🧱 남은 벽돌", remaining)


if st.session_state.win:

    st.success("🎉 축하합니다! 모든 벽돌을 깼습니다!")

elif st.session_state.game_over:

    st.error("💥 게임 오버!")

else:

    st.components.v1.html(
        create_board(),
        height=610
    )


# -----------------------------
# 게임 설명
# -----------------------------
st.markdown("---")

st.markdown(
    """
### 🎮 게임 방법

- **⬅️ 왼쪽 / 오른쪽 ➡️ 버튼**으로 패들을 움직입니다.
- 공이 패들에 맞으면 다시 튕겨 올라갑니다.
- 공으로 🧱 벽돌을 모두 깨면 승리합니다.
- 벽돌 하나를 깨면 **10점**을 얻습니다.
- 공을 놓치면 목숨이 하나 감소합니다.
- 목숨은 총 **3개**입니다.

💡 **팁:** 패들의 중앙이 아니라 양쪽 끝으로 공을 맞히면 공의 방향을 크게 바꿀 수 있습니다.
"""
)

# -----------------------------
# 자동 새로고침
# -----------------------------
if st.session_state.running:
    time.sleep(0.05)
    st.rerun()
