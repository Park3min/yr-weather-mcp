<p align="center">
  <img src="logo.png" width="140" alt="YR Weather Logo" />
</p>

# YR Weather MCP Server 🌤️

노르웨이 기상청(MET Norway / YR) API를 활용한 Claude Desktop용 Model Context Protocol (MCP) 날씨 서버입니다.

## 🚀 주요 기능
- **실시간 날씨**: 특정 위도/경도의 기온, 풍속, 습도, 날씨 상태 조회
- **시간대별 예보**: 향후 24시간 주요 시간대별 날씨 요약
- **주간 예보**: 일자별 최저/최고 기온 및 풍속 범위 분석

---

## ⚙️ 설치 및 설정 방법

### 방법 1. .dxt 파일 원클릭 설치 (추천 ⭐️)
1. GitHub 저장소에서 `yr-weather-mcp.dxt` 파일을 다운로드합니다.
2. 다운로드받은 `yr-weather-mcp.dxt` 파일을 더블클릭하여 Claude Desktop에 바로 설치합니다.

---

### 방법 2. GitHub 원격 연동 (uvx 사용)
`claude_desktop_config.json` 설정 파일에 아래 항목을 추가합니다.

```json
{
  "mcpServers": {
    "yr-weather": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Park3min/yr-weather-mcp.git",
        "yr-weather-mcp"
      ]
    }
  }
}
```

---

## 💡 사용 예시 (Claude 대화)
- *"서울 오늘 날씨랑 시간대별 예보 알려줘"*
- *"위도 37.5665, 경도 126.9780 주간 날씨 예보 어때?"*
