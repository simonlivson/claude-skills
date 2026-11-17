---
name: verified-social-reply
description: Draft a short reply to a post on X or LinkedIn after checking every fact against its source. Use when the user shares a post or thread and asks for a reply, comment, or quote post idea.
---

# Verified social reply

A reply that is short, natural and true. Checking comes before writing.

## When to use
- The user shares an X post, LinkedIn post, or thread (link or text) and asks what to reply or comment.

## Inputs
- The post text or link (required), plus the author's name and role if known.
- Any thread context or the article the post links to.
- The user's angle, if given (agree, add a data point, ask a question).

## Steps
1. **Read the source.** Open the post and anything it links to. Note the claim the post actually makes.
2. **Verify.** Every fact the reply would mention (numbers, dates, names, product features, the user's own results) must be confirmed in the source or in the user's own files. Keep numbers exactly as the source gives them.
3. **Decide whether to reply.** Skip and say why when the post is a rumor, the facts can't be confirmed, the topic is outside the user's experience, or a reply would only be praise with nothing to add.
4. **Pick one angle:** one real observation, one relevant result of the user's own, or one genuine question. Not all three.
5. **Draft.** X: under about 200 characters where possible. LinkedIn: 1 to 3 short sentences. Plain words, no hashtags unless asked, at most one emoji and usually none.
6. **Show the evidence.** Under the draft, list what was checked and where.

## Output format
```
Reply (draft):
<text>

Checked:
- <fact> : <source>

Skip?: no / yes, because <reason>
```

## Guardrails
- Draft only. Never post, like, follow or send. The user posts and clicks himself.
- No rumors, no claims that can't be verified, no invented experience.
- Not showy: no "Great post!", no buzzwords ("passionate", "game-changer"), no self-promotion beyond one honest relevant line.
- Nothing scheduled or posted from Friday sunset until Shabbat ends.
- When unsure, skip.
