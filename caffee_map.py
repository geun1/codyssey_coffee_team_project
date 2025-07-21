import pandas as pd


def load_and_analyze_data():
    """CSV 파일들을 불러와서 분석하고 area 1 데이터만 필터링"""
    
    # CSV 파일들 불러오기
    print("=== CSV 파일 불러오기 ===")
    area_map = pd.read_csv('data/area_map.csv')
    area_struct = pd.read_csv('data/area_struct.csv')
    area_category = pd.read_csv('data/area_category.csv')
    
    # 컬럼명 공백 제거
    area_category.columns = area_category.columns.str.strip()
    
    print("area_map.csv 내용:")
    print(area_map.head())
    print()
    
    print("area_struct.csv 내용:")
    print(area_struct.head())
    print()
    
    print("area_category.csv 내용:")
    print(area_category)
    print()
    
    # 구조물 ID를 이름으로 변환
    print("=== 구조물 ID를 이름으로 변환 ===")
    # area_category의 데이터 공백 제거
    area_category['category'] = area_category['category'].astype(int)
    area_category['struct'] = area_category['struct'].astype(str).str.strip()
    
    # merge를 위해 area_struct의 category와 매핑
    area_struct_named = area_struct.merge(
        area_category, 
        on='category', 
        how='left'
    )
    
    print("구조물 이름이 추가된 area_struct:")
    print(area_struct_named.head(10))
    print()
    
    # 세 데이터를 하나의 DataFrame으로 병합
    print("=== 데이터 병합 ===")
    merged_data = area_map.merge(
        area_struct_named, 
        on=['x', 'y'], 
        how='left'
    )
    
    # area 기준으로 정렬
    merged_data = merged_data.sort_values(['area', 'x', 'y'])
    
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
    try:
        merged_data, target_data = load_and_analyze_data()
        print("데이터 분석이 완료되었습니다.")
        return merged_data, target_data
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        return None, None


if __name__ == "__main__":
    main() 