# 🎥 Yt_Viz  
**유튜브 재생 횟수 시각화**  
**Visualize YouTube Play Count**

---

## 💻 프로젝트 소개 (Introduction to the Project)

- 본 프로젝트는 사용자의 YouTube 시청 기록(JSON 형식)을 불러와, 특정 기준에 따라 필터링 및 정제하고, 가장 많이 보는 영상을 시각화하는 데스크톱 애플리케이션입니다.  
- PyQt5 기반의 직관적인 GUI를 제공하며, Plotly를 활용해 시청 데이터를 동적적으로 시각화합니다.

- This project is a desktop application that loads a user's YouTube watch history (in JSON format), filters and cleans the data based on specific criteria, and visualizes the most frequently watched videos.  
- It features an intuitive GUI built with PyQt5 and uses Plotly to generate dynamic bar charts for visual analysis of viewing data.

---

## 💡 주요 기능 (Key Features)

### ✅ GUI 기반 사용자 입력 (User Input via GUI)
- 최소 재생 횟수 설정 (Set minimum view count)  
- 최대 영상 객수 제한 (Limit number of top videos)  
- JSON 파일 탐색 및 선택 (Browse and select JSON file)

### ✅ 데이터 전처리 및 필터링 (Data Cleaning and Filtering)
- 광고 관련 항목 자동 제거 (Automatic removal of ads)  
- 제목 및 세부정보 정제 (Refinement of titles and metadata)  
- 삭제/비공개 영상 제거 (Filter out deleted/private videos)

### ✅ 시청 횟수 배정 (Viewing Count Analysis)
- 영상별 시청 횟수 집계 (Count views per video)  
- 사용자 기준에 따른 필터링 적용 (Filter by view threshold)  
- 상위 영상 수 제한 (Limit number of displayed results)

### ✅ 시각화 결과 제공 (Visualization Output)
- Plotly 기반 인터랙티브 바 체트 생성 (Interactive bar chart with Plotly)  
- HTML 파일 자동 생성 및 웹 브라우저 실행 (Auto-generated HTML opened in browser)

---

## 📂 사용 방법 (How to Use)
1. [Google Takeout](https://takeout.google.com/)에서 유튜브 시청 기록(JSON 파일)을 다운로드합니다.  
2. 애플리케이션 실행 후 `파일 선택` 버튼으로 JSON 파일을 선택합니다.  
3. `최소 재생 횟수`와 `최대 영상 객수`를 입력한 드지 `그래프 보기`를 클릭합니다.  
4. 브라우저가 열리며 배열 결과가 시각화된 그래프가 Í \xcd9c력됩니다.

---

## ⚙️ 개발 환경 (Development Environment)
- Python 3.11.0  
- PyQt5  
- Pandas  
- Plotly

