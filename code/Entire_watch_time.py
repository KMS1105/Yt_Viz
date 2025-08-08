import sys
import json
import os
import time
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from PyQt5.QtWidgets import (
    QFileDialog, QApplication, QWidget, QLabel,
    QPushButton, QProgressBar, QMessageBox
)
from yt_dlp import YoutubeDL
import multiprocessing
import plotly.graph_objects as go
import webbrowser

COOKIE_FILE_PATH = "cookies.txt"
CHECKPOINT_FILE = "checkpoint.json"
CHECKPOINT_BACKUP_DIR = "checkpoints"

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

    def ask_resume_checkpoint(self, checkpoint, total_urls):
        processed = checkpoint.get("processed_count", 0)
        percent = checkpoint.get("progress_percent", 0)
        avg_speed = checkpoint.get("avg_speed", 0)

        remaining_videos = total_urls - processed
        est_remaining_seconds = remaining_videos / avg_speed if avg_speed > 0 else remaining_videos * 0.5

        h = int(est_remaining_seconds // 3600)
        m = int((est_remaining_seconds % 3600) // 60)
        s = int(est_remaining_seconds % 60)

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("중간 저장 불러오기")
        msg.setText(
            f"이전에 저장된 진행 데이터가 있습니다.\n"
            f"진행률: {percent}% ({processed}/{total_urls}개)\n"
            f"평균 처리 속도: {avg_speed:.2f}개/초\n"
            f"남은 예상 시간: 약 {h}시간 {m}분 {s}초\n"
            "이어할까요?"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg.exec_() == QMessageBox.Yes

    def save_checkpoint(self, short_sec, long_sec, processed_count, total_urls, avg_speed):
        percent = int(processed_count / total_urls * 100)
        checkpoint_data = {
            "total_short": short_sec,
            "total_long": long_sec,
            "processed_count": processed_count,
            "progress_percent": percent,
            "avg_speed": avg_speed
        }

        # 기본 체크포인트 저장
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

        # 백업 폴더 생성
        os.makedirs(CHECKPOINT_BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(CHECKPOINT_BACKUP_DIR, f"checkpoint_{timestamp}.json")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

        print(f"[DEBUG] 체크포인트 저장됨: {percent}% ({processed_count}/{total_urls}), 백업: {backup_path}")

    def load_checkpoint(self):
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def calc_total_time(self):
        if not self.json_path:
            self.lbl_result.setText("먼저 JSON 파일을 선택하세요.")
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            self.lbl_result.setText("JSON 파일을 열 수 없습니다.")
            return

        # 광고 제거
        filtered_entries = [
            e for e in data
            if not any(d.get("name", "") == "출처: Google 광고" for d in e.get("details", []))
        ]

        urls = []
        for entry in filtered_entries:
            url_raw = entry.get("titleUrl", "")
            url = url_raw.replace("\\u003d", "=").replace("\u003d", "=").strip()
            if url.startswith("https://www.youtube.com/watch?v=") or url.startswith("https://youtu.be/"):
                urls.append(url)

        urls = list(set(urls))
        total_urls = len(urls)

        if not urls:
            self.lbl_result.setText("유효한 유튜브 영상 URL이 없습니다.")
            return

        total_short, total_long, processed_count = 0, 0, 0
        start_time = time.time()

        checkpoint = self.load_checkpoint()
        if checkpoint and self.ask_resume_checkpoint(checkpoint, total_urls):
            total_short = checkpoint.get("total_short", 0)
            total_long = checkpoint.get("total_long", 0)
            processed_count = checkpoint.get("processed_count", 0)
            urls = urls[processed_count:]

        self.progress.setValue(0)
        self.progress.show()

        max_workers = multiprocessing.cpu_count() * 2
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_video_length, url): url for url in urls}

            for i, future in enumerate(as_completed(futures), 1):
                try:
                    length = future.result()
                except Exception:
                    length = 0

                if 0 < length < 180:
                    total_short += length
                elif length >= 180:
                    total_long += length

                processed_count += 1
                progress_pct = int(processed_count / total_urls * 100)
                elapsed = time.time() - start_time
                avg_speed = processed_count / elapsed if elapsed > 0 else 0

                self.progress.setValue(progress_pct)
                self.lbl_result.setText(
                    f"[{processed_count}/{total_urls}] {progress_pct}% 진행 중...\n"
                    f"현재 누적 - 3분 미만: {total_short}초, 3분 이상: {total_long}초\n"
                    f"평균 처리 속도: {avg_speed:.2f}개/초"
                )
                QApplication.processEvents()

                if processed_count % 1000 == 0:
                    self.save_checkpoint(total_short, total_long, processed_count, total_urls, avg_speed)

        self.save_checkpoint(total_short, total_long, processed_count, total_urls, processed_count / (time.time() - start_time))

        def sec_to_hms(s):
            h, s = divmod(s, 3600)
            m, s = divmod(s, 60)
            return h, m, s

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

        extra_html = f"""
        <div style="text-align:center; font-size:16px; margin-top:20px;">
            <p>숏폼(3분 미만) 영상 누적 시청시간: {short_h}시간 {short_m}분 {short_s}초</p>
            <p>롱폼(3분 이상) 영상 누적 시청시간: {long_h}시간 {long_m}분 {long_s}초</p>
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
