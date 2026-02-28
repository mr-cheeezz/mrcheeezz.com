from .env import beta, branch, github_pat
import requests

main_ver = 4
sub_ver = 0
minor_ver = 0
def format_commit_info(branch_name, commit_sha, commit_message, commit_author, commit_date):
    commit_hash_short = commit_sha[:7]

    formatted_info = f"({branch_name}, {commit_hash_short}, commit {commit_message})"

    return formatted_info

def get_last_commit_info(owner='mr-cheeezz', repo='Website', branch='master'):
    api_url = f'https://api.github.com/repos/{owner}/{repo}/branches/{branch}'
    headers = {}
    if github_pat:
        headers['Authorization'] = f'token {github_pat}'

    try:
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None

        branch_info = response.json()
        commit_sha = branch_info['commit']['sha']
        commit_info = branch_info['commit']['commit']
        last_commit_message = commit_info['message']
        last_commit_author = commit_info['author']['name']
        last_commit_date = commit_info['author']['date']

        formatted_info = format_commit_info(branch, commit_sha, last_commit_message, last_commit_author, last_commit_date)
        return formatted_info
    except (requests.RequestException, KeyError, TypeError, ValueError):
        return None

last_commit_info = get_last_commit_info()

def format_version(ver):
    parts = ver.split('.')
    
    parts[-1] = parts[-1].rstrip('0')
    
    formatted_ver = '.'.join(parts)
    
    if not parts[-1]:
        formatted_ver = formatted_ver.rsplit('.', 1)[0]
    
    return formatted_ver

ver = f'{main_ver}.{sub_ver}.{minor_ver}'
basic_ver = format_version(ver)
_commit_suffix = f' {last_commit_info}' if last_commit_info else ''
beta_ver = f'Dev {basic_ver}{_commit_suffix}'
verbose_version = f'{basic_ver}{_commit_suffix}'

version = beta_ver if beta else basic_ver
