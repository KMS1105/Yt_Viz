import sys
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from PyQt5.QtWidgets import (
    QFileDialog, QApplication, QWidget, QLabel,
    QPushButton, QProgressBar
)
from yt_dlp import YoutubeDL
import multiprocessing
import plotly.graph_objects as go
import webbrowser

COOKIE_FILE_PATH = "cookies.txt"  # 쿠키 필요 시 경로 지정

def fetch_video_length(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'skip_download': True,
        'cookiefile': COOKIE_FILE_PATH,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get('duration', 0)
            return duration or 0
    except Exception as e:
        print(f"[ERROR] 영상 길이 조회 실패: {url} | 에러: {e}")
        return 0

class YoutubeWatchTimeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.json_path = ''
        self.initUI()

    def initUI(self):
        self.btn_browse = QPushButton("JSON 파일 선택", self)
        self.btn_browse.move(20, 20)
        self.btn_browse.clicked.connect(self.browse_file)

        self.btn_calc = QPushButton("총 시청시간 계산", self)
        self.btn_calc.move(150, 20)
        self.btn_calc.clicked.connect(self.calc_total_time)

        self.lbl_result = QLabel('', self)
        self.lbl_result.move(20, 70)
        self.lbl_result.resize(600, 80)
        self.lbl_result.setWordWrap(True)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(20, 160, 600, 20)
        self.progress.setValue(0)
        self.progress.hide()

        self.setWindowTitle('전체 누적 시청시간')
        self.setGeometry(300, 300, 650, 220)
        self.show()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "JSON 파일 선택", "", "JSON Files (*.json)")
        if file_path:
            self.json_path = file_path
            self.lbl_result.setText(f"선택된 파일: {file_path.split('/')[-1]}")
            print(f"[DEBUG] JSON 파일 선택됨: {file_path}")

    def calc_total_time(self):
        if not self.json_path:
            self.lbl_result.setText("먼저 JSON 파일을 선택하세요.")
            print("[DEBUG] JSON 파일 미선택 상태에서 계산 시도")
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[DEBUG] JSON 파일 로드 성공: 총 {len(data)}개 항목")
        except Exception as e:
            self.lbl_result.setText("JSON 파일을 열 수 없습니다.")
            print(f"[DEBUG] JSON 파일 로드 실패: {e}")
            return

        filtered_entries = []
        for entry in data:
            details = entry.get("details", [])
            if any(d.get("name", "") == "출처: Google 광고" for d in details):
                continue
            filtered_entries.append(entry)

        urls = []
        for entry in filtered_entries:
            url_raw = entry.get("titleUrl", "")
            url = url_raw.replace("\\u003d", "=").replace("\u003d", "=").strip()
            if url.startswith("https://www.youtube.com/watch?v=") or url.startswith("https://youtu.be/"):
                urls.append(url)

        if not urls:
            self.lbl_result.setText("유효한 유튜브 영상 URL이 없습니다.")
            print("[DEBUG] 유효 URL 없음")
            return

        urls = list(set(urls))  # 중복 제거

        self.progress.setValue(0)
        self.progress.show()

        total_short = 0  # 3분 미만
        total_long = 0   # 3분 이상
        total_urls = len(urls)

        max_workers = multiprocessing.cpu_count() * 3
        print(f"[DEBUG] CPU 코어 수: {multiprocessing.cpu_count()}, max_workers: {max_workers}")

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_video_length, url): url for url in urls}

            for i, future in enumerate(as_completed(futures), 1):
                url = futures[future]
                try:
                    length = future.result()
                except Exception:
                    length = 0

                if 0 < length < 180:
                    total_short += length
                elif length >= 180:
                    total_long += length

                progress_pct = int(i / total_urls * 100)
                self.progress.setValue(progress_pct)
                self.lbl_result.setText(
                    f"[{i}/{total_urls}] {progress_pct}% 진행 중... 최근 영상 길이: {length}초\n"
                    f"현재 누적 - 3분 미만: {total_short}초, 3분 이상: {total_long}초"
                )
                print(f"[{i}/{total_urls}] {progress_pct}% URL: {url} 길이: {length}초 | "
                      f"누적(미만): {total_short}초, 누적(이상): {total_long}초")

                QApplication.processEvents()

        def sec_to_hms(s):
            h = s // 3600
            m = (s % 3600) // 60
            sec = s % 60
            return h, m, sec

        short_h, short_m, short_s = sec_to_hms(total_short)
        long_h, long_m, long_s = sec_to_hms(total_long)
        total_h, total_m, total_s = sec_to_hms(total_short + total_long)

        final_msg = (
            f"3분 미만 영상 누적 시청시간: {short_h}시간 {short_m}분 {short_s}초\n"
            f"3분 이상 영상 누적 시청시간: {long_h}시간 {long_m}분 {long_s}초\n"
            f"전체 누적 시청시간: {total_h}시간 {total_m}분 {total_s}초"
        )
        self.lbl_result.setText(final_msg)
        self.progress.hide()
        print(f"[DEBUG] 계산 완료:\n{final_msg}")

        # 도넛 차트 생성
        labels = ['3분 미만', '3분 이상']
        values = [total_short, total_long]
        colors = ['#FFA07A', '#20B2AA']

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker_colors=colors,
            hoverinfo="label+percent+value",
            textinfo='label+percent'
        )])

        fig.update_layout(
            title_text="숏폼(3분 미만) vs 롱폼(3분 이상) 누적 시청시간 비율",
            annotations=[dict(text='시간 비율', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )

        # 차트 밑에 누적시간 텍스트 넣기 위한 html 코드 추가
        extra_html = f"""
        <div style="text-align:center; font-size:16px; margin-top:20px;">
            <p>3분 미만 영상 누적 시청시간: {short_h}시간 {short_m}분 {short_s}초</p>
            <p>3분 이상 영상 누적 시청시간: {long_h}시간 {long_m}분 {long_s}초</p>
            <p>전체 누적 시청시간: {total_h}시간 {total_m}분 {total_s}초</p>
        </div>
        """

        html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')
        html_str = f"<html><body>{html_str}{extra_html}</body></html>"

        with open("output_chart.html", "w", encoding="utf-8") as f:
            f.write(html_str)

        webbrowser.open("output_chart.html")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YoutubeWatchTimeApp()
    sys.exit(app.exec_())
