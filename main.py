#!/usr/bin/env python3
"""
반달곰 커피를 찾아서: 데이터 분석과 경로 탐색 프로젝트
메인 프로그램 - CLI 인터페이스
"""

import sys
import os


def print_menu():
    """메뉴를 출력하는 함수"""
    print("\n" + "="*60)
    print("🐻 반달곰 커피를 찾아서: 데이터 분석과 경로 탐색 프로젝트")
    print("="*60)
    print("1. 데이터 수집 및 분석 (1단계)")
    print("2. 지도 시각화 (2단계)")
    print("3. 최단 경로 탐색 (3단계)")
    print("4. 모든 구조물 방문 경로 탐색 (보너스)")
    print("5. 전체 프로세스 실행")
    print("0. 종료")
    print("="*60)


def run_stage_1():
    """1단계: 데이터 수집 및 분석 실행"""
    print("\n🔍 1단계: 데이터 수집 및 분석을 실행합니다...")
    try:
        import mas_map
        mas_map.main()
        print("✅ 1단계가 성공적으로 완료되었습니다.")
    except ImportError:
        print("❌ mas_map.py 파일이 없습니다.")
    except Exception as e:
        print(f"❌ 1단계 실행 중 오류가 발생했습니다: {e}")


def run_stage_2():
    """2단계: 지도 시각화 실행"""
    print("\n🗺️  2단계: 지도 시각화를 실행합니다...")
    try:
        import map_draw
        map_draw.main()
        print("✅ 2단계가 성공적으로 완료되었습니다.")
    except ImportError:
        print("❌ map_draw.py 파일이 없습니다.")
    except Exception as e:
        print(f"❌ 2단계 실행 중 오류가 발생했습니다: {e}")


def run_stage_3():
    """3단계: 최단 경로 탐색 실행"""
    print("\n🚶 3단계: 최단 경로 탐색을 실행합니다...")
    try:
        import map_direct_save
        map_direct_save.main('shortest')
        print("✅ 3단계가 성공적으로 완료되었습니다.")
    except ImportError:
        print("❌ map_direct_save.py 파일이 없습니다.")
    except Exception as e:
        print(f"❌ 3단계 실행 중 오류가 발생했습니다: {e}")


def run_bonus():
    """보너스: 모든 구조물 방문 경로 탐색 실행"""
    print("\n🏆 보너스: 모든 구조물 방문 경로 탐색을 실행합니다...")
    try:
        import map_direct_save
        map_direct_save.main('all_structures')
        print("✅ 보너스 기능이 성공적으로 완료되었습니다.")
    except ImportError:
        print("❌ map_direct_save.py 파일이 없습니다.")
    except Exception as e:
        print(f"❌ 보너스 기능 실행 중 오류가 발생했습니다: {e}")


def run_all_stages():
    """전체 프로세스 실행"""
    print("\n🚀 전체 프로세스를 순차적으로 실행합니다...")
    
    # 1단계 실행
    run_stage_1()
    
    # 2단계 실행
    run_stage_2()
    
    # 3단계 실행
    run_stage_3()
    
    # 보너스 실행 여부 확인
    while True:
        bonus_choice = input("\n보너스 기능(모든 구조물 방문)도 실행하시겠습니까? (y/n): ").strip().lower()
        if bonus_choice in ['y', 'yes', '예', 'ㅇ']:
            run_bonus()
            break
        elif bonus_choice in ['n', 'no', '아니오', 'ㄴ']:
            break
        else:
            print("올바른 선택지를 입력해주세요 (y/n).")
    
    print("\n🎉 전체 프로세스가 완료되었습니다!")


def check_dependencies():
    """필요한 라이브러리 확인"""
    required_modules = ['pandas', 'matplotlib']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ 다음 라이브러리가 설치되지 않았습니다: {', '.join(missing_modules)}")
        print("다음 명령어로 설치해주세요:")
        print(f"pip install {' '.join(missing_modules)}")
        return False
    
    return True


def check_data_files():
    """데이터 파일 존재 확인"""
    required_files = [
        'data/area_map.csv',
        'data/area_struct.csv', 
        'data/area_category.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 다음 데이터 파일이 없습니다: {', '.join(missing_files)}")
        print("data 폴더에 필요한 CSV 파일들이 있는지 확인해주세요.")
        return False
    
    return True


def main():
    """메인 함수"""
    print("🐻 반달곰 커피 프로젝트를 시작합니다!")
    
    # 의존성 및 데이터 파일 확인
    if not check_dependencies():
        return
    
    if not check_data_files():
        return
    
    print("✅ 모든 의존성과 데이터 파일이 확인되었습니다.")
    
    while True:
        print_menu()
        
        try:
            choice = input("원하는 작업을 선택하세요 (0-5): ").strip()
            
            if choice == '1':
                run_stage_1()
            elif choice == '2':
                run_stage_2()
            elif choice == '3':
                run_stage_3()
            elif choice == '4':
                run_bonus()
            elif choice == '5':
                run_all_stages()
            elif choice == '0':
                print("\n👋 프로그램을 종료합니다. 감사합니다!")
                break
            else:
                print("❌ 올바른 선택지를 입력해주세요 (0-5).")
        
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다. 감사합니다!")
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main() 