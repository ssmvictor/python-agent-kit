---
description: Coordinate multiple agents for complex tasks. Use for multi-perspective analysis, comprehensive reviews, or tasks requiring different domain expertise.
---

# Multi-Agent Orchestration

> Terminology follows [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

You are now in **ORCHESTRATION MODE**. Your task: coordinate specialized agents to solve this complex problem.

## Task to Orchestrate
$ARGUMENTS

---

## Minimum Agent Requirement

> ⚠️ **ORCHESTRATION = MINIMUM 3 DIFFERENT AGENTS**
> 
> If you use fewer than 3 agents, you are NOT orchestrating - you're just delegating.
> 
> **Validation before completion:**
> - Count invoked agents
> - If `agent_count < 3` → STOP and invoke more agents
> - Single agent = FAILURE of orchestration

### Agent Selection Matrix

| Task Type | REQUIRED Agents (minimum) |
|-----------|---------------------------|
...
---

## Pre-Flight: Mode Check
...
---

## STRICT 2-PHASE ORCHESTRATION

### PHASE 1: PLANNING (Sequential - NO parallel agents)

| Step | Agent | Action |
|------|-------|--------|
| 1 | `project-planner` | Create docs/PLAN.md |
| 2 | (optional) `explorer-agent` | Codebase discovery if needed |

> **Requirement:** NO OTHER AGENTS during planning! Only project-planner and explorer-agent.

### ⏸️ CHECKPOINT: User Approval

```
After PLAN.md is complete, ASK:

"✅ Plan created: docs/PLAN.md

Do you approve? (Y/N)
- Y: Implementation starts
- N: I'll revise the plan"
```

> **Constraint:** You MUST NOT proceed to Phase 2 without explicit user approval!

### PHASE 2: IMPLEMENTATION (Parallel agents after approval)
...
---

## Orchestration Protocol

### Step 1: Analyze Task Domains
...
### Step 2: Phase Detection
...
### Step 3: Execute Based on Phase

**PHASE 1 (Planning):**
...
**PHASE 2 (Implementation - after approval):**
...
**CRITICAL: Context Passing**

When invoking ANY subagent, you MUST include:

1. **Original User Request:** Full text of what user asked
2. **Decisions Made:** All user answers to Socratic questions
3. **Previous Agent Work:** Summary of what previous agents did
4. **Current Plan State:** If plan files exist in workspace, include them

**Example with FULL context:**
...
> **VIOLATION:** Invoking subagent without full context = subagent will make wrong assumptions!


### Step 4: Verification
...
### Step 5: Synthesize Results
...
---

## Output Format
...
---

## EXIT GATE

Before completing orchestration, you MUST verify:

1. ✅ **Agent Count:** `invoked_agents >= 3`
2. ✅ **Scripts Executed:** At least `security_scan.py` ran
3. ✅ **Report Generated:** Orchestration Report with all agents listed

> **If any check fails → You MUST NOT mark orchestration complete. Invoke more agents or run scripts.**

---

**Begin orchestration now. Select 3+ agents, execute sequentially, run verification scripts, synthesize results.**

