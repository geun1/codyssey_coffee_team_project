import pandas as pd
from utils import load_data, merge_data

def analyze_data(area_map, area_struct, area_category):
    """데이터를 확인 및 병합하고 area 1 데이터만 필터링 후 통계 분석"""
    
    print("area_map.csv 내용:")
    print(area_map.head())
    print()
    
    print("area_struct.csv 내용:")
    print(area_struct.head())
    print()
    
    print("area_category.csv 내용:")
    print(area_category)
    print()
    
    merged_data = merge_data(area_map, area_struct, area_category)
    
    print("병합된 전체 데이터:")
    print(merged_data.head(10))
    print()
    
    # area 1에 대한 데이터만 필터링
    print("=== MyHome과 BandalgomCoffee 관련 area 데이터 필터링 ===")
    
    # 먼저 MyHome과 BandalgomCoffee가 있는 area 찾기
    my_home_area = merged_data[merged_data['struct'] == 'MyHome']['area'].iloc[0] if not merged_data[merged_data['struct'] == 'MyHome'].empty else None
    coffee_areas = merged_data[merged_data['struct'] == 'BandalgomCoffee']['area'].unique()
    
    print(f"MyHome이 있는 area: {my_home_area}")
    print(f"BandalgomCoffee가 있는 area들: {coffee_areas}")
    
    # MyHome과 BandalgomCoffee가 있는 모든 area 포함
    target_areas = set()
    if my_home_area is not None:
        target_areas.add(my_home_area)
    target_areas.update(coffee_areas)
    
    print(f"분석 대상 area들: {sorted(target_areas)}")
    
    # 대상 area들의 데이터 필터링
    target_data = merged_data[merged_data['area'].isin(target_areas)].copy()
    
    print("대상 area 데이터:")
    print(target_data)
    print()
    
    print(f"대상 area 데이터 개수: {len(target_data)}")
    print()

    
    # 구조물 종류별 요약 통계 (보너스)
    print("=== 구조물 종류별 요약 통계 (보너스) ===")
    if not target_data.empty:
        # category가 0이 아닌 것들만 (0은 빈 공간)
        structures = target_data[target_data['category'] != 0]
        
        if not structures.empty:
            structure_summary = structures.groupby('struct').agg({
                'x': 'count',
                'category': 'first'
            }).rename(columns={'x': 'count'})
            
            print("구조물 종류별 개수:")
            print(structure_summary)
            print()
            
            # 각 구조물의 위치 정보
            for struct_type in structures['struct'].unique():
                struct_locations = structures[structures['struct'] == struct_type][['x', 'y']]
                print(f"{struct_type} 위치:")
                print(struct_locations.to_string(index=False))
                print()
    
    return merged_data, target_data


def main():
    """메인 함수"""
    area_map_path = 'data/area_map.csv'
    area_struct_path = 'data/area_struct.csv'
    area_category_path = 'data/area_category.csv'

    try:
        area_map, area_struct, area_category = \
            load_data(area_map_path, area_struct_path, area_category_path)
        merged_data, target_data = \
            analyze_data(area_map, area_struct, area_category)
        print("데이터 분석이 완료되었습니다.")
        return merged_data, target_data
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        return None, None


if __name__ == "__main__":
    main() 