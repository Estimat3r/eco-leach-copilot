"""OpenAI 기반 AI 챗봇 엔진 — 침출 공정 전문 어시스턴트."""

from __future__ import annotations
import json
from openai import OpenAI

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """당신은 NCM811 폐배터리 침출 공정 전문 AI 어시스턴트입니다.
사용자는 폐배터리 재활용 현장 엔지니어 또는 연구자입니다.

당신의 역할:
1. 침출 공정 조건(온도, 시간, H₂SO₄ 농도, H₂O₂ 농도, 고액비)에 대한 질문에 답변
2. Li, Ni, Co, Mn 회수율 최적화 방법 안내
3. 탄소 배출 감축 전략 제안 (LCA 기반 emission factor 활용)
4. 공정 조건 간 trade-off 설명
5. 그래프/차트 요청 시 조건을 파악하여 시뮬레이터가 차트를 생성하도록 안내

핵심 지식:
- 침출 시스템: NCM811 / H₂SO₄ + H₂O₂ / stirred batch leaching
- 탄소 배출: 가열(한국 전력 0.459 kg CO₂/kWh) + H₂SO₄(0.09 kg CO₂/kg) + H₂O₂(2.5 kg CO₂/kg)
- 온도 범위: 10~90°C, 시간: 1~360분, H₂SO₄: 0.3~2.0M, H₂O₂: 0~2.0M, 고액비: 20~333 g/L

답변 원칙:
- 한국어로 답변
- 구체적인 수치와 근거 제시
- 회수율과 탄소 배출을 항상 함께 고려
- 간결하고 실용적으로 (3~5문장 권장)"""

# 그래프 생성용 function calling 도구 정의
CHART_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_comparison_chart",
            "description": "두 공정 조건의 금속 회수율과 탄소 배출량을 비교하는 차트를 생성합니다. 사용자가 두 조건 비교 그래프를 요청할 때 호출하세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "condition_a": {
                        "type": "object",
                        "description": "조건 A의 공정 파라미터",
                        "properties": {
                            "temp_C": {"type": "number", "description": "온도 (°C), 10~90"},
                            "time_min": {"type": "number", "description": "반응 시간 (분), 1~360"},
                            "h2so4_M": {"type": "number", "description": "H₂SO₄ 농도 (M), 0.3~2.0"},
                            "h2o2_M": {"type": "number", "description": "H₂O₂ 농도 (M), 0~2.0"},
                            "pulp_density_gL": {"type": "number", "description": "고액비 (g/L), 20~333"},
                        },
                        "required": ["temp_C", "time_min", "h2so4_M", "h2o2_M", "pulp_density_gL"],
                    },
                    "condition_b": {
                        "type": "object",
                        "description": "조건 B의 공정 파라미터",
                        "properties": {
                            "temp_C": {"type": "number"},
                            "time_min": {"type": "number"},
                            "h2so4_M": {"type": "number"},
                            "h2o2_M": {"type": "number"},
                            "pulp_density_gL": {"type": "number"},
                        },
                        "required": ["temp_C", "time_min", "h2so4_M", "h2o2_M", "pulp_density_gL"],
                    },
                    "label_a": {"type": "string", "description": "조건 A 레이블 (예: '고온 조건')"},
                    "label_b": {"type": "string", "description": "조건 B 레이블 (예: '저온 조건')"},
                },
                "required": ["condition_a", "condition_b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_kinetics_chart",
            "description": "특정 공정 조건에서 시간에 따른 금속 침출률 변화(kinetics) 차트를 생성합니다. 사용자가 시간에 따른 변화나 kinetics 그래프를 요청할 때 호출하세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "temp_C": {"type": "number"},
                    "h2so4_M": {"type": "number"},
                    "h2o2_M": {"type": "number"},
                    "pulp_density_gL": {"type": "number"},
                },
                "required": ["temp_C", "h2so4_M", "h2o2_M", "pulp_density_gL"],
            },
        },
    },
]


def get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)


def chat(
    client: OpenAI,
    history: list[dict],
    user_message: str,
) -> tuple[str, dict | None]:
    """OpenAI에 메시지 전송.

    Returns:
        (text_response, chart_request)
        chart_request: None 또는 {"type": "comparison"|"kinetics", ...}
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=CHART_TOOLS,
        tool_choice="auto",
        temperature=0.7,
        max_tokens=800,
    )

    msg = response.choices[0].message

    # 함수 호출 감지
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if func_name == "generate_comparison_chart":
            return "📊 요청하신 조건 비교 차트를 생성했습니다.", {
                "type": "comparison",
                "condition_a": args["condition_a"],
                "condition_b": args["condition_b"],
                "label_a": args.get("label_a", "조건 A"),
                "label_b": args.get("label_b", "조건 B"),
            }
        elif func_name == "generate_kinetics_chart":
            return "📈 요청하신 Kinetics 차트를 생성했습니다.", {
                "type": "kinetics",
                **args,
            }

    return msg.content or "", None


def build_context_message(
    condition: dict[str, float] | None = None,
    last_result: dict | None = None,
) -> str:
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
