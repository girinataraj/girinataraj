# Cinematic GitHub profile — finishing kit

This branch replaces the restrained first draft with an illustrated developer identity, technical dossier, technology logos, five projects, a journey section, real GitHub telemetry and a contribution calendar. The live profile changes when merged into main.

## Content evidence

Degree, institution, location, internship and early project details come from the public résumé at `girinataraj/Resume-RAG-Application/python-server/app/data/resume.txt`. These are self-reported details. The other portfolio's sample education/employment entries were not used. No phone number, GPA, client success percentage or unverifiable business impact is added.

Flagship summaries were checked against READMEs and selected code. Résumé RAG's chain/retriever implementation and Crown Dental's React App were inspected. The summaries do not assert hosted availability. Silex is a fork and is not presented as an original build.

## Suggested account bio and pins

Bio: Full-stack developer exploring applied AI. React, TypeScript, Python & C#. Building useful interfaces and the systems behind them. Erode, India.

Suggested pin order:

1. QueueLess-Pulse
2. closefuture-agent
3. sacred-commerce
4. Resume-RAG-Application
5. Crown-Dental-Clinic

Bio, native pins and other repositories' descriptions are not edited by this branch. Add clear root READMEs to Résumé RAG and Crown Dental before treating all five pins as a finished storefront.

Pinning: profile → Customize your pins → select and reorder → Save pins. GitHub supports up to six repositories/gists. [Official instructions](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile).

## Links

Both www.girinataraj.tech and girinataraj.tech failed DNS checks. The main link leads to Selected work. Restore the portfolio link when healthy. LinkedIn is preserved from the original README; automated access returns HTTP 999, so its destination content could not be independently checked.

## Live visuals

- Refresh: daily at 03:23 UTC / 08:53 Asia/Calcutta, or manually. Schedules start after merge to the default branch and may be delayed by GitHub.
- `activity.svg`: three latest original public project pushes, excluding forks, archives and the profile repository.
- `github-dashboard.svg`: original public project repositories, active days in the past 365 days, and repositories grouped by GitHub's primary-language metadata. Bars do not measure proficiency or source-byte percentages.
- `contributions.svg`: actual public profile calendar intensity. The public calendar can include anonymized private activity if the account owner enables it. No private repository details are requested.
- Calendar HTML is an undocumented GitHub presentation surface. Missing/incomplete/invalid markup fails the job and preserves the previous visuals. All fetches and rendering finish before files are replaced.
- The refresh workflow stages only these three generated SVGs. Repository rules may block bot pushes; no rule is bypassed.
- Uses Python's standard library and the automatic Actions token. No personal token or paid service is required. Calendar requests send no authorization or cookies.
- Pull-request checks run eleven tests and parse all SVG assets. Tests cover filtering, escaping, calendar completeness, source-failure preservation, animation coverage and actual encoded GIF frame durations.

## Visual maintenance

The hero is an original fictional illustrated developer mascot, not an identity-matched portrait. Its displayed version is now a continuously looping 48-frame GIF with portrait parallax, holographic HUD motion, particles and typing titles. All displayed visual assets animate; native prose and table content stay readable. See `MOTION.md` for the complete motion inventory and verification. Provenance and the original generation prompt are in `ASSETS.md`. Technology logos are local animated SVG wrappers retaining Devicon's original paths and license.

Edit `README.md` for content. Displayed graphics are animated SVGs and GIFs; the original hero PNG remains an authoring source only. The local HTML preview approximates GitHub; inspect the branch README before merge. No arbitrary scripts/styles are required inside the README, and no repositories are renamed, archived or deleted.
