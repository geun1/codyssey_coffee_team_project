# utils.py

import pandas as pd

def load_data(area_map_path, area_struct_path, area_category_path):
    # 지정된 경로로부터 데이터를 불러오고 타입 변환하는 함수

    area_map = pd.read_csv(area_map_path)
    area_struct = pd.read_csv(area_struct_path)
    area_category = pd.read_csv(area_category_path)

    # 컬럼명 공백 제거
    area_map.columns = area_map.columns.str.strip()
    area_struct.columns = area_struct.columns.str.strip()
    area_category.columns = area_category.columns.str.strip()
    
    # 컬럼 데이터 별 공백 제거 및 타입 변환
    area_map['x'] = area_map['x'].astype(int)
    area_map['y'] = area_map['y'].astype(int)
    area_map['ConstructionSite'] = area_map['ConstructionSite'].astype(int)

    area_struct['x'] = area_struct['x'].astype(int)
    area_struct['y'] = area_struct['y'].astype(int)
    area_struct['category'] = area_struct['category'].astype(int)
    area_struct['area'] = area_struct['area'].astype(int)

    area_category['category'] = area_category['category'].astype(int)
    area_category['struct'] = area_category['struct'].astype(str).str.strip()

    return area_map, area_struct, area_category


def merge_data(area_map, area_struct, area_category, default_label="None"):
    # 공사 여부, 구조물 위치 정보, 구조물 유형 라벨 정보를 모두 병합하고 area 기준으로 정렬하는 함수

    area_struct_named = area_struct.merge(area_category, on='category', how='left')
    merged_data = area_map.merge(area_struct_named, on=['x', 'y'], how='left')
    merged_data = merged_data.sort_values(by=['area', 'x', 'y']).reset_index(drop=True)
    merged_data.fillna({
        'struct': default_label
    }, inplace=True)

    
    return merged_data

