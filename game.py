import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌 깨기",
    page_icon="🧱",
    layout="centered"
)

html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    background: #0f172a;
    font-family: Arial, sans-serif;
    color: white;
    overflow: hidden;
}

.game-wrapper {
    width: 100%;
    max-width: 720px;
    margin: auto;
    text-align: center;
}

.title {
    font-size: 28px;
    font-weight: bold;
    margin: 10px 0;
}

.info {
    display: flex;
    justify-content: space-around;
    align-items: center;
    background: #1e293b;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 10px;
    font-size: 16px;
}

#gameCanvas {
    width: 100%;
    max-width: 700px;
    aspect-ratio: 7 / 6;
    background: #020617;
    border: 3px solid #475569;
    border-radius: 12px;
    display: block;
    margin: auto;
    touch-action: none;
}

.controls {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 15px;
}

.control-btn {
    width: 120px;
    height: 55px;
    border: none;
    border-radius: 15px;
    background: #2563eb;
    color: white;
    font-size: 24px;
    font-weight: bold;
    touch-action: manipulation;
}

.control-btn:active {
    transform: scale(0.95);
    background: #1d4ed8;
}

.restart {
    margin-top: 12px;
    width: 260px;
    height: 48px;
    border: none;
    border-radius: 12px;
    background: #16a34a;
    color: white;
    font-size: 18px;
    font-weight: bold;
    touch-action: manipulation;
}

.restart:active {
    transform: scale(0.97);
}

.message {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    pointer-events: none;
}

.canvas-container {
    position: relative;
}

.small {
    font-size: 13px;
    color: #cbd5e1;
    margin-top: 10px;
}
</style>
</head>

<body>

<div class="game-wrapper">

    <div class="title">🧱 벽돌 깨기</div>

    <div class="info">
        <div>🏆 점수: <span id="score">0</span></div>
        <div>❤️ 목숨: <span id="lives">3</span></div>
        <div>🧱 벽돌: <span id="bricks">40</span></div>
    </div>

    <div class="canvas-container">

        <canvas id="gameCanvas" width="700" height="600"></canvas>

        <div id="message" class="message"></div>

    </div>

    <div class="controls">

        <button
            class="control-btn"
            id="leftBtn">
            ◀
        </button>

        <button
            class="control-btn"
            id="rightBtn">
            ▶
        </button>

    </div>

    <button
        class="restart"
        id="restartBtn">
        🔄 다시 시작
    </button>

    <div class="small">
        PC: ← → 키로 이동 / 모바일: 버튼 또는 터치로 이동
    </div>

</div>

<script>

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const scoreText = document.getElementById("score");
const livesText = document.getElementById("lives");
const bricksText = document.getElementById("bricks");
const message = document.getElementById("message");

const leftBtn = document.getElementById("leftBtn");
const rightBtn = document.getElementById("rightBtn");
const restartBtn = document.getElementById("restartBtn");


/* =========================
   게임 변수
========================= */

let score = 0;
let lives = 3;

let gameRunning = true;
let gameOver = false;
let gameWon = false;

let leftPressed = false;
let rightPressed = false;

let animationId;


/* 공 */

let ball = {
    x: 350,
    y: 500,
    radius: 9,
    dx: 4,
    dy: -4
};


/* 패들 */

let paddle = {
    width: 120,
    height: 16,
    x: 290,
    y: 550,
    speed: 8
};


/* 벽돌 */

let bricks = [];

const rows = 5;
const cols = 8;

const brickWidth = 75;
const brickHeight = 25;

const brickGap = 10;

const brickStartX = 25;
const brickStartY = 60;


/* =========================
   벽돌 생성
========================= */

function createBricks() {

    bricks = [];

    for (let row = 0; row < rows; row++) {

        for (let col = 0; col < cols; col++) {

            bricks.push({
                x: brickStartX + col * (brickWidth + brickGap),
                y: brickStartY + row * (brickHeight + brickGap),
                width: brickWidth,
                height: brickHeight,
                alive: true
            });

        }

    }

}


/* =========================
   게임 초기화
========================= */

function resetGame() {

    cancelAnimationFrame(animationId);

    score = 0;
    lives = 3;

    gameRunning = true;
    gameOver = false;
    gameWon = false;

    leftPressed = false;
    rightPressed = false;

    paddle.x = 290;

    ball.x = 350;
    ball.y = 500;

    ball.dx = Math.random() > 0.5 ? 4 : -4;
    ball.dy = -4;

    createBricks();

    message.innerHTML = "";

    updateInfo();

    gameLoop();

}


/* =========================
   정보 업데이트
========================= */

function updateInfo() {

    scoreText.textContent = score;
    livesText.textContent = lives;

    const remaining = bricks.filter(
        brick => brick.alive
    ).length;

    bricksText.textContent = remaining;

}


/* =========================
   공 그리기
========================= */

function drawBall() {

    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        ball.radius,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = "#facc15";

    ctx.shadowBlur = 15;
    ctx.shadowColor = "#facc15";

    ctx.fill();

    ctx.shadowBlur = 0;

    ctx.closePath();

}


/* =========================
   패들 그리기
========================= */

function drawPaddle() {

    ctx.fillStyle = "#3b82f6";

    ctx.beginPath();

    ctx.roundRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height,
        8
    );

    ctx.fill();

}


/* =========================
   벽돌 그리기
========================= */

function drawBricks() {

    bricks.forEach((brick, index) => {

        if (!brick.alive) {
            return;
        }

        const colors = [
            "#ef4444",
            "#f97316",
            "#eab308",
            "#22c55e",
            "#3b82f6"
        ];

        ctx.fillStyle = colors[index % colors.length];

        ctx.beginPath();

        ctx.roundRect(
            brick.x,
            brick.y,
            brick.width,
            brick.height,
            5
        );

        ctx.fill();

        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1;
        ctx.stroke();

    });

}


/* =========================
   배경
========================= */

function drawBackground() {

    ctx.fillStyle = "#020617";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

}


/* =========================
   패들 이동
========================= */

function movePaddle() {

    if (leftPressed) {

        paddle.x -= paddle.speed;

    }

    if (rightPressed) {

        paddle.x += paddle.speed;

    }

    if (paddle.x < 0) {

        paddle.x = 0;

    }

    if (
        paddle.x + paddle.width >
        canvas.width
    ) {

        paddle.x =
            canvas.width - paddle.width;

    }

}


/* =========================
   공 움직임
========================= */

function moveBall() {

    ball.x += ball.dx;
    ball.y += ball.dy;


    /* 왼쪽 벽 */

    if (
        ball.x - ball.radius <= 0
    ) {

        ball.x = ball.radius;
        ball.dx *= -1;

    }


    /* 오른쪽 벽 */

    if (
        ball.x + ball.radius >=
        canvas.width
    ) {

        ball.x =
            canvas.width - ball.radius;

        ball.dx *= -1;

    }


    /* 위쪽 벽 */

    if (
        ball.y - ball.radius <= 0
    ) {

        ball.y = ball.radius;
        ball.dy *= -1;

    }


    /* 패들 충돌 */

    if (
        ball.y + ball.radius >= paddle.y &&
        ball.y - ball.radius <=
            paddle.y + paddle.height &&
        ball.x >= paddle.x &&
        ball.x <=
            paddle.x + paddle.width &&
        ball.dy > 0
    ) {

        ball.y =
            paddle.y - ball.radius;

        ball.dy *= -1;


        /* 패들 위치에 따라 방향 변화 */

        const hitPosition =
            (
                ball.x -
                (paddle.x + paddle.width / 2)
            ) /
            (paddle.width / 2);

        ball.dx =
            hitPosition * 6;

    }


    /* 바닥 */

    if (
        ball.y - ball.radius >
        canvas.height
    ) {

        loseLife();

    }

}


/* =========================
   목숨 감소
========================= */

function loseLife() {

    lives--;

    updateInfo();

    if (lives <= 0) {

        gameOver = true;
        gameRunning = false;

        message.innerHTML =
            "💥 GAME OVER<br>" +
            "<span style='font-size:18px'>" +
            "다시 시작 버튼을 눌러주세요" +
            "</span>";

        return;

    }


    /* 공 리셋 */

    ball.x = canvas.width / 2;
    ball.y = 500;

    ball.dx =
        Math.random() > 0.5
        ? 4
        : -4;

    ball.dy = -4;

}


/* =========================
   벽돌 충돌
========================= */

function checkBrickCollision() {

    for (
        let i = 0;
        i < bricks.length;
        i++
    ) {

        const brick = bricks[i];

        if (!brick.alive) {
            continue;
        }


        if (
            ball.x + ball.radius >
                brick.x &&
            ball.x - ball.radius <
                brick.x + brick.width &&
            ball.y + ball.radius >
                brick.y &&
            ball.y - ball.radius <
                brick.y + brick.height
        ) {

            brick.alive = false;

            ball.dy *= -1;

            score += 10;

            updateInfo();

            break;

        }

    }


    /* 승리 */

    const remaining =
        bricks.filter(
            brick => brick.alive
        ).length;

    if (remaining === 0) {

        gameWon = true;
        gameRunning = false;

        message.innerHTML =
            "🎉 YOU WIN!<br>" +
            "<span style='font-size:18px'>" +
            "점수: " + score +
            "</span>";

    }

}


/* =========================
   게임 그리기
========================= */

function draw() {

    drawBackground();

    drawBricks();

    drawPaddle();

    drawBall();

}


/* =========================
   게임 루프
========================= */

function gameLoop() {

    draw();

    if (gameRunning) {

        movePaddle();

        moveBall();

        checkBrickCollision();

        animationId =
            requestAnimationFrame(
                gameLoop
            );

    }

}


/* =========================
   키보드
========================= */

document.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "ArrowLeft"
        ) {

            leftPressed = true;

            event.preventDefault();

        }

        if (
            event.key === "ArrowRight"
        ) {

            rightPressed = true;

            event.preventDefault();

        }

    }
);


document.addEventListener(
    "keyup",
    function(event) {

        if (
            event.key === "ArrowLeft"
        ) {

            leftPressed = false;

        }

        if (
            event.key === "ArrowRight"
        ) {

            rightPressed = false;

        }

    }
);


/* =========================
   버튼 조작
========================= */

function pressLeft() {
    leftPressed = true;
}

function releaseLeft() {
    leftPressed = false;
}

function pressRight() {
    rightPressed = true;
}

function releaseRight() {
    rightPressed = false;
}


/* 왼쪽 버튼 */

leftBtn.addEventListener(
    "mousedown",
    pressLeft
);

leftBtn.addEventListener(
    "mouseup",
    releaseLeft
);

leftBtn.addEventListener(
    "mouseleave",
    releaseLeft
);

leftBtn.addEventListener(
    "touchstart",
    function(e) {
        e.preventDefault();
        pressLeft();
    }
);

leftBtn.addEventListener(
    "touchend",
    function(e) {
        e.preventDefault();
        releaseLeft();
    }
);


/* 오른쪽 버튼 */

rightBtn.addEventListener(
    "mousedown",
    pressRight
);

rightBtn.addEventListener(
    "mouseup",
    releaseRight
);

rightBtn.addEventListener(
    "mouseleave",
    releaseRight
);

rightBtn.addEventListener(
    "touchstart",
    function(e) {
        e.preventDefault();
        pressRight();
    }
);

rightBtn.addEventListener(
    "touchend",
    function(e) {
        e.preventDefault();
        releaseRight();
    }
);


/* =========================
   캔버스 터치 이동
========================= */

canvas.addEventListener(
    "touchmove",
    function(e) {

        e.preventDefault();

        const rect =
            canvas.getBoundingClientRect();

        const touch =
            e.touches[0];

        const scaleX =
            canvas.width /
            rect.width;

        const touchX =
            (touch.clientX - rect.left)
            * scaleX;

        paddle.x =
            touchX -
            paddle.width / 2;


        if (paddle.x < 0) {

            paddle.x = 0;

        }

        if (
            paddle.x + paddle.width >
            canvas.width
        ) {

            paddle.x =
                canvas.width -
                paddle.width;

        }

    },
    {
        passive: false
    }
);


/* =========================
   다시 시작
========================= */

restartBtn.addEventListener(
    "click",
    function() {

        resetGame();

    }
);


/* =========================
   시작
========================= */

createBricks();
updateInfo();
gameLoop();

</script>

</body>
</html>
"""

components.html(
    html,
    height=850,
    scrolling=False
)
