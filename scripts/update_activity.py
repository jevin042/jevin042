"""Refresh a self-hosted SVG using only public GitHub repository metrics."""
import os, json, urllib.request, datetime, html
from pathlib import Path
from collections import Counter

def request(path):
    headers={'User-Agent':'jevin042-profile', 'Accept':'application/vnd.github+json'}
    if os.getenv('GITHUB_TOKEN'):
        headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
    with urllib.request.urlopen(urllib.request.Request('https://api.github.com/'+path,headers=headers),timeout=30) as result:
        return json.load(result)

repos=[]
page=1
while True:
    batch=request(f'users/jevin042/repos?per_page=100&page={page}')
    repos.extend(repo for repo in batch if not repo['private'])
    if len(batch)<100: break
    page+=1
languages=Counter(repo['language'] for repo in repos if repo['language'] and not repo['fork'])
stars=sum(repo['stargazers_count'] for repo in repos)
text=''
for x,number,label in [(38,len(repos),'PUBLIC REPOSITORIES'),(335,stars,'STARS RECEIVED'),(630,len(languages),'PRIMARY LANGUAGES')]:
    text+=f'<text x="{x}" y="112" fill="#f4f8ff" font-size="49" font-weight="750">{number:02d}</text><text x="{x}" y="143" fill="#839bbc" font-size="11" letter-spacing="2">{label}</text>'
colors=['#438dff','#72c8ff','#ab9dff','#ff6580','#68d7a4']
total=sum(languages.values()) or 1
x=38
for index,(language,count) in enumerate(languages.most_common()):
    width=count/total*1124
    text+=f'<rect x="{x:.1f}" y="180" width="{width:.1f}" height="8" fill="{colors[index%len(colors)]}"/>'
    x+=width
x=38
for index,(language,count) in enumerate(languages.most_common(5)):
    text+=f'<circle cx="{x}" cy="214" r="4" fill="{colors[index%len(colors)]}"/><text x="{x+13}" y="218" fill="#b8c8e0" font-size="13">{html.escape(language)} · {count} repos</text>'
    x+=225
date=datetime.datetime.now(datetime.timezone.utc).strftime('%d %b %Y')
result=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="270" viewBox="0 0 1200 270" role="img"><title>Public GitHub activity for jevin042</title><rect width="1200" height="270" rx="18" fill="#0c1529"/><g font-family="Segoe UI,Arial,sans-serif"><text x="38" y="37" fill="#79b9ff" font-size="11" letter-spacing="2">PUBLIC WORK / LIVE REPOSITORY METRICS</text>{text}<text x="38" y="251" fill="#627b9e" font-size="11">Updated {date} UTC · Primary language per non-fork repository · Source: GitHub API</text></g></svg>'''
target=Path(__file__).resolve().parent.parent/'assets/activity.svg'
target.write_text(result,encoding='utf-8')
print(f'Updated activity: {len(repos)} public repositories, {stars} stars.')
