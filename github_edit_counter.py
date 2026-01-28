import requests
import time

# 토큰, 본인 정보
TOKEN = ""
USERNAME = ""

headers = {"Authorization": f"token {TOKEN}"}


def get_repos_user(username):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/user/repos?per_page=100&page={page}&affiliation=owner"
        r = requests.get(url, headers=headers)
        data = r.json()
        if not data or "message" in data:
            break
        repos.extend([repo["full_name"] for repo in data])
        page += 1
    return repos


def get_orgs():
    orgs = []
    page = 1
    while True:
        url = f"https://api.github.com/user/orgs?per_page=100&page={page}"
        r = requests.get(url, headers=headers)
        data = r.json()
        if not data or "message" in data:
            break
        orgs.extend([org["login"] for org in data])
        page += 1
    return orgs


def get_repos_org(org):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
        r = requests.get(url, headers=headers)
        data = r.json()
        if not data or "message" in data:
            break
        repos.extend([repo["full_name"] for repo in data])
        page += 1
    return repos


def get_commit_contributions(username, full_repo):
    added, deleted = 0, 0
    page = 1
    while True:
        url = f"https://api.github.com/repos/{full_repo}/commits?author={username}&per_page=100&page={page}"
        r = requests.get(url, headers=headers)
        data = r.json()

        if not data or "message" in data:
            break

        for commit in data:
            sha = commit["sha"]
            commit_url = f"https://api.github.com/repos/{full_repo}/commits/{sha}"
            c = requests.get(commit_url, headers=headers).json()
            if "files" in c:
                for f in c["files"]:
                    added += f.get("additions", 0)
                    deleted += f.get("deletions", 0)

            time.sleep(0.2)

        page += 1

    return added, deleted


if __name__ == "__main__":
    repos = []

    # 내 개인 레포
    repos.extend(get_repos_user(USERNAME))

    # 내가 속한 모든 org
    orgs = get_orgs()
    for org in orgs:
        repos.extend(get_repos_org(org))

    # 집계
    total_added, total_deleted = 0, 0
    for repo in repos:
        a, d = get_commit_contributions(USERNAME, repo)
        total_added += a
        total_deleted += d
        print(f"{repo}: +{a} / -{d}")

    print("=" * 40)
    print(f"총합: 추가 {total_added}, 삭제 {total_deleted}, 전체 변화 {total_added + total_deleted}")
