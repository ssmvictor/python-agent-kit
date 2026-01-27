# .agent Style Guide - Language & Conventions

> This document defines the standards for writing agent rules and skill instructions in this workspace.

## 1. Normative Language (RFC 2119)

All agent and skill files MUST use [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) terminology to define requirements and constraints.

| Term | Usage | Meaning |
|------|-------|---------|
| **MUST** | Absolute Requirement | This is an inviolable rule. Failure = Protocol Violation. |
| **MUST NOT** | Absolute Prohibition | Explicitly forbidden action. |
| **SHOULD** | Recommended | Strong suggestion, but valid reasons may exist to ignore it. |
| **SHOULD NOT** | Not Recommended | Action to avoid unless absolutely necessary. |
| **MAY** | Optional | Truly optional behavior or choice. |

### Examples:
- ✅ "You MUST read the agent file before implementation."
- ✅ "You MUST NOT write code in PLANNING mode."
- ✅ "You SHOULD ask clarifying questions if the request is vague."

---

## 2. Rule Hierarchy (P-Levels)

Rules are categorized by priority levels.

| Level | Scope | Reference |
|-------|-------|-----------|
| **P0** | Universal Rules | `GEMINI.md` |
| **P1** | Agent Persona | `agents/*.md` |
| **P2** | Skill Logic | `skills/*/SKILL.md` |

**Conflict resolution**: If rules conflict, P0 > P1 > P2.

---

## 3. Visual Style

### Emojis
Use emojis as **thematic markers**, not as replacements for priority text.

- 🤖 - Agent/AI behavior
- 🛠️ - Tools/Setup
- 🧹 - Clean Code
- ⚠️ - Warnings (informational)
- 🛑 - Gates/Stops
- ✅/❌ - Success/Failure indicators

### Red Circle (🔴)
Do NOT use the red circle emoji (🔴) as a marker for "MANDATORY". Use the word **MUST** or **REQUIRED** instead.
- ❌ `🔴 MANDATORY: Do X`
- ✅ `**Requirement:** You MUST do X`

---

## 4. Documentation Structure

### Agent Files
1. **Frontmatter** (name, description, tools, skills)
2. **Terminology Reference** (link to RFC 2119)
3. **Philosophy/Mindset**
4. **Decision Process** (Phases)
5. **Expertise Areas**
6. **Checklists** (Review/Verification)

### Skill Files
1. **Frontmatter**
2. **Core Principle**
3. **Implementation Patterns** (Code blocks)
4. **Anti-Patterns**
5. **Verification Scripts**

---

## 5. Proactivity vs. Restraint

1. **Be Proactive**: Fulfill the user's request thoroughly, including implied follow-ups.
2. **Use the Socratic Gate**: For complex/vague tasks, always ASK before acting.
3. **Clean Code**: Never sacrifice quality for speed. Follow the `clean-code` skill.
