import heapq

# 정점 리스트
vertex = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

# 인접 행렬 (None은 연결되지 않음을 의미)
weight = [
    [None, 29, None, None, None, 10, None],  # A
    [29, None, 16, None, None, None, 15],  # B
    [None, 16, None, 12, None, None, None],  # C
    [None, None, 12, None, 22, None, 18],  # D
    [None, None, None, 22, None, 27, 25],  # E
    [10, None, None, None, 27, None, None],  # F
    [None, 15, None, 18, 25, None, None]  # G
]

def prim(vertex, weight):
    n = len(vertex)

    # 최소 신장 트리
    mst = []
    total_weight = 0
    visited = [False] * n
    # A 정점 = 0, 0, -1
    # (가중치, 현재 정점, 이전 정점)
    min_heap = [(0, 0, -1)]

    while min_heap:
        w, u, prev = heapq.heappop(min_heap)

        if visited[u]:
            continue

        visited[u] = True
        total_weight += w

        # MST에 간선 정보 추가 (시작 정점 제외)
        if prev != -1:
            mst.append((vertex[prev], vertex[u], w))
            print(f"선택된 간선: {vertex[prev]} - {vertex[u]}, 간선의 가중치: {w}, 총 가중치: {total_weight}")

        # 인접 행렬에서 연결된 정점 찾기
        for v in range(n):
            if weight[u][v] is not None and not visited[v]:
                heapq.heappush(min_heap, (weight[u][v], v, u))

    return total_weight, mst

# 실행
total, mst_edges = prim(vertex, weight)

# 파이썬 heapq는 튜플의 가장 첫번째 요소 순로 가장 작은 값을 찾음