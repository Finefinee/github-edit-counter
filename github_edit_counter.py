import requests
import time

# 토큰, 본인 정보
TOKEN = ""
USERNAME = ""

headers = {"Authorization": f"token {TOKEN}"}


def check_rate_limit():
    """현재 rate limit 상태를 확인하고 출력"""
    url = "https://api.github.com/rate_limit"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        core = data["resources"]["core"]
        remaining = core["remaining"]
        limit = core["limit"]
        reset_time = core["reset"]

        print(f"Rate Limit 상태: {remaining}/{limit} 남음")

        if remaining < 100:
            wait_time = reset_time - time.time()
            if wait_time > 0:
                print(f"[경고] Rate limit이 부족합니다 ({remaining}개 남음). {int(wait_time)}초 후 초기화됩니다.")
                response = input("계속 진행하시겠습니까? (y/n): ")
                if response.lower() != 'y':
                    print("프로그램을 종료합니다.")
                    exit(0)
        return remaining
    else:
        print("[경고] Rate limit 확인 실패")
        return None


def get_repos_user(username):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/user/repos?per_page=100&page={page}&affiliation=owner"
        r = requests.get(url, headers=headers)

        # Rate limit 체크
        if r.status_code == 403:
            print(f"  [경고] Rate limit 도달. 60초 대기 중...")
            time.sleep(60)
            continue

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

        # Rate limit 체크
        if r.status_code == 403:
            print(f"  [경고] Rate limit 도달. 60초 대기 중...")
            time.sleep(60)
            continue

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

        # Rate limit 체크
        if r.status_code == 403:
            print(f"  [경고] Rate limit 도달. 60초 대기 중...")
            time.sleep(60)
            continue

        data = r.json()
        if not data or "message" in data:
            break
        repos.extend([repo["full_name"] for repo in data])
        page += 1
    return repos


def get_commit_contributions(username, full_repo):
    """GitHub의 contributor stats API를 사용하여 정확한 통계 가져오기"""
    url = f"https://api.github.com/repos/{full_repo}/stats/contributors"

    # Contributor stats API는 계산에 시간이 걸릴 수 있어 최대 10번 재시도
    max_retries = 10
    wait_time = 3  # 초기 대기 시간

    for attempt in range(max_retries):
        r = requests.get(url, headers=headers)

        # Rate limit 체크
        if r.status_code == 403:
            print(f"  [경고] Rate limit 도달. 60초 대기 중...")
            time.sleep(60)
            continue

        # 202는 통계를 계산 중이라는 의미, 대기 후 재시도
        if r.status_code == 202:
            if attempt == 0:
                print(f"  [정보] 통계 계산 중... (대기 시간: {wait_time}초)")
            else:
                print(f"  [정보] 재시도 중... ({attempt + 1}/{max_retries}, 대기: {wait_time}초)")
            time.sleep(wait_time)
            # 대기 시간을 점진적으로 늘림 (최대 10초)
            wait_time = min(wait_time + 1, 10)
            continue

        # 204는 빈 레포지토리 또는 커밋 없음
        if r.status_code == 204:
            return 0, 0

        if r.status_code != 200:
            print(f"  [경고] {full_repo}: contributor stats 조회 실패 (status: {r.status_code})")
            return 0, 0

        data = r.json()

        # data가 리스트가 아닌 경우 (에러 메시지 등)
        if not isinstance(data, list):
            print(f"  [경고] {full_repo}: 잘못된 응답 형식")
            return 0, 0

        # 해당 사용자의 통계 찾기
        for contributor in data:
            if contributor.get("author") and contributor["author"]["login"].lower() == username.lower():
                # 모든 주차별 통계 합산
                total_added = 0
                total_deleted = 0
                commit_count = 0

                for week in contributor.get("weeks", []):
                    total_added += week.get("a", 0)  # additions
                    total_deleted += week.get("d", 0)  # deletions
                    commit_count += week.get("c", 0)  # commits

                if commit_count > 0:
                    print(f"  [정보] {commit_count}개 커밋 발견")

                return total_added, total_deleted

        # 해당 사용자를 찾지 못한 경우
        return 0, 0

    print(f"  [경고] {full_repo}: 통계 계산 시간 초과 (최대 재시도 횟수 도달)")
    return 0, 0


if __name__ == "__main__":
    print("=" * 60)
    print("GitHub 편집 기여도 분석 시작")
    print("=" * 60)

    # 시작 시 rate limit 확인
    print("\nRate Limit 확인 중...")
    check_rate_limit()
    print()

    repos = []

    print("레포지토리 목록 가져오는 중...")

    # 내 개인 레포
    user_repos = get_repos_user(USERNAME)
    repos.extend(user_repos)
    print(f"개인 레포: {len(user_repos)}개")

    # 내가 속한 모든 org
    orgs = get_orgs()
    print(f"조직: {len(orgs)}개")
    for org in orgs:
        org_repos = get_repos_org(org)
        repos.extend(org_repos)
        print(f"  - {org}: {len(org_repos)}개 레포")

    print(f"\n총 {len(repos)}개 레포지토리 분석 시작...\n")

    # 집계
    total_added, total_deleted = 0, 0
    for idx, repo in enumerate(repos, 1):
        print(f"[{idx}/{len(repos)}] {repo} 분석 중...")
        try:
            a, d = get_commit_contributions(USERNAME, repo)
            total_added += a
            total_deleted += d
            if a > 0 or d > 0:
                print(f"  결과: +{a} / -{d}")
            else:
                print(f"  결과: 기여 없음")
        except Exception as e:
            print(f"  [에러] {repo}: {str(e)}")
            continue

    print("\n" + "=" * 60)
    print(f"총합: 추가 {total_added:,}, 삭제 {total_deleted:,}, 전체 변화 {total_added + total_deleted:,}")
