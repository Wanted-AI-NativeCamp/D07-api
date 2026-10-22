import random
import tkinter as tk
from datetime import datetime

# 동행복권 공 색상 기준
def ball_color(n):
    if n <= 10:
        return "#FBC400"  # 노랑
    if n <= 20:
        return "#69C8F2"  # 파랑
    if n <= 30:
        return "#FF7272"  # 빨강
    if n <= 40:
        return "#AAAAAA"  # 회색
    return "#B0D840"      # 초록


def make_set():
    return sorted(random.sample(range(1, 46), 6))


BALL = 44
GAP = 8
SETS = 5


def draw():
    canvas.delete("all")
    now = datetime.now()
    date_label.config(text=now.strftime("%Y년 %m월 %d일 %H:%M:%S"))

    for row in range(SETS):
        y = 20 + row * (BALL + 16)
        canvas.create_text(20, y + BALL / 2, text=chr(ord("A") + row),
                           font=("맑은 고딕", 14, "bold"), fill="#333")
        for col, n in enumerate(make_set()):
            x = 50 + col * (BALL + GAP)
            canvas.create_oval(x, y, x + BALL, y + BALL,
                               fill=ball_color(n), outline="")
            canvas.create_text(x + BALL / 2, y + BALL / 2, text=str(n),
                               font=("맑은 고딕", 14, "bold"), fill="white")


root = tk.Tk()
root.title("로또 번호 생성기")
root.configure(bg="white")
root.resizable(False, False)

tk.Label(root, text="로또 6/45 번호 생성기", font=("맑은 고딕", 18, "bold"),
         bg="white").pack(pady=(16, 4))
date_label = tk.Label(root, text="버튼을 눌러 번호를 생성하세요",
                      font=("맑은 고딕", 11), fg="#666", bg="white")
date_label.pack()

canvas = tk.Canvas(root, width=50 + 6 * (BALL + GAP) + 10,
                   height=20 + SETS * (BALL + 16), bg="white",
                   highlightthickness=0)
canvas.pack(padx=16, pady=8)

tk.Button(root, text="번호 생성", font=("맑은 고딕", 13, "bold"),
          bg="#2D6CDF", fg="white", activebackground="#1F55B8",
          activeforeground="white", relief="flat", padx=24, pady=8,
          command=draw).pack(pady=(4, 18))

root.mainloop()
