"""Build a profile card from public repository metadata. Python standard library only."""
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import urllib.request

OWNER = 'girinataraj'
ROOT = Path(__file__).resolve().parents[1]


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
<circle cx="49" cy="{y-8}" r="4" fill="#ff7448"/>
<text x="70" y="{y}" fill="#f3eee4" font-size="27">{escape(label)}</text>
<text x="1156" y="{y}" fill="#acb1ac" font-size="21" text-anchor="end">{day}</text>''')
    if not rows:
        rows.append('<text x="42" y="160" fill="#c9cbc5" font-size="26">No public project pushes to show yet.</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="380" viewBox="0 0 1200 380" role="img" aria-labelledby="title desc">
<title id="title">From the workshop: latest public project pushes</title>
<desc id="desc">Public, original, non-archived repositories. Dates are last code pushes in UTC. Checked {escape(checked)}.</desc>
<rect width="1200" height="380" rx="20" fill="#141617"/>
<g font-family="Consolas, Liberation Mono, monospace">
<text x="42" y="49" fill="#ff9c7b" font-size="17" letter-spacing="3">FROM THE WORKSHOP</text>
<text x="42" y="88" fill="#f3eee4" font-size="29">Latest public code pushes</text>
<text x="1156" y="83" fill="#acb1ac" font-size="17" text-anchor="end">UTC</text>
{''.join(rows)}
<text x="42" y="350" fill="#acb1ac" font-size="17">GitHub public repository data / checked {escape(checked)}</text>
</g></svg>
'''


def update(path, fetch=fetch_repositories):
    selected = select_repositories(fetch())
    svg = render_card(selected, datetime.now(timezone.utc).date().isoformat())
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(svg, encoding='utf-8', newline='\n')
    temporary.replace(path)
    return selected


if __name__ == '__main__':
    selected = update(ROOT / 'assets' / 'activity.svg')
    print(f'Updated public activity card with {len(selected)} repositories.')
