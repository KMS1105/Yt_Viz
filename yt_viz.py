import sys
import json
import re
from PyQt5.QtWidgets import (
    QFileDialog, QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QProgressBar
)
from collections import Counter
import pandas as pd
import plotly.express as px
import webbrowser

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.json_path = ''
        self.initUI()

    def initUI(self):
        self.lbl_min_views = QLabel('최소 재생 횟수:', self)
        self.lbl_min_views.move(20, 20)
        self.qle_min_views = QLineEdit(self)
        self.qle_min_views.move(120, 15)
        self.qle_min_views.resize(100, 25)

        self.lbl_max_videos = QLabel('최대 영상 갯수:', self)
        self.lbl_max_videos.move(20, 55)
        self.qle_max_videos = QLineEdit(self)
        self.qle_max_videos.move(120, 50)
        self.qle_max_videos.resize(100, 25)

        self.btn_browse = QPushButton("파일 선택", self)
        self.btn_browse.move(240, 15)
        self.btn_browse.clicked.connect(self.browse_file)

        self.btn = QPushButton("그래프 보기", self)
        self.btn.move(240, 50)
        self.btn.clicked.connect(self.show_plot)

        self.result_lbl = QLabel('', self)
        self.result_lbl.move(20, 90)
        self.result_lbl.resize(380, 20)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(20, 90, 380, 20)
        self.progress.setValue(0)
        self.progress.hide()

        self.setWindowTitle('재생 횟수 그래프 설정')
        self.setGeometry(300, 300, 420, 130)
        self.show()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "파일 선택", "", "JSON Files (*.json)")
        if file_path:
            self.json_path = file_path
            self.result_lbl.setText(f"선택된 파일: {file_path.split('/')[-1]}")

    def show_plot(self):
        self.progress.setValue(0)
        self.progress.show()
        self.result_lbl.setText('')

        if not self.json_path:
            self.result_lbl.setText("먼저 JSON 파일을 선택해주세요.")
            self.progress.hide()
            return

        try:
            min_views = int(self.qle_min_views.text())
            max_videos = int(self.qle_max_videos.text())
        except ValueError:
            self.result_lbl.setText("숫자를 정확히 입력해주세요.")
            self.progress.hide()
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except Exception:
            self.result_lbl.setText("JSON 파일을 불러오는 데 실패했습니다.")
            self.progress.hide()
            return

        self.progress.setValue(20)

        # JSON 정제
        cleaned_data = []
        for entry in raw_data:
            title = entry.get("title", "")
            header = entry.get("header", "")
            details = entry.get("details", [])
            detail_names = [d.get("name", "") for d in details]

            if "YouTube 홈페이지에서 본 광고" in title:
                continue
            if any("출처: Google 광고" in dn for dn in detail_names):
                continue
            if "광고" in title or "광고" in header:
                continue

            # "을(를) 시청했습니다." 제거
            title = re.sub(r"을\(를\) 시청했습니다\.?", "", title).strip()
            entry["title"] = title
            cleaned_data.append(entry)

        self.progress.setValue(40)

        df = pd.DataFrame(cleaned_data)
        if 'title' not in df.columns:
            self.result_lbl.setText("title 항목이 없습니다.")
            self.progress.hide()
            return

        titles = df['title'].astype(str).tolist()
        names = df['name'].astype(str).tolist() if 'name' in df else [''] * len(titles)

        def clean_title(title, name):
            name = name.strip().lower().replace('\u200b', '')
            if '출처: google 광고' in name or 'dlsrjteh wldnjwnj' in name:
                return None
            title = title.strip().replace('\u200b', '')
            blocked_keywords = ['[삭제된 동영상]', '[비공개 동영상]', 'xdptj']
            if any(kw in title for kw in blocked_keywords):
                return None
            return title.strip()

        cleaned_titles = [clean_title(t, n) for t, n in zip(titles, names)]
        cleaned_titles = [t for t in cleaned_titles if t]

        self.progress.setValue(60)

        title_counts = Counter(cleaned_titles)
        filtered_counts = {k: v for k, v in title_counts.items() if v >= min_views}
        sorted_counts = dict(sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True))

        if not sorted_counts:
            self.result_lbl.setText(f"{min_views}회 이상 시청된 영상이 없습니다.")
            self.progress.hide()
            return

        self.progress.setValue(80)

        limited_counts = dict(list(sorted_counts.items())[:max_videos])
        x = list(limited_counts.keys())
        y = list(limited_counts.values())

        fig = px.bar(
            x=x,
            y=y,
            labels={'x': '영상 제목', 'y': '재생 횟수'},
            title=f'최소 {min_views}회 이상 재생, 상위 {max_videos}개 영상'
        )
        fig.update_traces(
            hovertemplate='%{x}<br>재생 횟수: %{y:d}회<extra></extra>'
        )
        fig.update_layout(
            xaxis_tickangle=90,
            height=1000,
            width=1400
        )

        fig.write_html("output_plot.html")
        self.progress.setValue(100)

        webbrowser.open("output_plot.html")
        self.progress.hide()
        self.result_lbl.setText("그래프를 웹에서 열었습니다.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
