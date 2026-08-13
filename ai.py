import json
import os
import re
import urllib.error
import urllib.request


def summarize_material(title: str, text: str, subject: str) -> dict:
    prompt = f"""You are an educational assistant for Grade 7 {subject} at a Philippine junior high school.
Summarize ONLY the uploaded lesson text. Do not add outside knowledge.
Return JSON with this shape:
{{
  "intro": "one friendly sentence",
  "sections": [
    {{"id": "s1", "heading": "short heading", "body": "2-4 student-friendly sentences", "citation": "p. 1"}}
  ]
}}
Use 3 to 5 sections. Cite approximate page or section from the source text.
Lesson title: {title}
Lesson text:
{text[:12000]}
"""
    data = _complete_json(prompt)
    sections = data.get("sections") or []
    if not sections:
        return _fallback_summary(title, text)
    normalized = []
    for index, section in enumerate(sections[:5], start=1):
        normalized.append(
            {
                "id": section.get("id") or f"s{index}",
                "heading": section.get("heading") or f"Section {index}",
                "body": section.get("body") or "",
                "citation": section.get("citation") or f"p. {index}",
            }
        )
    return {
        "intro": data.get("intro") or f"A short summary of {title} from your uploaded material.",
        "sections": normalized,
    }


def generate_hots_questions(title: str, text: str, subject: str, bloom: str, count: int, types: list[str]) -> list[dict]:
    bloom_line = {
        "mixed": "Mix Analyze (C4), Evaluate (C5), and Create (C6).",
        "c4": "All questions must target Analyze (C4).",
        "c5": "All questions must target Evaluate (C5).",
        "c6": "All questions must target Create (C6).",
        "Analyze": "All questions must target Analyze (C4).",
        "Evaluate": "All questions must target Evaluate (C5).",
        "Create": "All questions must target Create (C6).",
        "Mixed C4–C6": "Mix Analyze (C4), Evaluate (C5), and Create (C6).",
    }.get(bloom, "Mix Analyze (C4), Evaluate (C5), and Create (C6).")
    allowed = types or ["mcq", "essay", "problem"]
    prompt = f"""You generate HOTS questions for Grade 7 {subject}.
Use ONLY the uploaded lesson text. No outside facts.
{bloom_line}
Allowed types: {", ".join(allowed)}.
Create exactly {count} questions.
Return JSON:
{{
  "questions": [
    {{
      "bloom": "Analyze|Evaluate|Create",
      "type": "mcq|essay|problem",
      "prompt": "question",
      "options": [{{"id":"a","text":"..."}}, {{"id":"b","text":"..."}}, {{"id":"c","text":"..."}}, {{"id":"d","text":"..."}}],
      "answer": "b",
      "explanation": "short explanation grounded in the text",
      "rubric": "short rubric or null",
      "citation": "p. 2"
    }}
  ]
}}
For essay/problem, options should be [] and answer null.
Lesson title: {title}
Lesson text:
{text[:12000]}
"""
    data = _complete_json(prompt)
    questions = data.get("questions") or []
    if not questions:
        return _fallback_questions(title, text, count, allowed)
    return [_normalize_question(item, index) for index, item in enumerate(questions[:count], start=1)]


def _normalize_question(item: dict, index: int) -> dict:
    qtype = item.get("type") or "mcq"
    if qtype not in {"mcq", "essay", "problem"}:
        qtype = "mcq"
    options = item.get("options") or []
    if qtype != "mcq":
        options = []
    return {
        "id": index,
        "type": qtype,
        "type_label": {"mcq": "Multiple choice", "essay": "Essay", "problem": "Problem-solving"}[qtype],
        "bloom": item.get("bloom") or "Analyze",
        "prompt": item.get("prompt") or "Explain a key idea from the lesson.",
        "citation": item.get("citation") or "source text",
        "options": options,
        "answer": item.get("answer"),
        "explanation": item.get("explanation") or "Use evidence from the uploaded lesson.",
        "rubric": item.get("rubric"),
    }


_LAST_AI_ERROR = ""


def last_ai_error() -> str:
    return _LAST_AI_ERROR


def _set_ai_error(message: str) -> None:
    global _LAST_AI_ERROR
    _LAST_AI_ERROR = message
    print(f"[ai] {message}")


def _complete_json(prompt: str) -> dict:
    raw = _complete(prompt)
    if not raw:
        return {}
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        _set_ai_error("Model returned text that was not valid JSON.")
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        _set_ai_error("Could not parse model JSON.")
        return {}


def _complete(prompt: str) -> str:
    global _LAST_AI_ERROR
    _LAST_AI_ERROR = ""
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    provider = os.environ.get("AI_PROVIDER", "").strip().lower()

    # Prefer Gemini when both keys exist unless AI_PROVIDER forces openai.
    order = []
    if provider == "openai":
        order = ["openai", "gemini"]
    elif provider == "gemini":
        order = ["gemini", "openai"]
    elif gemini_key:
        order = ["gemini", "openai"]
    else:
        order = ["openai", "gemini"]

    errors = []
    for name in order:
        if name == "openai" and openai_key:
            try:
                return _openai(prompt, openai_key)
            except Exception as exc:
                detail = _http_error_text(exc)
                errors.append(f"OpenAI: {detail}")
        if name == "gemini" and gemini_key:
            try:
                return _gemini(prompt, gemini_key)
            except Exception as exc:
                detail = _http_error_text(exc)
                errors.append(f"Gemini: {detail}")

    if not openai_key and not gemini_key:
        _set_ai_error("No OPENAI_API_KEY or GEMINI_API_KEY set. Using fallback questions.")
    elif errors:
        _set_ai_error(" | ".join(errors) + " Using fallback questions.")
    else:
        _set_ai_error("AI provider returned an empty response. Using fallback questions.")
    return ""


def _http_error_text(exc: Exception) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        body = exc.read().decode("utf-8", errors="ignore")
        return f"HTTP {exc.code} {body[:240]}"
    return f"{type(exc).__name__}: {exc}"


def _openai(prompt: str, key: str) -> str:
    body = json.dumps(
        {
            "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            "temperature": 0.4,
            "messages": [
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"]


def _gemini(prompt: str, key: str) -> str:
    configured = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip()
    models = []
    for model in (configured, "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"):
        if model and model not in models:
            models.append(model)

    last_error = None
    for model in models:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={key}"
        )
        body = json.dumps(
            {
                "contents": [{"parts": [{"text": "Return valid JSON only.\n\n" + prompt}]}],
                "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json"},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            candidates = payload.get("candidates") or []
            if not candidates:
                raise RuntimeError(f"{model} returned no candidates: {payload}")
            parts = candidates[0].get("content", {}).get("parts") or []
            text = "".join(part.get("text", "") for part in parts).strip()
            if not text:
                raise RuntimeError(f"{model} returned empty text: {payload}")
            return text
        except Exception as exc:
            last_error = exc
            continue
    raise last_error or RuntimeError("Gemini request failed")


def _fallback_summary(title: str, text: str) -> dict:
    sentences = _sentences(text)
    chunks = [sentences[i : i + 2] for i in range(0, min(len(sentences), 8), 2)] or [[text[:280]]]
    sections = []
    for index, chunk in enumerate(chunks[:4], start=1):
        sections.append(
            {
                "id": f"s{index}",
                "heading": f"Key idea {index}",
                "body": " ".join(chunk)[:500],
                "citation": f"p. {index}",
            }
        )
    return {
        "intro": f"A short student-friendly summary of {title} from the uploaded material.",
        "sections": sections,
    }


def _fallback_questions(title: str, text: str, count: int, allowed: list[str]) -> list[dict]:
    sentences = _sentences(text) or [f"{title} is the focus of this lesson."]
    blooms = ["Analyze", "Evaluate", "Create"]
    types_cycle = [t for t in ["mcq", "essay", "problem"] if t in allowed] or ["mcq"]
    questions = []
    for index in range(count):
        snippet = sentences[index % len(sentences)][:180]
        qtype = types_cycle[index % len(types_cycle)]
        bloom = blooms[index % 3]
        if qtype == "mcq":
            questions.append(
                {
                    "id": index + 1,
                    "type": "mcq",
                    "type_label": "Multiple choice",
                    "bloom": bloom,
                    "prompt": f"Based on the lesson about {title}, which statement best matches this idea: “{snippet}”?",
                    "citation": f"p. {index + 1}",
                    "options": [
                        {"id": "a", "text": "It is unrelated to the uploaded lesson."},
                        {"id": "b", "text": "It reflects a main idea from the uploaded material."},
                        {"id": "c", "text": "It should be ignored because it is only an example."},
                        {"id": "d", "text": "It replaces the need for evidence from the text."},
                    ],
                    "answer": "b",
                    "explanation": "The best choice stays grounded in the uploaded lesson instead of outside ideas.",
                    "rubric": None,
                }
            )
        elif qtype == "essay":
            questions.append(
                {
                    "id": index + 1,
                    "type": "essay",
                    "type_label": "Essay",
                    "bloom": bloom,
                    "prompt": f"Using the lesson on {title}, evaluate this idea and explain with evidence: “{snippet}”",
                    "citation": f"p. {index + 1}",
                    "options": [],
                    "answer": None,
                    "explanation": "A strong answer makes a clear claim and supports it with details from the uploaded text.",
                    "rubric": "Claim + evidence from the lesson + explanation.",
                }
            )
        else:
            questions.append(
                {
                    "id": index + 1,
                    "type": "problem",
                    "type_label": "Problem-solving",
                    "bloom": bloom,
                    "prompt": f"Create an original Grade 7 example that applies this idea from {title}: “{snippet}”",
                    "citation": f"p. {index + 1}",
                    "options": [],
                    "answer": None,
                    "explanation": "A solid response invents a new example and clearly connects it to the lesson idea.",
                    "rubric": "Original example + connection to the lesson.",
                }
            )
    return questions


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if len(part.strip()) > 40][:20]
