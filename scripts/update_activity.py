"""Build a profile card from public repository metadata. Python standard library only."""
from datetime import datetime, timezone, date, timedelta
from collections import Counter
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import urllib.request

OWNER = 'girinataraj'
ROOT = Path(__file__).resolve().parents[1]


def with_motion(svg, kind):
    """Keep motion in every generated snapshot without changing source data."""
    style = '''<style>
@keyframes trace{to{stroke-dashoffset:-1200}}
@keyframes breathe{0%,100%{opacity:.35}50%{opacity:1}}
@keyframes fillbar{0%,8%{transform:scaleX(.15)}55%,92%{transform:scaleX(1)}100%{transform:scaleX(.15)}}
.moving-rule{stroke-dasharray:180 1020;animation:trace 7s linear infinite}
.activity-dot{animation:breathe 3s ease-in-out infinite}
.telemetry-bar{transform-box:fill-box;transform-origin:left;animation:fillbar 8s ease-in-out infinite}
@media(prefers-reduced-motion:reduce){.moving-rule,.activity-dot,.telemetry-bar{animation:none}}
</style>'''
    extras = '<path class="moving-rule" d="M0 2H1200" stroke="#67e8ee" stroke-width="3"/>'
    if kind == 'calendar':
        extras += '''<path d="M48 71V222" stroke="#b2ffff" stroke-opacity=".65" stroke-width="2"><animateTransform attributeName="transform" type="translate" from="0 0" to="1075 0" dur="12s" repeatCount="indefinite"/></path>'''
    svg = svg.replace('>', '>' + style, 1)
    return svg.replace('</svg>', extras + '</svg>')


def fetch_repositories():
    records = []
    # This endpoint returns public repositories only, even when authenticated.
    for page in range(1, 11):
        url = f'https://api.github.com/users/{OWNER}/repos?type=owner&sort=pushed&per_page=100&page={page}'
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'girinataraj-profile'}
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = f'Bearer {token}'
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError('GitHub did not return a repository list')
        records.extend(batch)
        if len(batch) < 100:
            return records
    raise ValueError('Pagination limit reached; keeping the previous card')


def select_repositories(records):
    eligible = [r for r in records if not any(r.get(k, False) for k in ('private', 'fork', 'archived'))
                and r.get('name') != OWNER and r.get('pushed_at')]
    return sorted(eligible, key=lambda r: r['pushed_at'], reverse=True)[:3]


def render_card(records, checked):
    rows = []
    for i, repo in enumerate(records):
        y = 148 + i * 76
        name = repo['name']
        label = name if len(name) <= 39 else name[:36] + '...'
        day = datetime.fromisoformat(repo['pushed_at'].replace('Z', '+00:00')).date().isoformat()
        rows.append(f'''<path d="M42 {y+25}H1158" stroke="#292b2c"/>
<circle class="activity-dot" cx="49" cy="{y-8}" r="4" fill="#4de0e6"/>
<text x="70" y="{y}" fill="#f3eee4" font-size="27">{escape(label)}</text>
<text x="1156" y="{y}" fill="#acb1ac" font-size="21" text-anchor="end">{day}</text>''')
    if not rows:
        rows.append('<text x="42" y="160" fill="#c9cbc5" font-size="26">No public project pushes to show yet.</text>')
    return with_motion(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="380" viewBox="0 0 1200 380" role="img" aria-labelledby="title desc">
<title id="title">From the workshop: latest public project pushes</title>
<desc id="desc">Public, original, non-archived repositories. Dates are last code pushes in UTC. Checked {escape(checked)}.</desc>
<rect width="1200" height="380" rx="20" fill="#0b1624"/>
<g font-family="Consolas, Liberation Mono, monospace">
<text x="42" y="49" fill="#6ee6ec" font-size="17" letter-spacing="3">RECENT TRANSMISSIONS</text>
<text x="42" y="88" fill="#f3eee4" font-size="29">Latest public code pushes</text>
<text x="1156" y="83" fill="#acb1ac" font-size="17" text-anchor="end">UTC</text>
{''.join(rows)}
<text x="42" y="350" fill="#acb1ac" font-size="17">GitHub public repository data / checked {escape(checked)}</text>
</g></svg>
''', 'activity')


def update(path, fetch=fetch_repositories):
    selected = select_repositories(fetch())
    svg = render_card(selected, datetime.now(timezone.utc).date().isoformat())
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(svg, encoding='utf-8', newline='\n')
    temporary.replace(path)
    return selected


def parse_calendar(html):
    class Calendar(HTMLParser):
        def __init__(self):
            super().__init__()
            self.days = {}

        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            if tag == 'td' and 'data-date' in values and 'data-level' in values:
                day = date.fromisoformat(values['data-date']).isoformat()
                level = int(values['data-level'])
                if level not in range(5):
                    raise ValueError('Invalid GitHub calendar intensity')
                self.days[day] = level

    parser = Calendar()
    parser.feed(html)
    if not parser.days:
        raise ValueError('GitHub contribution calendar was unavailable or its markup changed')
    return sorted(parser.days.items())


def fetch_calendar():
    # Public HTML only; no cookies or authorization are sent to this endpoint.
    request = urllib.request.Request(f'https://github.com/users/{OWNER}/contributions',
                                     headers={'User-Agent': 'girinataraj-profile'})
    with urllib.request.urlopen(request, timeout=30) as response:
        days = parse_calendar(response.read().decode('utf-8'))
    validate_calendar(days, datetime.now(timezone.utc).date().isoformat())
    return days


def calendar_window(days, checked):
    today = date.fromisoformat(checked)
    return [(day, level) for day, level in days
            if today - timedelta(days=364) <= date.fromisoformat(day) <= today]


def validate_calendar(days, checked):
    today = date.fromisoformat(checked)
    expected = {(today-timedelta(days=i)).isoformat() for i in range(365)}
    actual = {day for day, _ in calendar_window(days, checked)}
    if actual != expected:
        raise ValueError('Incomplete public calendar; keeping previous visuals')


def render_dashboard(records, days, checked):
    original = [r for r in records if not any(r.get(k, False) for k in ('private', 'fork', 'archived'))
                and r.get('name') != OWNER]
    active = sum(level > 0 for _, level in calendar_window(days, checked))
    languages = Counter(r['language'] for r in original if r.get('language')).most_common(4)
    bars = []
    maximum = max((count for _, count in languages), default=1)
    colors = ['#65e7e6', '#64aaff', '#b3a0f4', '#f0b17b']
    for i, (language, count) in enumerate(languages):
        y = 130 + i * 50
        bars.append(f'<text x="680" y="{y}" fill="#d9e5f0" font-size="20">{escape(language)}</text>'
                    f'<rect x="820" y="{y-16}" width="280" height="12" rx="6" fill="#1b2a3d"/>'
                    f'<rect class="telemetry-bar" x="820" y="{y-16}" width="{280*count/maximum:.1f}" height="12" rx="6" fill="{colors[i]}"/>'
                    f'<text x="1145" y="{y}" fill="#b4c6d7" font-size="20" text-anchor="end">{count}</text>')
    return with_motion(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360" viewBox="0 0 1200 360" role="img" aria-labelledby="title desc">
<title id="title">GitHub engineering telemetry</title><desc id="desc">{len(original)} original public repository entries; {active} active day entries in the last 365 days. Bars count original project repositories by their primary language, not proficiency.</desc>
<rect width="1200" height="360" rx="20" fill="#0b1624" stroke="#25415a"/>
<g font-family="Consolas, Liberation Mono, monospace">
<text x="36" y="46" fill="#67e8ee" font-size="17" letter-spacing="3">ENGINEERING TELEMETRY</text>
<text x="1160" y="46" fill="#99adc3" font-size="16" text-anchor="end">CHECKED / {escape(checked)} UTC</text>
<rect x="35" y="80" width="275" height="211" rx="14" fill="#102235" stroke="#29465c"/>
<rect x="329" y="80" width="275" height="211" rx="14" fill="#102235" stroke="#29465c"/>
<text x="59" y="170" fill="#e6f7ff" font-size="70" font-weight="700">{len(original):02}</text>
<text x="59" y="218" fill="#8eb2d0" font-size="20">ORIGINAL PUBLIC</text><text x="59" y="246" fill="#8eb2d0" font-size="20">PROJECT REPOS</text>
<text x="353" y="170" fill="#67e8ee" font-size="70" font-weight="700">{active:02}</text>
<text x="353" y="218" fill="#8eb2d0" font-size="20">ACTIVE DAYS</text><text x="353" y="246" fill="#8eb2d0" font-size="20">PAST 365 DAYS</text>
<text x="680" y="87" fill="#8eb2d0" font-size="17">REPOS BY PRIMARY LANGUAGE</text>{''.join(bars)}
<text x="36" y="331" fill="#90a8bc" font-size="16">GitHub public metadata + public profile calendar / forks, archives and profile repo excluded from project counts</text>
</g></svg>''', 'telemetry')


def render_contributions(days, checked):
    days = calendar_window(days, checked)
    if not days:
        raise ValueError('No current calendar dates found')
    start = date.fromisoformat(days[0][0])
    start -= timedelta(days=(start.weekday()+1) % 7)
    colors = ['#132638', '#1a455c', '#246f8a', '#2aa9b7', '#68e8e4']
    cells = []
    for day, level in days:
        offset = (date.fromisoformat(day)-start).days
        x, y = 58 + (offset//7)*20, 79 + (offset % 7)*20
        cells.append(f'<rect x="{x}" y="{y}" width="15" height="15" rx="3" fill="{colors[level]}"><title>{day}: GitHub intensity {level} of 4</title></rect>')
    active = sum(level > 0 for _, level in days)
    return with_motion(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="270" viewBox="0 0 1200 270" role="img" aria-labelledby="title desc">
<title id="title">The commit trail: GitHub profile activity</title><desc id="desc">{active} active days in the past 365 days. Actual public GitHub profile contribution intensity, not a synthetic pattern.</desc>
<rect width="1200" height="270" rx="20" fill="#08131f" stroke="#25415a"/>
<g font-family="Consolas, Liberation Mono, monospace"><text x="35" y="43" font-size="18" letter-spacing="3" fill="#67e8ee">THE COMMIT TRAIL</text>
<text x="1160" y="43" font-size="17" fill="#a6bfd2" text-anchor="end">{active} ACTIVE DAYS / PAST 365 DAYS</text>
{''.join(cells)}
<text x="35" y="246" font-size="16" fill="#90a8bc">PUBLIC PROFILE CALENDAR / {days[0][0]} → {days[-1][0]}</text>
<text x="905" y="246" fill="#90a8bc" font-size="15">LESS</text>
{''.join(f'<rect x="{955+i*22}" y="232" width="15" height="15" rx="3" fill="{color}"/>' for i,color in enumerate(colors))}
<text x="1080" y="246" fill="#90a8bc" font-size="15">MORE</text></g></svg>''', 'calendar')


def update_workshop(directory, fetch_repos=fetch_repositories, fetch_days=fetch_calendar):
    records, days = fetch_repos(), fetch_days()
    checked = datetime.now(timezone.utc).date().isoformat()
    cards = {'activity.svg': render_card(select_repositories(records), checked),
             'github-dashboard.svg': render_dashboard(records, days, checked),
             'contributions.svg': render_contributions(days, checked)}
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name, svg in cards.items():
        temporary = directory / (name + '.tmp')
        temporary.write_text(svg, encoding='utf-8', newline='\n')
        temporary.replace(directory / name)
    return len(cards)


if __name__ == '__main__':
    count = update_workshop(ROOT / 'assets')
    print(f'Updated {count} GitHub profile visuals from public data.')
