# map_direct_save.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque
import itertools
from utils import load_data, merge_data
from matplotlib.lines import Line2D
import math

# 애초에 도달 불가능한 경우 (건설현장으로 인해) -> 현재 bfs 알고리즘에 구현되어 있음.
#                                         -> 보너스 문제에서는 확인이 필요한 상태 -> 구현되어 있음

# My Home 없는 경우 -> main에서 예외 처리가 잘 되어있음
# My Home 여러 개인 경우 -> 성립이 안된다. -> 추가 완료 float('inf') 활용
# 반달곰 커피가 없는 경우 -> main에서 예외 처리가 잘 되어있음

def find_optimal_all_structures_path(my_home, all_structures, coffee_shops, area_1_data):
    """모든 구조물을 방문하고 가장 가까운 카페로 가는 최적 경로 찾기 (DP TSP)"""
    if not all_structures:
        print("방문할 구조물이 없습니다.")
        return []
    
    if not coffee_shops:
        print("카페가 없습니다.")
        return []
    
    # 각 지점 간의 최단 거리 계산
    all_points = [my_home] + all_structures + coffee_shops
    distances = {}
    paths = {}
    
    print("구조물 간 최단 거리 계산 중...")
    for i, start in enumerate(all_points):
        for j, end in enumerate(all_points):
            if i != j:
                path = bfs_shortest_path(start, [end], area_1_data)
                if path:
                    distances[(start, end)] = len(path) - 1
                    paths[(start, end)] = path
                else:
                    distances[(start, end)] = float('inf')
                    paths[(start, end)] = []
    
    # DP를 사용한 TSP 최적화
    def solve_tsp_dp(start, points, end_points):
        """DP를 사용한 TSP 해결"""
        n = len(points)
        if n == 0:
            return float('inf'), []
        
        # DP 테이블: dp[mask][pos] = 현재 위치가 pos이고 방문한 지점들이 mask일 때의 최단 거리
        dp = {}
        
        def get_min_distance(mask, pos):
            if (mask, pos) in dp:
                return dp[(mask, pos)]
            
            # 모든 지점을 방문했는지 확인
            if mask == (1 << n) - 1: # n개의 구조물을 모두 방문했다면 (=> n개의 비트가 전부 1인 상태)
                # 모든 구조물을 방문했으므로 가장 가까운 카페로 이동
                min_cafe_dist = float('inf')
                best_cafe = None
                for cafe in end_points:
                    if (points[pos], cafe) in distances:
                        if distances[(points[pos], cafe)] < min_cafe_dist:
                            min_cafe_dist = distances[(points[pos], cafe)]
                            best_cafe = cafe
                dp[(mask, pos)] = min_cafe_dist
                return min_cafe_dist
            
            # 모든 지점을 방문하지 않았다면
            # 현재 위치에서 방문하지 않은 지점들 중 하나를 선택
            min_dist = float('inf')
            for next_pos in range(n):
                if mask & (1 << next_pos) == 0:  # 아직 방문하지 않은 구조물(지점)이라면
                    if (points[pos], points[next_pos]) in distances:
                        dist = distances[(points[pos], points[next_pos])]
                        remaining_dist = get_min_distance(mask | (1 << next_pos), next_pos) # 재귀함수
                        # dist = 지금 위치 → 다음 위치까지 가는 거리
                        # remaining_dist = 다음 위치에서 시작해서, 나머지를 다 돌고 카페까지 가는 최단 거리
                        total_dist = dist + remaining_dist
                        if total_dist < min_dist:
                            min_dist = total_dist
            
            dp[(mask, pos)] = min_dist
            return min_dist
        
        # 시작점에서 시작
        # total_distance = get_min_distance(0, 0)  # 0번째 지점(시작점)에서 시작

        min_total_distance = float('inf')
        best_first_idx = None

        for first_idx in range(len(all_structures)):
            first_dist = distances[(my_home, all_structures[first_idx])]
            remaining_dist = get_min_distance(1 << first_idx, first_idx)
            total = first_dist + remaining_dist
    
            if total < min_total_distance:
                min_total_distance = total
                best_first_idx = first_idx
        
        if min_total_distance == float('inf'):
            return []
        
        # 경로 복원
        def reconstruct_path(mask, pos):
            if mask == (1 << n) - 1:
                # 모든 구조물을 방문했으므로 가장 가까운 카페로 이동
                min_cafe_dist = float('inf')
                best_cafe = None
                for cafe in end_points:
                    if (points[pos], cafe) in distances:
                        if distances[(points[pos], cafe)] < min_cafe_dist:
                            min_cafe_dist = distances[(points[pos], cafe)]
                            best_cafe = cafe
                return [best_cafe] if best_cafe else []
            
            # 다음 방문할 지점 찾기
            min_dist = float('inf')
            best_next = None
            for next_pos in range(n):
                if mask & (1 << next_pos) == 0:
                    if (points[pos], points[next_pos]) in distances:
                        dist = distances[(points[pos], points[next_pos])]
                        remaining_dist = get_min_distance(mask | (1 << next_pos), next_pos)
                        total_dist = dist + remaining_dist
                        if total_dist < min_dist:
                            min_dist = total_dist
                            best_next = next_pos
            
            if best_next is not None:
                return [points[best_next]] + reconstruct_path(mask | (1 << best_next), best_next)
            return []
        
        # 전체 경로 구성
        optimal_order = reconstruct_path(0, 0)
        
        # 경로를 실제 좌표로 변환
        full_path = []
        current = start
        
        for next_point in optimal_order:
            if (current, next_point) in paths:
                segment = paths[(current, next_point)]
                if full_path:  # 첫 번째가 아니면 시작점 제외
                    segment = segment[1:]
                full_path.extend(segment)
                current = next_point
        
        return full_path
    
    # 작은 수의 구조물에 대해서는 DP 사용
    if len(all_structures) <= 12:  # DP는 12개까지 효율적
        print(f"DP를 사용한 TSP 최적화 중... ({len(all_structures)}개 구조물)")
        path = solve_tsp_dp(my_home, all_structures, coffee_shops)
        return path
    else:
        # 많은 구조물의 경우 greedy 방법 사용
        print(f"Greedy 방법으로 경로 계산 중... ({len(all_structures)}개 구조물)")
        full_path = [my_home]
        current = my_home
        remaining = list(all_structures)
        
        while remaining:
            # 가장 가까운 구조물 찾기
            min_distance = float('inf')
            closest = None
            
            for structure in remaining:
                if (current, structure) in distances:
                    dist = distances[(current, structure)]
                    if dist < min_distance:
                        min_distance = dist
                        closest = structure
            
            if closest and (current, closest) in paths:
                segment = paths[(current, closest)][1:]  # 시작점 제외
                full_path.extend(segment)
                current = closest
                remaining.remove(closest)
            else:
                break
        
        # 마지막 구조물에서 가장 가까운 카페로 이동
        if full_path:
            last_structure = full_path[-1]
            min_cafe_distance = float('inf')
            closest_cafe = None
            
            for cafe in coffee_shops:
                if (last_structure, cafe) in distances:
                    dist = distances[(last_structure, cafe)]
                    if dist < min_cafe_distance:
                        min_cafe_distance = dist
                        closest_cafe = cafe
            
            if closest_cafe and (last_structure, closest_cafe) in paths:
                cafe_segment = paths[(last_structure, closest_cafe)][1:]
                full_path.extend(cafe_segment)
        
        return full_path

def find_positions(area_1_data):
    """내 집과 반달곰 커피 위치, 그리고 모든 구조물 위치를 찾는 함수"""
    my_home = None
    coffee_shops = []
    all_structures = []
    
    for _, row in area_1_data.iterrows():
        x, y = row['x'], row['y']
        struct_name = row['struct']
        category = row['category']
        
        if pd.notna(struct_name):
            if struct_name == 'MyHome':
                if my_home == None:
                    my_home = (x, y)
                else:
                    my_home = (-1, -1) # 수정 요청 (3) 반영 -> (-1, -1)로 설정 (이 값은 해당 데이터에서 불가능한 값이므로 이 값으로 설정) -> main 함수에서 예외처리
                    break # 수정 요청 (2) 반영 -> break로 바로 종료
            elif struct_name == 'BandalgomCoffee':
                coffee_shops.append((x, y))
        
        # Apartment(category=1)와 Building(category=2)만 포함
        if (pd.notna(category) and category in [1, 2] and 
            row['ConstructionSite'] != 1):
            all_structures.append((x, y))
    
    return my_home, coffee_shops, all_structures

def is_valid_position(x, y, area_1_data):
    """해당 위치가 이동 가능한지 확인하는 함수"""
    # 지도 범위 내에 있는지 확인
    if x < area_1_data['x'].min() or x > area_1_data['x'].max():
        return False
    if y < area_1_data['y'].min() or y > area_1_data['y'].max():
        return False
    
    # 건설현장이 있는지 확인
    position_data = area_1_data[(area_1_data['x'] == x) & (area_1_data['y'] == y)]
    if not position_data.empty and position_data.iloc[0]['ConstructionSite'] == 1:
        return False
    
    return True

def bfs_shortest_path(start, end, area_1_data):
    """BFS를 사용한 최단 경로 탐색"""
    if start == end:
        return [start]
    
    queue = deque([(start, [start])])
    visited = {start}
    
    # 상하좌우 이동
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    while queue:
        (x, y), path = queue.popleft()
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            if (nx, ny) not in visited and is_valid_position(nx, ny, area_1_data):
                new_path = path + [(nx, ny)]
                
                if (nx, ny) in end:
                    return new_path
                
                queue.append(((nx, ny), new_path))
                visited.add((nx, ny))
    
    return None  # 경로를 찾을 수 없음



def save_path_to_csv(path, filename):
    """경로를 CSV 파일로 저장"""
    if path:
        path_df = pd.DataFrame(path, columns=['x', 'y'])
        path_df.to_csv(filename, index=False)
        print(f"경로가 {filename} 파일로 저장되었습니다.")
    else:
        print("저장할 경로가 없습니다.")


def draw_map_with_path(area_1_data, path, filename, title):
    """경로가 표시된 지도를 그리는 함수"""
    # 지도 크기 설정
    max_x = area_1_data['x'].max()
    max_y = area_1_data['y'].max()
    min_x = area_1_data['x'].min()
    min_y = area_1_data['y'].min()
    
    # 그래프 설정
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(min_x - 0.5, max_x + 0.5)
    ax.set_ylim(min_y - 0.5, max_y + 0.5)
    ax.set_aspect('equal')
    ax.invert_yaxis()
    
    # 그리드 라인 그리기
    for x in range(min_x, max_x + 1):
        ax.axvline(x=x, color='lightgray', linestyle='-', linewidth=0.5)
    for y in range(min_y, max_y + 1):
        ax.axhline(y=y, color='lightgray', linestyle='-', linewidth=0.5)
    
    # 구조물 그리기
    for _, row in area_1_data.iterrows():
        x, y = row['x'], row['y']
        construction_site = row['ConstructionSite']
        category = row['category']
        struct_name = row['struct']
        
        # 건설 현장
        if construction_site == 1:
            rect = patches.Rectangle((x-0.4, y-0.4), 0.8, 0.8, 
                                   linewidth=1, edgecolor='black', 
                                   facecolor='gray', alpha=0.8)
            ax.add_patch(rect)
        
        # 다른 구조물들
        elif pd.notna(category) and category != 0:
            if struct_name == 'Apartment':
                circle = patches.Circle((x, y), 0.3, 
                                      linewidth=1, edgecolor='black', 
                                      facecolor='#8B4513', alpha=0.8)  # SaddleBrown
                ax.add_patch(circle)
            
            elif struct_name == 'Building':
                circle = patches.Circle((x, y), 0.3, 
                                      linewidth=1, edgecolor='black', 
                                      facecolor='#8B4513', alpha=0.8)  # SaddleBrown
                ax.add_patch(circle)
            
            elif struct_name == 'MyHome':
                triangle = patches.RegularPolygon((x, y), 3, radius=0.3,
                                                orientation=math.radians(180),
                                                linewidth=1, edgecolor='black', 
                                                facecolor='green', alpha=0.8)
                ax.add_patch(triangle)
            
            elif struct_name == 'BandalgomCoffee':
                rect = patches.Rectangle((x-0.3, y-0.3), 0.6, 0.6, 
                                       linewidth=1, edgecolor='black', 
                                       facecolor='green', alpha=0.8)
                ax.add_patch(rect)
    
    # 경로 그리기
    if path and len(path) > 1:
        path_x = [point[0] for point in path]
        path_y = [point[1] for point in path]
        ax.plot(path_x, path_y, 'r-', linewidth=3, alpha=0.8, label='Path')
        
        # 시작점과 끝점 표시
        ax.plot(path_x[0], path_y[0], 'ro', markersize=8, label='Start')
        ax.plot(path_x[-1], path_y[-1], 'rs', markersize=8, label='End')
    
    # 범례 추가
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#8B4513', 
            markersize=10, markeredgecolor='black', label='Apartment/Building'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='green', 
            markersize=10, markeredgecolor='black', label='Bandalgom Coffee'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='green', 
            markersize=10, markeredgecolor='black', label='My Home'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='gray', 
            markersize=12, markeredgecolor='black', label='Construction Site')
    ]

    if path and len(path) > 1:
        legend_elements.append(Line2D([0], [0], color='red', linewidth=3, label='Path'))


    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
    
    # 제목 및 라벨 설정
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xlabel('X Coordinate', fontsize=12)
    ax.set_ylabel('Y Coordinate', fontsize=12)
    
    # 좌표 눈금 설정
    ax.set_xticks(range(min_x, max_x + 1))
    ax.set_yticks(range(min_y, max_y + 1))
    
    # 레이아웃 조정
    plt.tight_layout()
    
    # 이미지 저장
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"지도가 {filename} 파일로 저장되었습니다.")
    
    plt.show()


def main(mode='shortest'):
    """메인 함수"""

    area_map_path = 'data/area_map.csv'
    area_struct_path = 'data/area_struct.csv'
    area_category_path = 'data/area_category.csv'

    try:
        area_map, area_struct, area_category = \
            load_data(area_map_path, area_struct_path, area_category_path)
        target_data = merge_data(area_map, area_struct, area_category)

        # 위치 찾기
        my_home, coffee_shops, all_structures = find_positions(target_data)
    
        if not my_home:
            print("내 집 위치를 찾을 수 없습니다.")
            return # my_home이 없는 경우에 대한 예외 처리 존재
        
        if my_home == (-1, -1):
            print("내 집 위치가 여러 개여서 길 찾기를 시작할 수 없습니다.")
            return # my_home이 여러 개인 경우에 대한 예외 처리 추가
        
        if not coffee_shops:
            print("반달곰 커피 위치를 찾을 수 없습니다.")
            return
        
        print(f"내 집 위치: {my_home}")
        print(f"반달곰 커피 위치: {coffee_shops}")
        print(f"방문 가능한 구조물 개수: {len(all_structures)}")

        if mode == 'shortest':
            # 최단 경로 탐색
            print("\n=== 최단 경로 탐색 ===")
            path = bfs_shortest_path(my_home, coffee_shops, target_data) # 첫 번째 카페로 이동
            
            if path:
                print(f"최단 경로 길이: {len(path) - 1} 단계")
                print("경로:", path)
                
                # CSV 저장
                save_path_to_csv(path, 'home_to_cafe.csv')
                
                # 지도 시각화
                draw_map_with_path(target_data, path, 'map_final.png', 
                                 'Shortest Path to Bandalgom Coffee')
                
                print("최단 경로 탐색이 완료되었습니다.")
            else:
                print("경로를 찾을 수 없습니다.") 

        elif mode == 'all_structures':
            # 모든 구조물 방문 후 카페로 가는 경로
            print("\n=== 모든 구조물 방문 후 카페로 가는 경로 탐색 ===")
            if all_structures:
                path = find_optimal_all_structures_path(my_home, all_structures, coffee_shops, target_data)
                
                if path:
                    print(f"전체 경로 길이: {len(path) - 1} 단계")
                    print(f"방문하는 구조물 개수: {len(all_structures)}")
                    print(f"최종 목적지: 가장 가까운 카페")
                    
                    # CSV 저장
                    save_path_to_csv(path, 'home_to_all_structures_to_cafe.csv')
                    
                    # 지도 시각화
                    draw_map_with_path(target_data, path, 'map_all_structures_to_cafe.png', 
                                     'Path: Home → All Structures → Nearest Cafe')
                    
                    print("모든 구조물 방문 후 카페로 가는 경로 탐색이 완료되었습니다.")
                else:
                    print("경로를 찾을 수 없습니다.")
            else:
                print("방문할 구조물이 없습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

    
if __name__ == "__main__":
    main() 