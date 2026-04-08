---
title: EmailOpsEnv
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 📧 EmailOpsEnv — Customer Support Operations Simulator

## 🚀 Overview

**EmailOpsEnv** is a realistic OpenEnv environment that simulates **customer support email operations**, a common real-world workflow.

Agents must:
- Classify emails (spam vs legitimate)
- Respond to customer queries
- Prioritize urgent requests
- Manage limited steps efficiently

This environment evaluates **decision-making, prioritization, and sequential reasoning** in AI agents.

---

## 🎯 Real-World Motivation

Customer support teams deal with:
- High email volumes
- Spam filtering
- Urgent complaints
- Limited response time

This environment models these challenges, making it useful for:
- Reinforcement learning benchmarks
- LLM agent evaluation
- Workflow automation systems

---

## 🧠 Environment Design

### Episode Rules
- Max **10 steps per episode**
- Agent processes emails one-by-one
- Episode ends when:
  - All emails handled OR
  - Step limit reached

---

## 📥 Observation Space

Each step returns:

```json
{
  "inbox": [
    {
      "id": "string",
      "subject": "string",
      "body": "string",
      "category": "spam | complaint | inquiry",
      "urgency": 1-5,
      "archived": false,
      "replied": false
    }
  ],
  "current_email_id": "string",
  "draft_response": "string",
  "echoed_message": "string"
}

## ⚙️ Action Space

At each step, the agent must return a JSON action:

```json
{
  "action_type": "archive | send_reply",
  "email_id": "string"
}