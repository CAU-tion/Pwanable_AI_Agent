# Pwanable_AI_Agent
### 프로젝트 개요

LLM 기반 **AI Agent가 보안 워게임 문제를 스스로 분석하고 해결하는 시스템**을 개발합니다.

Agent에게 Web, Pwnable 등 분야별 보안 도구와 실행 환경을 제공하고,  
**문제 분석 → 도구 실행 → 결과 분석 → 재시도** 과정을 반복하여 Flag를 획득하도록 합니다.

또한 풀이 과정과 실행 기록을 Memory로 관리하여 이후 문제 해결에 활용할 수 있는 구조를 구현합니다.

---

### 프로젝트장

**CAUtion 0기 이병현**

---

### 프로젝트 방식

#### 공통 Agent/Core 개발 + Pwnable 하네스 구성

- **공통**
  - LLM API
  - Tool Calling
  - Memory
  - Logging
  - 기타 Agent 핵심 기능 개발

- **Pwnable 분야**
  - Pwnable 문제 풀이에 필요한 도구 구성
  - Agent가 도구를 사용할 수 있는 실행 환경 구축
  - 분야에 적합한 Harness 설계 및 구현

- **평가 및 분석**
  - 완성된 Agent를 실제 워게임 문제에 적용
  - **문제 해결 성공률** 비교
  - **풀이 과정** 분석
  - **Tool 사용 방식 및 호출 횟수** 분석
  - Harness 구성에 따른 성능 차이 비교

---

### 프로젝트 목적

단순히 LLM에게 문제 풀이를 질문하는 것을 넘어,  
**AI가 직접 보안 도구를 활용하여 문제를 해결하는 Agent**를 구현하는 것이 목표입니다.

프로젝트를 통해 다음 내용을 함께 학습합니다.

- **AI Agent 구조 및 동작 원리**
- **LLM API 및 Tool Calling**
- **Memory / Logging / Planning 구조**
- **System / Pwnable 보안 지식**
- **보안 도구를 Agent와 연결하는 Harness 구성**

최종적으로 **Harness의 구성에 따라 Agent의 문제 해결 성능이 어떻게 달라지는지 분석**하고,  
효율적인 보안 워게임 풀이 Agent 구조를 탐구합니다.
