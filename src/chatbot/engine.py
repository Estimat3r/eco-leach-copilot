"""Gemini 기반 AI 챗봇 엔진 — 침출 공정 전문 어시스턴트."""

from __future__ import annotations
from google import genai
from google.genai import types

SYSTEM_PROMPT = """
당신은 NCM811 폐배터리 침출 공정 전문 AI 어시스턴트입니다.
사용자는 폐배터리 재활용 현장 엔지니어 또는 연구자입니다.

당신의 역할:
1. 침출 공정 조건(온도, 시간, H₂SO₄ 농도, H₂O₂ 농도, 고액비)에 대한 질문에 답변
2. Li, Ni, Co, Mn 회수율 최적화 방법 안내
3. 탄소 배출 감축 전략 제안 (LCA 기반 emission factor 활용)
4. 공정 조건 간 trade-off 설명
5. 시뮬레이터 사용 방법 안내

핵심 지식:
- 침출 시스템: NCM811 / H₂SO₄ + H₂O₂ / stirred batch leaching
- 탄소 배출 계산: 가열(한국 전력 0.459 kg CO₂/kWh) + H₂SO₄(0.09 kg CO₂/kg) + H₂O₂(2.5 kg CO₂/kg)
- 온도 범위: 10~90°C, 시간: 1~360분, H₂SO₄: 0.3~2.0M, H₂O₂: 0~1.96M, 고액비: 20~333 g/L
- 고온/고농도 조건은 회수율을 높이지만 탄소 배출도 증가
- 포화 구간 이후 반응 시간 연장은 탄소 낭비

답변 원칙:
- 한국어로 답변
- 구체적인 수치와 근거를 제시
- 회수율과 탄소 배출을 항상 함께 고려
- 불확실한 내용은 솔직하게 인정
- 간결하고 실용적으로 답변 (3~5문장 권장)
"""


def get_client(api_key: str) -> genai.Client:
    """Gemini 클라이언트 초기화."""
    return genai.Client(api_key=api_key)


def chat(client: genai.Client, history: list[dict], user_message: str) -> str:
    """Gemini에 메시지 전송 후 응답 반환."""
    # history를 genai Content 형식으로 변환
    contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
        ),
    )
    return response.text


def build_context_message(
    condition: dict[str, float] | None = None,
    last_result: dict | None = None,
) -> str:
    """현재 시뮬레이터 상태를 챗봇 컨텍스트로 변환."""
    parts = []
    if condition:
        parts.append(
            f"[현재 입력 조건] "
            f"온도: {condition.get('temp_C')}°C, "
            f"시간: {condition.get('time_min')}분, "
            f"H₂SO₄: {condition.get('h2so4_M')}M, "
            f"H₂O₂: {condition.get('h2o2_M')}M, "
            f"고액비: {condition.get('pulp_density_gL')}g/L"
        )
    if last_result:
        leach = last_result.get("leach_rates", {})
        carbon = last_result.get("carbon_total_kg")
        if leach:
            parts.append(
                f"[최근 시뮬레이션 결과] "
                f"Li: {leach.get('Li_pct', 0):.1f}%, "
                f"Ni: {leach.get('Ni_pct', 0):.1f}%, "
                f"Co: {leach.get('Co_pct', 0):.1f}%, "
                f"Mn: {leach.get('Mn_pct', 0):.1f}%"
            )
        if carbon is not None:
            parts.append(f"[탄소 배출량] {carbon:.4f} kg CO₂")
    return "\n".join(parts)
