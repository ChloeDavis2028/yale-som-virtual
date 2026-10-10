"""Read-only access to the Yale SOM course catalog in data/yale_som.db.

Only public course fields are ever returned: never faculty_1_email. PhD courses are skipped.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "yale_som.db"
FIELDS = [
    "course_number", "course_title", "course_category", "course_session", "course_description",
    "faculty_1", "faculty_bio", "daytimes", "room", "section", "units",
]
DESCRIPTION_LIMIT = 400


def _query(sql: str, params: tuple = ()) -> list[dict]:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql, params)]
    finally:
        con.close()


def course_sections(number: str) -> list[dict]:
    """Every section of one course (e.g. 'MGT 409'), with all public fields."""
    cols = ", ".join(FIELDS)
    return _query(
        f"SELECT {cols} FROM courses WHERE course_category <> 'PhD' "
        "AND UPPER(REPLACE(course_number, ' ', '')) = UPPER(REPLACE(?, ' ', '')) ORDER BY section",
        (number.strip(),),
    )


def search_courses(keyword: str, limit: int = 8) -> list[dict]:
    """Courses whose number, title, description or instructor matches. Short descriptions, no bios."""
    cols = ", ".join(f for f in FIELDS if f != "faculty_bio")
    like = f"%{keyword.strip()}%"
    rows = _query(
        f"SELECT {cols} FROM courses WHERE course_category <> 'PhD' AND ("
        "course_number LIKE ? OR course_title LIKE ? OR course_description LIKE ? OR faculty_1 LIKE ?) "
        "ORDER BY course_number, section",
        (like, like, like, like),
    )
    seen, out = set(), []
    for r in rows:  # one row per course + instructor, not every section
        key = (r["course_number"], r["faculty_1"])
        if key in seen:
            continue
        seen.add(key)
        desc = r.get("course_description") or ""
        r["course_description"] = desc if len(desc) <= DESCRIPTION_LIMIT else desc[: DESCRIPTION_LIMIT - 1] + "…"
        out.append(r)
        if len(out) >= limit:
            break
    return out


# ---------- course material: questions and answers (data/course_material.db, built by seed_course_material.py)

MATERIAL_DB = DB.parent / "course_material.db"
STOPWORDS = {"what", "is", "the", "a", "an", "of", "and", "how", "do", "i", "does", "why", "to", "in", "for", "mean", "me", "explain"}


def _material(sql: str, params: tuple = ()) -> list[dict]:
    if not MATERIAL_DB.exists():
        return []
    con = sqlite3.connect(f"file:{MATERIAL_DB.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql, params)]
    finally:
        con.close()


def search_material(query: str, limit: int = 4) -> list[dict]:
    """Course Q&A whose topic, question or answer matches the words in the query, best matches first."""
    words = [w for w in "".join(ch if ch.isalnum() else " " for ch in query.lower()).split() if w not in STOPWORDS]
    if not words:
        return []
    rows = _material("SELECT course_number, topic, question, answer FROM course_qa")
    scored = []
    for r in rows:
        topic, q, a = r["topic"].lower(), r["question"].lower(), r["answer"].lower()
        score = sum(3 * (w in topic) + 2 * (w in q) + (w in a) for w in words)
        if score:
            scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:limit]]


def material_topics() -> list[str]:
    return [r["topic"] for r in _material("SELECT DISTINCT topic FROM course_qa ORDER BY topic")]


def course_brief(number: str) -> str:
    """Plain-text summary of one course for an agent's instructions."""
    sections = course_sections(number)
    if not sections:
        return f"No catalog entry found for {number}."
    first = sections[0]
    lines = [
        f"{first['course_number']}: {first['course_title']} ({first['course_category']}, "
        f"{first['units']} units, session {first['course_session']})",
        f"Instructor: {first['faculty_1']}",
        f"Description: {first['course_description'] or 'n/a'}",
        "Sections:",
    ]
    for s in sections:
        lines.append(f"- Section {s['section']}: {s['daytimes'] or 'time TBA'}, room {s['room'] or 'TBA'}")
    return "\n".join(lines)
