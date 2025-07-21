# map_draw.py
# 테스트입니다.

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def load_target_area_data():
    ## 1. MyHome과 BandalgomCoffee가 있는 area 데이터를 불러오는 함수 구현
    ## area_map.csv, area_struct.csv, area_category.csv 불러오기
    area_map = pd.read_csv('data/area_map.csv')
    area_struct = pd.read_csv('data/area_struct.csv')
    area_category = pd.read_csv('data/area_category.csv')
    
    ## 컬럼명 공백 제거
    area_category.columns = area_category.columns.str.strip()
    
    ## area_category의 공백 제거 및 타입 변환
    area_category['category'] = area_category['category'].astype(int)
    area_category['struct'] = area_category['struct'].astype(str).str.strip()
    
    ## 데이터 병합
    area_struct_named = area_struct.merge(area_category, on='category', how='left')
    merged_data = area_map.merge(area_struct_named, on=['x', 'y'], how='left')
    
    ## MyHome과 BandalgomCoffee가 있는 area 찾기
    my_home_area = merged_data[merged_data['struct'] == 'MyHome']['area'].iloc[0] if not merged_data[merged_data['struct'] == 'MyHome'].empty else None
    coffee_areas = merged_data[merged_data['struct'] == 'BandalgomCoffee']['area'].unique()
    
    ## 대상 area들 설정
    target_areas = set()
    if my_home_area is not None:
        target_areas.add(my_home_area)
    target_areas.update(coffee_areas)
    
    ## 대상 area들의 데이터만 필터링
    target_data = merged_data[merged_data['area'].isin(target_areas)].copy()
    
    return target_data


def draw_map():
    ## 지도를 시각화하는 함수 구현
    ## load_target_area_data() 함수를 사용하여 데이터 로드
    area_1_data = load_target_area_data()
    
    ## 지도 크기 설정 (좌측 상단이 (1,1), 우측 하단이 가장 큰 좌표)
    max_x = area_1_data['x'].max()
    max_y = area_1_data['y'].max()
    min_x = area_1_data['x'].min()
    min_y = area_1_data['y'].min()
    
    ## 그래프 설정
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(min_x - 0.5, max_x + 0.5)
    ax.set_ylim(min_y - 0.5, max_y + 0.5)
    ax.set_aspect('equal')
    
    ## 좌측 상단이 (1, 1)이 되도록 y축 뒤집기 [요구조건]
    ax.invert_yaxis()
    
    ## 그리드 라인 그리기
    for x in range(min_x, max_x + 1):
        ax.axvline(x=x, color='lightgray', linestyle='-', linewidth=0.5)
    for y in range(min_y, max_y + 1):
        ax.axhline(y=y, color='lightgray', linestyle='-', linewidth=0.5)
    
    ## 각 위치별로 구조물 그리기
    for _, row in area_1_data.iterrows():
        x, y = row['x'], row['y']
        construction_site = row['ConstructionSite']
        category = row['category']
        struct_name = row['struct']
        
        ## 건설 현장이 있는 경우, 회색 사각형으로 표시 (우선 순위 존재)
        if construction_site == 1:
            rect = patches.Rectangle((x-0.4, y-0.4), 0.8, 0.8, 
                                   linewidth=1, edgecolor='black', 
                                   facecolor='gray', alpha=0.8)
            ax.add_patch(rect)
        
        ## 다른 구조물들 표시 (건설 현장과 겹치지 않는 경우만)
        elif pd.notna(category) and category != 0:
            if struct_name == 'Apartment':
                ## 아파트: 진한 갈색 원형
                circle = patches.Circle((x, y), 0.3, 
                                      linewidth=1, edgecolor='black', 
                                      facecolor='#8B4513', alpha=0.8)
                ax.add_patch(circle)
            
            elif struct_name == 'Building':
                ## 빌딩: 진한 갈색 원형
                circle = patches.Circle((x, y), 0.3, 
                                      linewidth=1, edgecolor='black', 
                                      facecolor='#8B4513', alpha=0.8)
                ax.add_patch(circle)
            
            elif struct_name == 'MyHome':
                ## 내 집: 녹색 삼각형
                triangle = patches.RegularPolygon((x, y), 3, radius=0.3, 
                                                linewidth=1, edgecolor='black', 
                                                facecolor='green', alpha=0.8)
                ax.add_patch(triangle)
            
            elif struct_name == 'BandalgomCoffee':
                ## 반달곰 커피: 녹색 사각형
                rect = patches.Rectangle((x-0.3, y-0.3), 0.6, 0.6, 
                                       linewidth=1, edgecolor='black', 
                                       facecolor='green', alpha=0.8)
                ax.add_patch(rect)
    
    ## 범례 추가 (보너스 문제)
    legend_elements = [
        patches.Circle((0, 0), 0.3, facecolor='#8B4513', edgecolor='black', label='Apartment/Building'),
        patches.Rectangle((0, 0), 0.6, 0.6, facecolor='green', edgecolor='black', label='Bandalgom Coffee'),
        patches.RegularPolygon((0, 0), 3, radius=0.3, facecolor='green', edgecolor='black', label='My Home'),
        patches.Rectangle((0, 0), 0.8, 0.8, facecolor='gray', edgecolor='black', label='Construction Site')
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
    
    ## 제목 및 라벨 설정
    ax.set_title('Bandalgom Coffee Regional Map (MyHome & Coffee Areas)', fontsize=16, pad=20)
    ax.set_xlabel('X Coordinate', fontsize=12)
    ax.set_ylabel('Y Coordinate', fontsize=12)
    
    ## 좌표 눈금 설정
    ax.set_xticks(range(min_x, max_x + 1))
    ax.set_yticks(range(min_y, max_y + 1))
    
    ## 레이아웃 조정
    plt.tight_layout()
    
    ## 이미지 저장
    plt.savefig('map.png', dpi=300, bbox_inches='tight')
    print("지도가 map.png 파일로 저장되었습니다.")
    
    ## 그래프 표시
    plt.show()
    
    return area_1_data

def main():
    ## 메인 함수 구현
    try:
        area_1_data = draw_map()
        print("지도 시각화가 완료되었습니다.")
        return area_1_data
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        return None


if __name__ == "__main__":
    main()