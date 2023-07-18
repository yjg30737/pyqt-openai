# pyqt-openai
<div align="center">
  <img src="https://user-images.githubusercontent.com/55078043/229002952-9afe57de-b0b6-400f-9628-b8e0044d3f7b.png" width="150px" height="150px"><br/><br/>
  
  [![](https://dcbadge.vercel.app/api/server/cHekprskVE)](https://discord.gg/cHekprskVE)
</div>

ChatGPT를 본따 만든 파이썬을 이용한 데스크톱 챗봇입니다.

데스크톱 gui를 구성하는 데는 qt의 파이썬 바인딩 버전인 pyqt를 이용하였습니다.

openai api 키만 있으면 chatgpt와 같이 이용하실 수 있으며, 대화 목록 관리도 가능합니다.

모델은 gpt3.5, gpt4, 0613 버전 등 openai 플레이그라운드에서 볼 수 있는 것들은 모두 지원합니다.

그리고 데스크톱 소프트웨어의 강점인 윈도우 항상 최상위로 만들기, 투명도 조절도 가능하며

awesome-chatgpt-prompts와 같은 프롬프트 목록이 있기 때문에 프롬프트 자동완성 입력도 가능합니다.

데이터베이스 시스템은 데스크톱 소프트웨어의 영원한 친구인 sqlite입니다.

질문사항이 있으시면 뭐든 물어보세요.

프로필에 있는 제 이메일 혹은 현재 페이지 상단의 디스코드 배지를 누른 뒤, 저에게 dm을 보내셔도 됩니다.

개인적으로 AI 개발자라면 미드저니의 본산인데다가, 봇을 등록할 수 있는 메신저인 디스코드에 익숙해지는 것도 좋을 거라는 게 제 생각입니다 :)

## 기능
* 기본적으로 pyqt-openai는 이미지 생성 도구를 포함한 <b>ChatGPT의 데스크톱 애플리케이션 버전</b>입니다.
  * 텍스트 스트리밍 (기본으로 활성화되어 있으며, 비활성화할 수 있음)
  * 인공지능이 이전 대화 기록을 기억
  * 복사 버튼 지원
* <b>대화 관리</b>
  * 대화 추가 및 삭제
  * 대화 저장 - SQLite db, 텍스트 파일 압축 파일, HTML 파일 압축 파일 (둘 다 zip)
  * 대화 이름 변경
  * 위의 모든 내용은 conv.db라는 SQLite 데이터베이스 파일에 저장됩니다.
* OpenAI playground와 같이 매개변수(온도, top_p 등) 제어 지원
* <b>GPT-4-32k-0613</b>과 같은 최신 모델 지원
* <b>프롬프트 생성기</b> 지원 (관리 가능하며, 데이터베이스에 자동 저장됨)
* <b>슬래시 명령어</b> 지원
* 프롬프트 시작 및 종료 부분 지원
* 백그라운드 애플리케이션에서 실행할 수 있음
  * 응답이 생성되면 알림이 표시됨
* 창을 위에 유지하거나 투명도를 조절 가능
* 이미지 생성 (DALL-E)
* 이미지를 원하는 경우 복사 및 다운로드 가능. 이미지 위로 마우스 커서를 가져가면 됩니다.
* <b>llama-index</b>를 사용하여 OpenAI 모델 파인튜닝 가능
* 텍스트 기반 파일 업로드 지원

## 설치 방법
1. git clone ~
2. cd pyqt-openai
3. pip install -r requirements.txt --upgrade
4. cd pyqt_openai
5. API key 입력란에 API 키를 입력해야 합니다. OpenAI의 <a href="https://platform.openai.com/account/api-keys">공식 사이트</a>에서 이를 얻을 수 있습니다. 받기 전에 회원가입 및 로그인을 하셔야 됩니다.

이 API 키는 한번 생성하면 다시 안보여지므로 꼭 보관해두셔야 됩니다. 

6. python main.py

## 프리뷰
![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/c3f255c7-4c79-4ffe-aefa-1e0e55492362)
