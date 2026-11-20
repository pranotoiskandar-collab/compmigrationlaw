# Follow-a-country alerts

Visitors choose countries on [/follow/](https://theimr.org/follow/). Each week, `alerts.py` lists what was added to the
databases for each country (laws and regulations, court decisions, dated changes) and prepares one short email per
country, in English and Indonesian. **Nothing is sent automatically.**

## How it runs

- **Every Monday, 03:30 Jakarta time**, the GitHub Action *Country alerts* runs `tools/alerts/alerts.py --since "7 days ago"`.
  The emails are attached to the run as an artifact (`country-alerts`).
- If the repository secret `BUTTONDOWN_API_KEY` exists, each email is also created in Buttondown as a **draft** titled
  `[country-XX] New for …`. A person opens it, sets the recipients to the tag `country-XX` (Buttondown → the draft →
  *Recipients* → filter by tag) and presses **Send**.
- Weeks with nothing new produce no drafts.

## Sign-up

- Until Buttondown is set up, the form on /follow/ is the Netlify form `follow-country` (addresses collect in Netlify →
  Forms, with the countries chosen).
- Once `buttondown_username` is filled in `tools/digest/config.json` (the monthly digest, PR #23) or in
  `tools/alerts/config.json`, the publish step writes it to `/features/alerts-config.json`, and the form posts to Buttondown
  with one tag per country (`country-ID`, `country-MY`, …) and a language tag (`lang-en` or `lang-id`). Buttondown sends
  the confirmation email (turn on double opt-in) and handles unsubscribing.
- When switching, import the Netlify sign-ups into Buttondown with their tags.

Only people who sign up themselves receive these emails. Never add addresses from anywhere else.
