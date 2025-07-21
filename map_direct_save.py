# map_direct_save.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque
import itertools

def load_target_area_data():
    """MyHome과 BandalgomCoffee가 있는 area 데이터를 불러오는 함수"""
    # CSV 파일들 불러오기
    area_map = pd.read_csv('data/area_map.csv')
    area_struct = pd.read_csv('data/area_struct.csv')
    area_category = pd.read_csv('data/area_category.csv')
    
    # 컬럼명 공백 제거
    area_category.columns = area_category.columns.str.strip()
    
    # area_category의 공백 제거 및 타입 변환
    area_category['category'] = area_category['category'].astype(int)
    area_category['struct'] = area_category['struct'].astype(str).str.strip()
    
    # 데이터 병합
    area_struct_named = area_struct.merge(area_category, on='category', how='left')
    merged_data = area_map.merge(area_struct_named, on=['x', 'y'], how='left')
    
    # MyHome과 BandalgomCoffee가 있는 area 찾기
    my_home_area = merged_data[merged_data['struct'] == 'MyHome']['area'].iloc[0] if not merged_data[merged_data['struct'] == 'MyHome'].empty else None
    coffee_areas = merged_data[merged_data['struct'] == 'BandalgomCoffee']['area'].unique()
    
    # 대상 area들 설정
    target_areas = set()
    if my_home_area is not None:
        target_areas.add(my_home_area)
    target_areas.update(coffee_areas)
    
    # 대상 area들의 데이터만 필터링
    target_data = merged_data[merged_data['area'].isin(target_areas)].copy()
    
    return target_data

def find_positions(area_1_data):
    """내 집과 반달곰 커피 위치, 그리고 모든 구조물 위치를 찾는 함수"""
    my_home = None
    coffee_shop = None
    all_structures = []
    
    for _, row in area_1_data.iterrows():
        x, y = row['x'], row['y']
        struct_name = row['struct']
        category = row['category']
        
        if pd.notna(struct_name):
            if struct_name == 'MyHome':
                my_home = (x, y)
            elif struct_name == 'BandalgomCoffee':
                coffee_shop = (x, y)
            
            # 건설현장이 아닌 모든 구조물 (내 집 제외)
            if (pd.notna(category) and category != 0 and 
                struct_name != 'MyHome' and row['ConstructionSite'] != 1):
                all_structures.append((x, y))
    
    return my_home, coffee_shop, all_structures

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
                
                if (nx, ny) == end:
                    return new_path
                
                queue.append(((nx, ny), new_path))
                visited.add((nx, ny))
    
    return None  # 경로를 찾을 수 없음


def find_optimal_all_structures_path(my_home, all_structures, area_1_data):
    """모든 구조물을 방문하는 최적 경로 찾기 (TSP 근사해법)"""
    if not all_structures:
        return []
    
    # 각 구조물 간의 최단 거리 계산
    all_points = [my_home] + all_structures
    distances = {}
    paths = {}
    
    print("구조물 간 최단 거리 계산 중...")
    for i, start in enumerate(all_points):
        for j, end in enumerate(all_points):
            if i != j:
                path = bfs_shortest_path(start, end, area_1_data)
                if path:
                    distances[(start, end)] = len(path) - 1
                    paths[(start, end)] = path
                else:
                    distances[(start, end)] = float('inf')
                    paths[(start, end)] = []
    
    # 작은 수의 구조물에 대해서는 완전 탐색
    if len(all_structures) <= 8:
        min_distance = float('inf')
        best_order = None
        
        print(f"모든 구조물 방문 경로 최적화 중... ({len(all_structures)}개 구조물)")
        for perm in itertools.permutations(all_structures):
            total_distance = 0
            current = my_home
            
            for next_point in perm:
                if (current, next_point) in distances:
                    total_distance += distances[(current, next_point)]
                    current = next_point
                else:
                    total_distance = float('inf')
                    break
            
            if total_distance < min_distance:
                min_distance = total_distance
                best_order = perm
        
        # 최적 경로 구성
        if best_order:
            full_path = []
            current = my_home
            
            for next_point in best_order:
                if (current, next_point) in paths:
                    segment = paths[(current, next_point)]
                    if full_path:  # 첫 번째가 아니면 시작점 제외
                        segment = segment[1:]
                    full_path.extend(segment)
                    current = next_point
            
            return full_path
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
        
        return full_path
    
    return []


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
        patches.Circle((0, 0), 0.3, facecolor='#8B4513', edgecolor='black', label='Apartment/Building'),
        patches.Rectangle((0, 0), 0.6, 0.6, facecolor='green', edgecolor='black', label='Bandalgom Coffee'),
        patches.RegularPolygon((0, 0), 3, radius=0.3, facecolor='green', edgecolor='black', label='My Home'),
        patches.Rectangle((0, 0), 0.8, 0.8, facecolor='gray', edgecolor='black', label='Construction Site')
    ]
    
    if path and len(path) > 1:
        legend_elements.append(plt.Line2D([0], [0], color='red', linewidth=3, label='Path'))
    
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
    try:
        # 데이터 로드
        target_data = load_target_area_data()

                # 위치 찾기
        my_home, coffee_shop, all_structures = find_positions(target_data)
    
        if not my_home:
            print("내 집 위치를 찾을 수 없습니다.")
            return
        
        if not coffee_shop:
            print("반달곰 커피 위치를 찾을 수 없습니다.")
            return
        
        print(f"내 집 위치: {my_home}")
        print(f"반달곰 커피 위치: {coffee_shop}")
        print(f"방문 가능한 구조물 개수: {len(all_structures)}")

        if mode == 'shortest':
            # 최단 경로 탐색
            print("\n=== 최단 경로 탐색 ===")
            path = bfs_shortest_path(my_home, coffee_shop, target_data)
            
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
            # 모든 구조물 방문 경로 (보너스)
            print("\n=== 모든 구조물 방문 경로 탐색 (보너스) ===")
            if all_structures:
                path = find_optimal_all_structures_path(my_home, all_structures, target_data)
                
                if path:
                    print(f"모든 구조물 방문 경로 길이: {len(path) - 1} 단계")
                    print(f"방문하는 구조물 개수: {len(all_structures)}")
                    
                    # CSV 저장
                    save_path_to_csv(path, 'home_to_all_structures.csv')
                    
                    # 지도 시각화
                    draw_map_with_path(target_data, path, 'map_all_structures.png', 
                                     'Path Visiting All Structures')
                    
                    print("모든 구조물 방문 경로 탐색이 완료되었습니다.")
                else:
                    print("모든 구조물을 방문하는 경로를 찾을 수 없습니다.")
            else:
                print("방문할 구조물이 없습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

    
if __name__ == "__main__":
    main() 