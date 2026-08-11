[![English](https://img.shields.io/badge/Language-English-blue?style=for-the-badge)](README.md)
[![한국어](https://img.shields.io/badge/Language-한국어-red?style=for-the-badge)](README_KO.md)

<div align="center">
  <img src="assets/aegiscore_logo_banner.svg" alt="Aegiscore Logo">
</div>

<h1 align="center">Aegiscore — 자율 레드팀 에이전트</h1>

<p align="center"><i>"또 AI 해킹 툴이야? nmap 돌리고 리포트 쓰는 거 아니야?"</i></p>

<div align="center">

<a href="https://github.com/karishmaram-tech/AegisCore/blob/main/LICENSE">
  <img src="https://img.shields.io/github/license/karishmaram-tech/AegisCore?style=for-the-badge&color=blue" alt="License: Apache 2.0">
</a>
<a href="https://github.com/karishmaram-tech/AegisCore/stargazers">
  <img src="https://img.shields.io/github/stars/karishmaram-tech/AegisCore?style=for-the-badge&color=yellow" alt="Stargazers">
</a>
<a href="https://github.com/karishmaram-tech/AegisCore/graphs/contributors">
  <img src="https://img.shields.io/github/contributors/karishmaram-tech/AegisCore?style=for-the-badge&color=orange" alt="Contributors">
</a>



</div>

<br/>

<div align="center">
  <em>데모 영상 준비 중 - 녹화가 진행 중입니다.</em>
</div>



## 설치

설치 및 로컬 개발 환경 구축은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

→ **[빠른 시작](docs/getting-started.md)** · **[전체 셋업 가이드](docs/setup-guide.md)**

### 라이브러리로 사용 (pip)

에이전트 위에 무언가를 만드시나요 — 제품, 연구 통합, 커스텀 오케스트레이터? SDK 를 PyPI 에서 설치하세요:

```bash
pip install aegiscore              # 코어 SDK
pip install "aegiscore[neo4j]"     # + 지식그래프 공격체인 도구
```

`aegiscore` 은 **클라이언트 SDK** 입니다 — 에이전트 팩토리·미들웨어·도구·스킬을 담고 있고, LLM 호출과 샌드박스 실행은 런타임 서비스로 HTTP 라우팅합니다 (`AEGISCORE_LLM__PROXY_URL`, `SANDBOX_URL`). 에이전트를 실제로 돌리려면 그 서비스들이 필요합니다 — 위 Docker 스택을 쓰거나 URL 을 직접 가리키세요. 팩토리 오버라이드 surface, 선언적 `PluginBundle` 플러그인, 안전 게이트는 **[라이브러리로서의 Aegiscore](docs/library-usage.md)** 참고.



---

## 벤치마크

*벤치마크 결과 준비 중 — AegisCore에 자체 평가 스위트를 실행한 후 업데이트될 예정입니다.*

---

## Aegiscore이란?

AI + 해킹 도구들은 대부분 nmap 돌리고 리포트 출력하는 데모입니다. Aegiscore은 다릅니다.

**Aegiscore은 전문 자율 레드팀 에이전트입니다.** 실제 공격자처럼 현실적인 공격 체인을 실행합니다 — 정찰, 초기 침투, 권한 상승, 횡이동, C2 — 스캐너가 아닌 실제 공격자의 방식으로.

더 중요한 것은: 스크립트 키디와 레드티머를 구분하는 전문성을 갖추고 있다는 점입니다. 첫 번째 패킷이 나가기 전에 Aegiscore은 완전한 인게이지먼트 패키지 — **RoE**, **ConOps**, **디컨플릭션 플랜**, MITRE ATT&CK 매핑이 포함된 **OPPLAN** — 을 생성하고, 모든 행동은 그 규칙 안에서만 동작합니다.

→ **[인게이지먼트 워크플로 상세](docs/engagement-workflow.md)**

---

## 왜 Aegiscore인가?

**체크리스트 스캔이 아닌 실제 킬체인.** Aegiscore은 OPPLAN을 읽고 열린 경로를 통해 목표를 추적합니다 — 피벗, 적응, 기술 체이닝.

**진짜 인터랙티브 셸.** 실제 공격 도구들은 인터랙티브합니다 (`msfconsole`, `sliver-client`, `evil-winrm`). Aegiscore은 영구 tmux 세션에서 명령을 실행하고 인터랙티브 프롬프트를 자동 감지합니다 — 도구가 프롬프트를 띄우면 우회책 없이 후속 명령을 보냅니다.

**하드닝된 샌드박스 격리.** 모든 명령은 운영 네트워크(`sandbox-net`)의 Kali Linux 샌드박스에서 실행되며, 관리망(`aegiscore-net`)과 분리되어 있습니다. LangGraph는 Docker 소켓으로 샌드박스를 제어합니다. → **[아키텍처](docs/architecture.md)**

**공격이 방어를 만든다.** 계획 중인 [공격형 백신](docs/offensive-vaccine.md) 루프는 발견된 취약점을 공격 → 방어 → 검증 사이클로 전환하는 방향입니다.

---

## 아키텍처

<div align="center">
  <img src="assets/aegiscore_infra.svg" alt="Aegiscore Infrastructure" width="680">
</div>

두 개의 네트워크로 분리된 설계 — 관리 서비스(LiteLLM, PostgreSQL, LangGraph, Web)는 `aegiscore-net`, 샌드박스 / C2 서버 / 타깃은 `sandbox-net`. Neo4j는 양 네트워크에 듀얼-홈으로 두어 관리망의 에이전트가 샌드박스 내부에서 기록한 발견 사항을 영속화할 수 있게 합니다.

→ **[아키텍처 상세](docs/architecture.md)** · **[지식 그래프](docs/knowledge-graph.md)**

---

## 에이전트

킬체인 단계별로 구성된 16개의 전문 에이전트. 각 에이전트는 목표마다 새로운 컨텍스트 윈도우로 시작 — 누적 노이즈 없음.

오케스트레이션 · 정찰 · 초기 침투 · 사후 익스플로잇 · 취약점 연구 · 도메인 스페셜리스트 (AD, Cloud, 스마트 컨트랙트, 리버싱, Analyst).

→ **[에이전트 전체 목록 및 미들웨어 스택](docs/agents.md)**

---

## 모델 & 프로바이더

Tier 기반 자격증명-aware 폴백 체인. 사용 가능한 자격증명을 우선순위 순으로 알려주면, 모든 tier에서 primary→fallback 체인이 자동 구성됩니다.

| 프로파일 | 에이전트당 tier | 사용 케이스 |
|----------|------------------|-------------|
| **eco** (기본) | 에이전트별 (orchestrator/exploiter/patcher/analyst=HIGH, execution=MID, recon/soundwave=LOW) | 프로덕션 |
| **max** | 모든 에이전트 HIGH | 고가치 타깃 |
| **test** | 모든 에이전트 LOW | 개발 / CI |

**Tier가 매핑된 프로바이더**: Anthropic, OpenAI, Google Gemini, MiniMax, DeepSeek, xAI, Mistral, OpenRouter, Nvidia NIM, Ollama (로컬).
**구독 OAuth**: Claude Max/Pro/Team, ChatGPT Pro/Plus/Team, Gemini Advanced, Copilot Pro, SuperGrok, Perplexity Pro.

`aegiscore onboard`로 설정. → **[모델 전체 레퍼런스 및 폴백 예시](docs/models.md)**

---

## 문서

| 주제 | 문서 |
|------|------|
| 설치 및 첫 인게이지먼트 | [시작하기](docs/getting-started.md) |
| 셋업 / OAuth / 프로바이더 / 대시보드 전체 | [셋업 가이드](docs/setup-guide.md) |
| 모든 CLI 커맨드와 단축키 | [CLI 레퍼런스](docs/cli-reference.md) |
| 모든 `make` 타깃 | [Makefile 레퍼런스](docs/makefile-reference.md) |
| 에이전트 목록 및 미들웨어 | [에이전트](docs/agents.md) |
| 모델 프로필과 폴백 체인 | [모델](docs/models.md) |
| 스킬 시스템과 포맷 스펙 | [스킬](docs/skills.md) |
| 웹 대시보드 기능 및 설정 | [웹 대시보드](docs/web-dashboard.md) |
| 시스템 아키텍처와 네트워크 격리 | [아키텍처](docs/architecture.md) |
| Neo4j 지식 그래프 | [지식 그래프](docs/knowledge-graph.md) |
| 엔드투엔드 인게이지먼트 워크플로 | [인게이지먼트 워크플로](docs/engagement-workflow.md) |
| 공격형 백신 루프 | [공격형 백신](docs/offensive-vaccine.md) |
| Aegiscore 기여하기 | [기여 가이드](docs/contributing.md) |

---

## 기여하기

```bash
git clone https://github.com/karishmaram-tech/AegisCore.git
cd Aegiscore
make dev     # 핫 리로드로 시작
make cli     # 인터랙티브 CLI 열기 (별도 터미널)
```

→ **[기여 가이드](docs/contributing.md)**



---

## 면책조항

시스템 소유자로부터 명시적인 서면 허가 없이 어떠한 시스템이나 네트워크에도 이 프로젝트를 사용하지 마십시오. 컴퓨터 시스템에 대한 무단 접근은 불법입니다. 귀하의 행동에 대한 책임은 전적으로 귀하에게 있습니다. 이 프로젝트의 저자와 기여자는 오용에 대한 어떠한 책임도 지지 않습니다.

---

## 라이선스

[Apache-2.0](LICENSE)

---

<div align="center">
  <img src="assets/main.png" alt="Aegiscore">
</div>
