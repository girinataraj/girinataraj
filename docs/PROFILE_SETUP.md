# Profile finishing kit

The README and its original SVG artwork are ready in this repository. The proposed branch does not change the live profile until merged into main. LinkedIn was preserved from the original README. Both www.girinataraj.tech and girinataraj.tech failed DNS resolution during verification, so the main link leads to Selected builds instead. Restore the portfolio link after the domain works. LinkedIn returned its usual automated-access block (HTTP 999), so its page content was not independently verified.

## Suggested account bio

Full-stack developer building thoughtful interfaces, reliable workflows, and applied AI. React · TypeScript · Python · PostgreSQL.

This is proposed copy, not a claim that the account bio has been changed.

## Suggested pins, in order

1. QueueLess-Pulse — strongest connected product workflow and backend story.
2. closefuture-agent — AI retrieval, orchestration and MCP case study.
3. sacred-commerce — editorial UI and product ownership case study.

Three intentional pins are enough for this first version. Add further projects when they have a clear README, visuals and an understandable entry point. Silex is a fork of silexlabs/Silex; it is not presented as an original build. Resume-RAG-Application and ERP lacked a root README.md during this audit, so they are not featured yet. No repositories were deleted, archived or renamed.

To apply pins: profile → Customize your pins → select these repositories → reorder → Save pins. GitHub supports up to six pinned repositories and gists combined. Source: https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile

## Suggested repository descriptions and topics

| Repository | Description | Topics |
| --- | --- | --- |
| QueueLess-Pulse | Virtual queue platform with customer, staff, owner and reception workflows. React, Flask and PostgreSQL. | queue-management, react, typescript, flask, postgresql |
| closefuture-agent | AI assistant case study with grounded retrieval, intent routing, calendar scheduling and MCP tools. | rag, ai-agents, mcp, typescript, pgvector |
| sacred-commerce | Independent fictional commerce demo and product ownership case study. Editorial design, accessible shopping and simulated checkout. | nextjs, typescript, ecommerce-demo, accessibility, product-management |

These are prepared suggestions. Account bio, native pins and other repositories' metadata have not been edited by this branch.

## Activity automation

- `.github/workflows/profile-activity.yml` runs daily at 03:23 UTC / 08:53 Asia/Calcutta and can be run manually.
- Scheduled workflows begin after the workflow is on the default branch. The initial activity snapshot is included so the image works immediately.
- Python uses the GitHub public-user repositories endpoint, filters out forks/private/archived repos and this profile, and shows the three latest `pushed_at` dates.
- Only `assets/activity.svg` is generated. Failed fetches leave the previous card intact and fail the workflow visibly.
- The included workflow uses the automatic repository token; no personal token or paid service is required. GitHub repository rules may prevent bot pushes. If that happens, keep the last good card and adjust repository rules deliberately.
- The artwork is local, script-free SVG. Hero motion finishes after eight seconds and respects reduced-motion settings. The static composition works without animation.
- The layout uses standard GitHub Markdown and supported HTML. Local HTML previews approximate GitHub; the branch README is the canonical render to inspect before merging.

## Updating the profile

Edit `README.md` for text and links. Edit `assets/*.svg` for visuals. Keep project claims aligned with the repositories. The feature cards are original diagrams, not screenshots; the expandable QueueLess preview uses an actual screenshot already published in that project.

## Verification

Run `python -m unittest discover -s tests -v` to check filtering, XML escaping, empty results, and preservation of the last good card on a fetch error. Run `python scripts/update_activity.py` for a fresh public snapshot. Neither command publishes posts or changes other repositories.
