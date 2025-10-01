## CITS3200 Meeting Minutes — How to use this folder

This folder stores your team's meeting minutes in a source-controlled, easy-to-read format. Use the official CITS3200 template as a reference and keep a Markdown copy here for each meeting.

### Official UWA template
- Template page: [Template for Group Meeting Minutes](https://teaching.csse.uwa.edu.au/units/CITS3200/project/Minutes_GroupX_WkY.html)
- A local copy was downloaded to: `~/Downloads/CITS3200_GroupMeetingMinutesTemplate.html`

You can open the HTML in a browser and copy/paste into Word or Google Docs if required by assessors. For repository history and ease of diffing, keep the canonical minutes in Markdown in this folder.

### Recommended naming
- Repository copy (Markdown): `meeting_YYYY-MM-DD.md` (e.g., `meeting_2025-09-03.md`)
- Optional export for submission (if required): `Minutes_Group31_WkY.docx`

Examples already in this folder include `meeting_with_piers.txt`, `meeting5_w_auditor.txt`, and `meeting6.txt`.

### Minimum sections to include (aligns with the UWA template)
1. Title
2. Date/Time and Venue
3. Present / Apologies
4. Last Meeting Recap
5. Past Action Items (with status)
6. Discussion / New Meeting Points
7. Decisions Made
8. Action Items (owner and due date)
9. Next Meeting (date/time)

### Reusable Markdown template
Copy this into a new file (e.g., `meeting_YYYY-MM-DD.md`) and fill it in:

```markdown
# Meeting <number or short title>
Date/Time: <YYYY-MM-DD, HH:MM–HH:MM>
Venue: <location or call link>
Present: <names>
Apologies: <names or None>

## 1. Last Meeting Recap
<Brief recap of prior key items>

## 2. Past Action Items
- <Owner> — <action> — <status>
- <Owner> — <action> — <status>

## 3. Discussion / New Meeting Points
- <topic/point>
- <topic/point>

## 4. Decisions Made
- <decision>
- <decision>

## 5. Action Items
- <Owner> — <action> — Due: <YYYY-MM-DD>
- <Owner> — <action> — Due: <YYYY-MM-DD>

## 6. Next Meeting
Date/Time: <YYYY-MM-DD, HH:MM>
Venue: <location or call link>
```

### Tips
- Keep action items specific and assign a single owner with a due date.
- When exporting to `.docx` for submission, retain the Markdown copy in this repository for version control.
- Keep section headings consistent across meetings to simplify review and comparison.


