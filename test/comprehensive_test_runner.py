import sys
import os
import pandas as pd
import time
from pathlib import Path

# 상위 디렉토리의 모듈들을 import하기 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from map_direct_save import (
    find_positions, 
    bfs_shortest_path, 
    find_optimal_all_structures_path,
    save_path_to_csv,
    draw_map_with_path
)
from utils import load_data, merge_data
from caffee_map import analyze_data

class ComprehensiveTestRunner:
    """종합 테스트 실행기 - 1단계~3단계, 보너스까지 모든 기능 테스트"""
    
    def __init__(self):
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        self.results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.test_cases = [
            'basic_case',
            # 'small_map', 
            # 'large_map',
            # 'many_structures',
            # 'many_construction',
            # 'isolated_areas',
            # 'complex_pattern',
            # 'sparse_layout',
            # 'empty_data',
            # 'single_point',
            # 'all_construction',
            # 'isolated_points'
        ]
    
    def run_single_test(self, case_name):
        """단일 테스트 케이스 실행 - 모든 단계 포함"""
        print(f"\n {case_name} 종합 테스트 실행 중...")
        
        case_dir = os.path.join(self.test_data_dir, case_name)
        
        try:
            # 데이터 로드
            area_map_path = os.path.join(case_dir, 'area_map.csv')
            area_struct_path = os.path.join(case_dir, 'area_struct.csv')
            area_category_path = os.path.join(case_dir, 'area_category.csv')
            
            # 파일 존재 확인
            if not all(os.path.exists(p) for p in [area_map_path, area_struct_path, area_category_path]):
                print(f"    ❌ 데이터 파일이 없습니다: {case_dir}")
                return {'error': '데이터 파일이 없습니다'}
            
            area_map, area_struct, area_category = load_data(
                area_map_path, area_struct_path, area_category_path
            )
            target_data = merge_data(area_map, area_struct, area_category)
            
            # 위치 찾기
            my_home, coffee_shops, all_structures = find_positions(target_data)
            
            print(f"  📍 내 집: {my_home}")
            print(f"  ☕ 카페: {len(coffee_shops)}개")
            print(f"  🏢 구조물: {len(all_structures)}개")
            
            # 결과 저장 폴더 생성
            case_results_dir = os.path.join(self.results_dir, case_name)
            os.makedirs(case_results_dir, exist_ok=True)
            
            results = {}
            
            # 1단계: 데이터 수집 및 분석 (caffee_map.py 분석 기능 활용)
            print("  📊 1단계: 데이터 수집 및 분석...")
            data_analysis = self.perform_data_analysis(area_map, area_struct, area_category, case_results_dir)
            results['step1_data_analysis'] = data_analysis
            
            # 2단계: 지도 시각화
            print(" ️ 2단계: 지도 시각화...")
            map_visualization = self.perform_map_visualization(target_data, case_results_dir)
            results['step2_map_visualization'] = map_visualization
            
            # 3단계: 최단 경로 탐색
            print("  🛣️ 3단계: 최단 경로 탐색...")
            shortest_path_result = self.perform_shortest_path_test(my_home, coffee_shops, target_data, case_results_dir)
            results['step3_shortest_path'] = shortest_path_result
            
            # 보너스: 모든 구조물 방문 경로 탐색
            print("  🏃 보너스: 모든 구조물 방문 경로 탐색...")
            all_structures_result = self.perform_all_structures_test(my_home, all_structures, coffee_shops, target_data, case_results_dir)
            results['bonus_all_structures'] = all_structures_result
            
            # 데이터 정보 저장
            data_info = {
                'total_points': len(target_data),
                'my_home': my_home,
                'coffee_shops': coffee_shops,
                'all_structures': all_structures,
                'construction_sites': len(target_data[target_data['ConstructionSite'] == 1])
            }
            results['data_info'] = data_info
            
            return results
            
        except Exception as e:
            print(f"    ❌ 오류 발생: {str(e)}")
            return {'error': str(e)}
    
    def perform_data_analysis(self, area_map, area_struct, area_category, case_results_dir):
        """1단계: 데이터 수집 및 분석 (caffee_map.py 분석 기능 활용)"""
        try:
            # caffee_map.py의 analyze_data 함수 사용
            merged_data, target_data = analyze_data(area_map, area_struct, area_category)
            
            # 분석 결과를 파일로 저장
            analysis_file = os.path.join(case_results_dir, 'data_analysis.txt')
            
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write("=== 1단계: 데이터 수집 및 분석 결과 ===\n\n")
                
                # area_map.csv 내용
                f.write("area_map.csv 내용:\n")
                f.write(area_map.head().to_string())
                f.write("\n\n")
                
                # area_struct.csv 내용
                f.write("area_struct.csv 내용:\n")
                f.write(area_struct.head().to_string())
                f.write("\n\n")
                
                # area_category.csv 내용
                f.write("area_category.csv 내용:\n")
                f.write(area_category.to_string())
                f.write("\n\n")
                
                # 병합된 전체 데이터
                f.write("병합된 전체 데이터:\n")
                f.write(merged_data.head(10).to_string())
                f.write("\n\n")
                
                # BandalgomCoffee 관련 area 데이터 필터링
                f.write("=== BandalgomCoffee 관련 area 데이터 필터링 ===\n")
                
                # BandalgomCoffee가 있는 area 찾기
                target_areas = merged_data[merged_data['struct'] == 'BandalgomCoffee']['area'].unique()
                f.write(f"BandalgomCoffee가 있는 분석 대상 area들: {target_areas}\n\n")
                
                # 대상 area들의 데이터 필터링
                target_data_filtered = merged_data[merged_data['area'].isin(target_areas)].copy()
                f.write("대상 area 데이터:\n")
                f.write(target_data_filtered.to_string())
                f.write(f"\n\n대상 area 데이터 개수: {len(target_data_filtered)}\n\n")
                
                # 구조물 종류별 요약 통계 (보너스)
                f.write("=== 구조물 종류별 요약 통계 (보너스) ===\n")
                if not target_data_filtered.empty:
                    # category가 0이 아닌 것들만 (0은 빈 공간)
                    structures = target_data_filtered[target_data_filtered['category'] != 0]
                    
                    if not structures.empty:
                        structure_summary = structures.groupby('struct').size().reset_index(name='count')
                        
                        f.write("구조물 종류별 개수:\n")
                        f.write(structure_summary.to_string(index=False))
                        f.write("\n\n")
                        
                        # 각 구조물의 위치 정보
                        for struct_type in structures['struct'].unique():
                            struct_locations = structures[structures['struct'] == struct_type][['x', 'y']]
                            f.write(f"{struct_type} 위치:\n")
                            f.write(struct_locations.to_string(index=False))
                            f.write("\n\n")
                
                # 기본 통계 정보 추가
                f.write("=== 기본 통계 정보 ===\n")
                total_points = len(merged_data)
                construction_sites = len(merged_data[merged_data['ConstructionSite'] == 1])
                apartments = len(merged_data[merged_data['category'] == 1])
                buildings = len(merged_data[merged_data['category'] == 2])
                homes = len(merged_data[merged_data['category'] == 3])
                coffee_shops = len(merged_data[merged_data['category'] == 4])
                
                f.write(f"총 지점 수: {total_points}\n")
                f.write(f"건설현장: {construction_sites}개\n")
                f.write(f"아파트: {apartments}개\n")
                f.write(f"빌딩: {buildings}개\n")
                f.write(f"내 집: {homes}개\n")
                f.write(f"카페: {coffee_shops}개\n")
            
            return {
                'success': True,
                'total_points': len(merged_data),
                'construction_sites': construction_sites,
                'apartments': apartments,
                'buildings': buildings,
                'homes': homes,
                'coffee_shops': coffee_shops,
                'target_areas': target_areas.tolist() if 'target_areas' in locals() else [],
                'target_data_count': len(target_data_filtered) if 'target_data_filtered' in locals() else 0,
                'analysis_file': analysis_file
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def perform_map_visualization(self, target_data, case_results_dir):
        """2단계: 지도 시각화"""
        try:
            # 기본 지도 그리기
            map_file = os.path.join(case_results_dir, 'basic_map.png')
            draw_map_with_path(target_data, [], map_file, 'Basic Map Visualization')
            
            return {
                'success': True,
                'map_file': map_file
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def perform_shortest_path_test(self, my_home, coffee_shops, target_data, case_results_dir):
        """3단계: 최단 경로 탐색"""
        try:
            if not my_home or not coffee_shops:
                return {'success': False, 'error': '내 집 또는 카페가 없음'}
            
            # 최단 경로 찾기
            shortest_path = bfs_shortest_path(my_home, coffee_shops, target_data)
            
            if shortest_path:
                # 지도 그리기
                shortest_map_file = os.path.join(case_results_dir, 'shortest_path.png')
                draw_map_with_path(target_data, shortest_path, shortest_map_file, 
                                'Shortest Path to Coffee')
                
                # CSV 저장
                shortest_csv_file = os.path.join(case_results_dir, 'shortest_path.csv')
                save_path_to_csv(shortest_path, shortest_csv_file)
                
                return {
                    'success': True,
                    'length': len(shortest_path) - 1,
                    'map_file': shortest_map_file,
                    'csv_file': shortest_csv_file
                }
            else:
                return {'success': False, 'error': '최단 경로를 찾을 수 없음'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def perform_all_structures_test(self, my_home, all_structures, coffee_shops, target_data, case_results_dir):
        """보너스: 모든 구조물 방문 경로 탐색"""
        try:
            if not my_home or not all_structures or not coffee_shops:
                return {'success': False, 'error': '내 집, 구조물, 또는 카페가 없음'}
            
            # 모든 구조물 방문 경로 찾기
            all_structures_path = find_optimal_all_structures_path(
                my_home, all_structures, coffee_shops, target_data
            )
            
            if all_structures_path:
                # 지도 그리기
                all_structures_map_file = os.path.join(case_results_dir, 'all_structures_path.png')
                draw_map_with_path(target_data, all_structures_path, all_structures_map_file,
                                'All Structures Path to Coffee')
                
                # CSV 저장
                all_structures_csv_file = os.path.join(case_results_dir, 'all_structures_path.csv')
                save_path_to_csv(all_structures_path, all_structures_csv_file)
                
                return {
                    'success': True,
                    'length': len(all_structures_path) - 1,
                    'structures_visited': len(all_structures),
                    'map_file': all_structures_map_file,
                    'csv_file': all_structures_csv_file
                }
            else:
                return {'success': False, 'error': '모든 구조물 방문 경로를 찾을 수 없음'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 80)
        print("                    종합 테스트 실행 (1단계~3단계 + 보너스)")
        print("=" * 80)
        
        start_time = time.time()
        all_results = {}
        
        for case_name in self.test_cases:
            results = self.run_single_test(case_name)
            all_results[case_name] = results
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 결과 요약 생성
        self.generate_comprehensive_summary(all_results, total_time)
        
        return all_results
    
    def generate_comprehensive_summary(self, all_results, total_time):
        """종합 결과 요약 생성"""
        summary_file = os.path.join(self.results_dir, 'comprehensive_test_summary.txt')
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("                    종합 테스트 결과 요약\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"총 실행 시간: {total_time:.2f}초\n")
            f.write(f"테스트 케이스 수: {len(all_results)}\n\n")
            
            for case_name, results in all_results.items():
                f.write(f"📁 {case_name}\n")
                f.write("-" * 50 + "\n")
                
                if 'error' in results:
                    f.write(f"❌ 오류: {results['error']}\n")
                else:
                    data_info = results.get('data_info', {})
                    f.write(f"📍 내 집: {data_info.get('my_home', 'None')}\n")
                    f.write(f"☕ 카페: {len(data_info.get('coffee_shops', []))}개\n")
                    f.write(f"🏢 구조물: {len(data_info.get('all_structures', []))}개\n")
                    f.write(f"🚧 건설현장: {data_info.get('construction_sites', 0)}개\n\n")
                    
                    # 1단계: 데이터 분석 결과
                    step1 = results.get('step1_data_analysis', {})
                    if step1.get('success'):
                        f.write("📊 1단계(데이터 분석): ✅ 성공\n")
                        f.write(f"   - 총 지점: {step1.get('total_points', 0)}개\n")
                        f.write(f"   - 아파트: {step1.get('apartments', 0)}개\n")
                        f.write(f"   - 빌딩: {step1.get('buildings', 0)}개\n")
                        f.write(f"   - 대상 area: {step1.get('target_areas', [])}\n")
                        f.write(f"   - 대상 데이터: {step1.get('target_data_count', 0)}개\n")
                    else:
                        f.write("📊 1단계(데이터 분석): ❌ 실패\n")
                    
                    # 2단계: 지도 시각화 결과
                    step2 = results.get('step2_map_visualization', {})
                    if step2.get('success'):
                        f.write("️ 2단계(지도 시각화): ✅ 성공\n")
                    else:
                        f.write("️ 2단계(지도 시각화): ❌ 실패\n")
                    
                    # 3단계: 최단 경로 결과
                    step3 = results.get('step3_shortest_path', {})
                    if step3.get('success'):
                        f.write(f"🛣️ 3단계(최단 경로): ✅ 성공 (길이: {step3.get('length', 0)})\n")
                    else:
                        f.write("🛣️ 3단계(최단 경로): ❌ 실패\n")
                    
                    # 보너스: 모든 구조물 방문 결과
                    bonus = results.get('bonus_all_structures', {})
                    if bonus.get('success'):
                        f.write(f"🏃 보너스(모든 구조물): ✅ 성공 (길이: {bonus.get('length', 0)})\n")
                    else:
                        f.write("🏃 보너스(모든 구조물): ❌ 실패\n")
                
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("📊 결과 파일들은 각 테스트 케이스 폴더에 저장되었습니다.\n")
            f.write("📁 PNG 파일: 지도 시각화\n")
            f.write("📁 CSV 파일: 경로 데이터\n")
            f.write("📁 TXT 파일: 데이터 분석 결과\n")
        
        print(f"\n 종합 결과 요약이 {summary_file}에 저장되었습니다.")
        print(f"📁 모든 결과는 {self.results_dir} 폴더에 저장되었습니다.")

def main():
    """메인 실행 함수"""
    runner = ComprehensiveTestRunner()
    results = runner.run_all_tests()
    
    # 성공/실패 통계
    total_cases = len(results)
    successful_step1 = sum(1 for r in results.values() 
                          if r.get('step1_data_analysis', {}).get('success', False))
    successful_step2 = sum(1 for r in results.values() 
                          if r.get('step2_map_visualization', {}).get('success', False))
    successful_step3 = sum(1 for r in results.values() 
                          if r.get('step3_shortest_path', {}).get('success', False))
    successful_bonus = sum(1 for r in results.values() 
                          if r.get('bonus_all_structures', {}).get('success', False))
    
    print(f"\n 최종 통계:")
    print(f"   총 테스트 케이스: {total_cases}개")
    print(f"   1단계(데이터 분석) 성공: {successful_step1}개")
    print(f"   2단계(지도 시각화) 성공: {successful_step2}개")
    print(f"   3단계(최단 경로) 성공: {successful_step3}개")
    print(f"   보너스(모든 구조물) 성공: {successful_bonus}개")

if __name__ == "__main__":
    main() 