import tkinter as tk
import random
import time

# --- 게임 상수 설정 ---
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 700
ROAD_SPEED = 5
ROAD_SEGMENT_HEIGHT = 10  # 도로 조각의 높이

CAR_WIDTH = 40
CAR_HEIGHT = 60
CAR_SPEED = 20

class RacingGame:
    def __init__(self, master):
        self.master = master
        self.master.title("간단 레이싱 게임")
        self.master.resizable(False, False)

        # 캔버스 생성 (게임이 그려질 공간)
        self.canvas = tk.Canvas(self.master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="gray")
        self.canvas.pack()

        # 게임 상태 변수
        self.is_game_running = False
        self.start_time = 0
        self.road_segments = []

        # 시작 버튼 표시
        self.start_button = tk.Button(self.master, text="게임 시작", font=("Helvetica", 20), command=self.start_game)
        self.start_button_window = self.canvas.create_window(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, window=self.start_button)

        self.score_text_id = None


    def start_game(self):
        """게임 시작 처리"""
        # 시작 버튼 숨기기
        self.start_button.destroy()
        self.canvas.delete(self.start_button_window)

        # 게임 상태 초기화
        self.is_game_running = True
        self.road_segments = []
        self.canvas.delete("all") # 이전 게임 오버 화면 등 모두 지우기

        # 도로 초기화
        self.road_center = WINDOW_WIDTH / 2
        self.road_width = WINDOW_WIDTH / 3
        # 화면을 채울 초기 도로 생성
        for y_pos in range(WINDOW_HEIGHT, -ROAD_SEGMENT_HEIGHT, -ROAD_SEGMENT_HEIGHT):
            self.create_road_segment(y_pos)

        # 자동차 생성
        car_y_pos = WINDOW_HEIGHT - 100
        self.car = self.canvas.create_rectangle(
            WINDOW_WIDTH / 2 - CAR_WIDTH / 2, car_y_pos - CAR_HEIGHT / 2,
            WINDOW_WIDTH / 2 + CAR_WIDTH / 2, car_y_pos + CAR_HEIGHT / 2,
            fill="blue", outline="white"
        )

        # 점수판 생성
        self.score_text_id = self.canvas.create_text(
            50, 20, text="점수: 0", font=("Helvetica", 16), fill="white", anchor="w"
        )

        # 키보드 이벤트 바인딩
        self.master.bind("<Left>", self.move_left)
        self.master.bind("<Right>", self.move_right)

        # 게임 시작 시간 기록 및 게임 루프 시작
        self.start_time = time.time()
        self.game_loop()

    def create_road_segment(self, y_pos):
        """새로운 도로 조각을 생성"""
        # 도로의 중심과 폭을 약간씩 변경하여 구불구불한 길 생성
        self.road_center += random.randint(-8, 8)
        self.road_width += random.randint(-5, 5)

        # 도로의 최소/최대 폭 및 중심 위치 제한
        self.road_width = max(WINDOW_WIDTH / 5, min(self.road_width, WINDOW_WIDTH * 0.9))
        self.road_center = max(self.road_width / 2, min(self.road_center, WINDOW_WIDTH - self.road_width / 2))

        left_edge = self.road_center - self.road_width / 2
        right_edge = self.road_center + self.road_width / 2

        # 도로 조각(검은색 사각형)을 그리고 리스트에 추가
        segment = self.canvas.create_rectangle(
            left_edge, y_pos, right_edge, y_pos + ROAD_SEGMENT_HEIGHT,
            fill="black", outline=""
        )
        self.road_segments.append((segment, left_edge, right_edge))

    def move_road(self):
        """도로를 아래로 스크롤"""
        for segment_data in self.road_segments:
            self.canvas.move(segment_data[0], 0, ROAD_SPEED)

        # 화면 아래로 사라진 도로 조각 제거
        if self.road_segments:
            first_segment_coords = self.canvas.coords(self.road_segments[0][0])
            if first_segment_coords[1] > WINDOW_HEIGHT:
                self.canvas.delete(self.road_segments[0][0])
                self.road_segments.pop(0)

        # 화면 위쪽에 새로운 도로 조각 생성
        last_segment_coords = self.canvas.coords(self.road_segments[-1][0])
        if last_segment_coords[1] > 0:
            self.create_road_segment(-ROAD_SEGMENT_HEIGHT)

    def move_left(self, event):
        """자동차를 왼쪽으로 이동"""
        car_coords = self.canvas.coords(self.car)
        if car_coords[0] > 0: # 창 왼쪽 경계를 넘지 않도록
            self.canvas.move(self.car, -CAR_SPEED, 0)

    def move_right(self, event):
        """자동차를 오른쪽으로 이동"""
        car_coords = self.canvas.coords(self.car)
        if car_coords[2] < WINDOW_WIDTH: # 창 오른쪽 경계를 넘지 않도록
            self.canvas.move(self.car, CAR_SPEED, 0)

    def check_collision(self):
        """충돌 감지"""
        car_coords = self.canvas.coords(self.car)
        car_left, car_top, car_right, car_bottom = car_coords

        # 자동차의 Y 좌표와 겹치는 도로 조각들을 찾음
        for segment, left_edge, right_edge in self.road_segments:
            seg_coords = self.canvas.coords(segment)
            if seg_coords[3] > car_top and seg_coords[1] < car_bottom:
                # 자동차가 도로 경계를 벗어났는지 확인
                if car_left < seg_coords[0] or car_right > seg_coords[2]:
                    self.game_over()
                break # 자동차 위치의 도로 조각은 하나뿐이므로 더 검사할 필요 없음

    def update_score(self):
        """점수 업데이트"""
        elapsed_time = time.time() - self.start_time
        score = int(elapsed_time)
        self.canvas.itemconfig(self.score_text_id, text=f"점수: {score}")
        return score

    def game_loop(self):
        """메인 게임 루프"""
        if not self.is_game_running:
            return

        self.move_road()
        self.check_collision()
        self.update_score()

        # 16ms 마다 (약 60 FPS) 게임 루프를 다시 호출
        self.master.after(16, self.game_loop)

    def game_over(self):
        """게임 오버 처리"""
        self.is_game_running = False
        final_score = self.update_score()

        # 키보드 이벤트 바인딩 해제
        self.master.unbind("<Left>")
        self.master.unbind("<Right>")

        # 게임 오버 메시지 표시
        self.canvas.create_text(
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50,
            text="게임 오버!", font=("Helvetica", 40, "bold"), fill="red"
        )
        self.canvas.create_text(
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
            text=f"최종 점수: {final_score}", font=("Helvetica", 20), fill="white"
        )

        # 다시 시작 버튼
        self.restart_button = tk.Button(self.master, text="다시 시작", font=("Helvetica", 20), command=self.start_game)
        self.restart_button_window = self.canvas.create_window(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 60, window=self.restart_button)


if __name__ == "__main__":
    root = tk.Tk()
    game = RacingGame(root)
    root.mainloop()
