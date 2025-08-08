# 🎥 Yt_Viz  
**유튜브 기록 시각화 도구**  
**Visualize Your YouTube History**

---

## 💻 프로젝트 소개 (Introduction to the Project)

- 이 프로젝트는 사용자의 유튜브 **시청기록** 및 **검색기록** (JSON 형식)을 불러와, 필터링/정제 후 **가장 많이 본 영상** 또는 **가장 많이 검색한 키워드**를 **시각화**하는 데스크톱 애플리케이션입니다.
- PyQt5 기반 GUI로 쉽고 직관적인 조작이 가능하며, Plotly를 활용해 **인터랙티브한 그래프**를 생성합니다.

---

## 💡 주요 기능 (Key Features)

### ✅ GUI 기반 분석 선택 (GUI-Based Interaction)
- 두 개의 탭 제공: `시청기록`, `검색기록`  
- 각 탭에서 개별적으로 JSON 파일 선택 및 분석 실행 가능

### ✅ 사용자 설정 적용 (Customizable Settings)
- **최소 반복 횟수** 설정 (예: 3회 이상 시청/검색한 항목만 보기)  
- **최대 표시 항목 수** 제한 (예: 상위 20개만 시각화)

### ✅ 데이터 정제 및 필터링 (Data Cleaning)
- 광고 관련 기록 자동 제거  
- 삭제된 영상 / 비공개 영상 / 스팸 검색어 등 제거  
- 제목 및 키워드 자동 정제

### ✅ 시각화 결과 제공 (Interactive Visualization)
- Plotly 기반 바 차트 생성  
- HTML 파일로 자동 저장 및 브라우저 자동 실행

---

## 📂 사용 방법 (How to Use)

1. [Google Takeout](https://takeout.google.com/)에서 YouTube 데이터를 다운로드하세요.  
   - "YouTube 및 YouTube Music" → "시청기록" 및 "검색기록" 포함  
2. 애플리케이션 실행 후 `시청기록` 또는 `검색기록` 탭에서 JSON 파일을 선택합니다.  
3. `최소 횟수`와 `최대 표시 갯수`를 입력한 뒤 `분석 실행` 버튼을 클릭하세요.  
4. 브라우저에서 분석 결과가 시각화되어 자동으로 열립니다.

---

## 🔗 실행 파일 (.exe)

가장 많이 본 영상 조회

[👉 다운로드 (Google Drive)](https://drive.google.com/file/d/1Sj7kfXiU6wdWlR8wjrGigCxzdsUJ3ZFZ/view?usp=sharing)

유튜브 전체기간 누적 시청시간

[👉 다운로드 (Google Drive)](https://drive.google.com/file/d/1gkCfx8nhH-FjMYjipm9BMCH2QXA0VDDd/view?usp=sharing)

---

## ⚙️ 개발 환경 (Development Environment)

- Python 3.11.0  
- PyQt5  
- Pandas  
- Plotly

---

