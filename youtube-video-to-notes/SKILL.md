---
name: youtube-video-to-notes
description: Turn a YouTube video into short, timestamped notes from its transcript, with key ideas, tools mentioned, steps to copy and what to verify. Use when the user shares a YouTube link and asks to summarize it, take notes, extract the steps or tools, or compare several videos.
---

# YouTube video to notes

Notes that save watching time and can be checked against the video.

## When to use
- A YouTube link plus "summarize", "notes", "what tools does he use", "what can I apply", or a list of videos to compare.

## Inputs
- The video link(s). Optional: the user's goal (what they want to apply).

## Steps
1. **Get the transcript and metadata** (title, channel, date, length) with whatever YouTube or transcript tool is available. If no transcript is available, say so and work from the description only, marked as such.
2. **Skim for structure.** Find the sections and their timestamps.
3. **Extract**: the main claims, each with a timestamp; tools, products and links named; any step-by-step process.
4. **Separate** what the creator shows working on screen from opinion or sponsor content.
5. **Apply**: 3 to 5 things the user could do, tied to their goal if given.
6. **For several videos**, add a short table: idea | who says it | timestamp, and note where they agree or differ.

## Output format
```
<Title>, <channel>, <date>, <length>  <link>
In one line: ...
Key points:
- [mm:ss] ...
Tools mentioned: ...
Steps to copy: 1. ... 2. ...
Worth verifying: ...
```
Under 40 lines per video.

## Guardrails
- Every point needs a timestamp. Don't add points the video doesn't make.
- Flag sponsored segments and paid courses or communities as such.
- Check product features against official docs before recommending them.
