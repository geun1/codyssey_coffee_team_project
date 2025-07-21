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


def main(mode='shortest'):
    """메인 함수"""
    try:
        # 데이터 로드
        target_data = load_target_area_data()

                # 위치 찾기
        my_home, coffee_shop, all_structures = find_positions(target_data)
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
if __name__ == "__main__":
    main() 