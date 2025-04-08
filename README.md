# Yt_Viz
유튜브 재생 횟수 시각화 

Visualize YouTube play count

### 🖥 프로젝트 소개 (Introduction to the Project)
- 본 프로젝트는 사용자의 YouTube 시청 기록(JSON 형식)을 불러와, 특정 기준에 따라 필터링 및 정제하고, 가장 많이 본 영상을 시각화하는 데스크탑 애플리케이션입니다.
- PyQt5를 기반으로 직관적인 GUI를 제공하며, Plotly를 활용한 동적 바 차트로 시청 데이터를 시각적으로 분석할 수 있습니다.
  
- This project is a desktop application that loads a user's YouTube watch history (in JSON format), filters and cleans the data based on specific criteria, and visualizes the most frequently watched videos.
- It features an intuitive GUI built with PyQt5 and uses Plotly to generate dynamic bar charts for visual analysis of viewing data.

### 💡 주요 기능
#### GUI 기반 사용자 입력

- 최소 재생 횟수 설정

- 최대 영상 갯수 제한

- JSON 파일 탐색 및 선택


#### 데이터 전처리 및 필터링

- 광고 관련 항목 자동 제거

- 제목 및 세부정보 정제

- 삭제되거나 비공개된 영상 필터링


#### 시청 횟수 분석

- 영상별 시청 횟수 집계

- 최소 재생 횟수 이상 필터 적용

- 상위 영상 수 제한

  
#### 시각화 결과 제공

- Plotly로 인터랙티브한 바 차트 생성

- HTML 파일로 그래프 자동 생성 및 웹 브라우저 열기
  
#### ⚙️ 개발 환경 (Development Environment)
- python 3.11.0
