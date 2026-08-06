import json
import os
import sys

# [요구사항 4] 개별 퀴즈를 관리하는 클래스
class Quiz:
    def __init__(self, question, options, answer):
        self.question = question   # str: 문제 내용
        self.options = options     # list: 4개의 선택지
        self.answer = answer       # int: 정답 번호 (1~4)

    def display(self, index):
        """문제를 화면에 예쁘게 출력합니다."""
        print(f"\nQ{index}. {self.question}")
        for i, opt in enumerate(self.options, 1):
            print(f"   ({i}) {opt}")

    def is_correct(self, user_input):
        """[데이터타입 bool 활용] 정답 여부를 True/False로 반환합니다."""
        return user_input == self.answer

# [요구사항 10] 게임 전체 흐름을 관리하는 클래스
class QuizGame:
    def __init__(self):
        self.file_path = "state.json"
        self.quizzes = []
        self.best_score = None  # [요구사항 8] 아직 퀴즈를 안 푼 상태는 None
        self.load_data()        # 시작할 때 파일 불러오기

    def clear_screen(self):
        """화면을 깨끗하게 지워주는 기능 (Windows는 cls, Mac/Linux는 clear)"""
        os.system('cls' if os.name == 'nt' else 'clear')    

    # [요구사항 11] 파일 읽기(r) 및 예외 처리
    def load_data(self):
        # 기본 퀴즈 데이터 5개 (파일이 없거나 손상되었을 때 사용)
        default_data = {
            "best_score": None,
            "quizzes": [
                {"question": "다음 중 맞춤법이 올바른 것은?", "options": ["어의없다", "어이없다", "어의업다", "어이업다"], "answer": 2},
                {"question": "'오랜만에'의 줄임말로 옳은 것은?", "options": ["오랫만", "오랫만에", "오랜만", "오랜마네"], "answer": 3},
                {"question": "물건을 '통째로' 삼키다. 맞을까요?", "options": ["통째로", "통채로", "통재로", "통체로"], "answer": 1},
                {"question": "어떤 일이 잘 안될 때 쓰는 말은?", "options": ["안되", "안돼", "않되", "않돼"], "answer": 2},
                {"question": "윗사람에게 쓰는 인사말로 옳은 것은?", "options": ["안녕히 계세요", "안녕히 계셔요", "안녕히 가세요", "모두 맞음"], "answer": 4}
            ]
        }

        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.best_score = data.get("best_score")
                    self.quizzes = [Quiz(**q) for q in data.get("quizzes", [])]
            else:
                raise FileNotFoundError # 파일 없으면 기본 데이터로 이동

        except (FileNotFoundError, json.JSONDecodeError):
            # [요구사항 3] 파일이 없거나 손상된 경우 초기화
            print("⚠️ 데이터를 불러올 수 없어 기본 퀴즈로 시작합니다.")
            self.best_score = default_data["best_score"]
            self.quizzes = [Quiz(**q) for q in default_data["quizzes"]]

    # [요구사항 11] 파일 쓰기(w)
    def save_data(self):
        data = {
            "best_score": self.best_score,
            "quizzes": [vars(q) for q in self.quizzes] # Quiz 객체를 dict로 변환
        }
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except OSError:
            print("⚠️ 파일 저장 중 오류가 발생했습니다.")

    # [요구사항 3] 공통 입력 예외처리 (반복되는 숫자 입력을 하나로 처리)
    def get_input(self, prompt, min_val, max_val):
        while True:
            try:
                user_input = input(prompt).strip() # 공백 제거
                if not user_input:
                    print("⚠️ 입력이 비어있습니다.")
                    continue
                
                val = int(user_input) # 숫자 변환 시도
                if min_val <= val <= max_val:
                    return val
                print(f"⚠️ {min_val}~{max_val} 사이의 숫자를 입력하세요.")
            except ValueError:
                print("⚠️ 문자가 아닌 숫자로 입력해주세요.")

    def play(self):
        """[요구사항 6] 퀴즈 풀기"""
        if not self.quizzes:
            print("❌ 등록된 퀴즈가 없습니다.")
            return

        current_score = 0
        print("\n--- 퀴즈를 시작합니다! ---")
        for i, quiz in enumerate(self.quizzes, 1):
            quiz.display(i)
            user_ans = self.get_input("정답 번호 (1-4): ", 1, 4)
            
            if quiz.is_correct(user_ans):
                print("✅ 정답입니다!")
                current_score += 20 # 5문제 기준 100점 만점
            else:
                print(f"❌ 틀렸습니다. 정답은 {quiz.answer}번입니다.")

        print(f"\n[이번 게임 점수: {current_score}점]")
        
        # [요구사항 8] 최고 점수 비교 및 갱신
        if self.best_score is None or current_score > self.best_score:
            print("🏆 최고 점수 갱신!")
            self.best_score = current_score
            self.save_data()

    def add_quiz(self):
        """[요구사항 7] 퀴즈 추가"""
        print("\n--- 새 퀴즈 추가 ---")
        question = input("문제 내용을 입력하세요: ").strip()
        
        options = []
        for i in range(1, 5):
            option = input(f"보기 {i}: ").strip()
            options.append(option)
        
        # 이 줄들이 반드시 위쪽 코드들과 세로 줄이 딱 맞아야 합니다!
            answer = self.get_input("정답 번호 (1-4): ", 1, 4)
        
            self.quizzes.append(Quiz(question, options, answer))
            self.save_data()
            print("✅ 퀴즈가 성공적으로 추가되었습니다.")
        

    def show_list(self):
        """[요구사항 8] 퀴즈 목록 보기"""
        print("\n--- 저장된 퀴즈 목록 ---")
        if not self.quizzes:
            print("퀴즈가 하나도 없습니다.")
        else:
            for i, q in enumerate(self.quizzes, 1):
                print(f"{i}. {q.question}")
                

    def run(self):
        try: # 1. 여기서 try를 시작합니다.
            """[요구사항 2] 메인 메뉴 실행"""
            while True:
                self.clear_screen() # <--- 메뉴를 그리기 전에 화면을 싹 지움
                print("\n=== 📝 맞춤법 마스터 퀴즈 ===")
                print("1. 퀴즈 풀기")
                print("2. 퀴즈 추가")
                print("3. 퀴즈 목록")
                print("4. 최고 점수 확인")
                print("5. 종료")
                print("============================")

               # 기존 코드에서 메뉴 선택 시            
                choice = input("선택: ").strip() # 앞뒤 공백 제거

               # [추가] 빈 입력 처리
                if not choice:
                    print("⚠️ 입력이 비어 있습니다. 숫자를 입력해주세요.")
                    input("\n엔터를 누르면 메뉴로 돌아갑니다...")
                    continue
               
                if choice == '1': 
                   self.play()
                   input("\n[Enter]를 누르면 메뉴로 돌아갑니다...") # 이 줄을 추가!
                elif choice == '2': 
                   self.add_quiz()
                   input("\n[Enter]를 누르면 메뉴로 돌아갑니다...") # 이 줄을 추가!
                elif choice == '3': 
                   self.show_list()
                   input("\n[Enter]를 누르면 메뉴로 돌아갑니다...") # 이 줄을 추가!
                elif choice == '4':
                # [요구사항 8] 아직 안 푼 경우 처리
                    if self.best_score is None:
                        print("\n📭 아직 퀴즈를 푼 기록이 없습니다.")
                    else:
                        print(f"\n🏆 현재 최고 점수: {self.best_score}점")
                    input("\n엔터를 누르면 메뉴로 돌아갑니다...") # 점수 확인 후 멈춤 필요
                elif choice == '5':
                    print("재밌게 즐기셨나요? 게임을 종료합니다!")
                    break
                else:
                   # [요구사항] 허용 범위 밖 숫자 처리
                   print("⚠️ 잘못된 선택입니다. 1~5번 메뉴를 선택해주세요.")
                   input("\n엔터를 누르면 메뉴로 돌아갑니다...")

        except (KeyboardInterrupt, EOFError):
            # [요구사항 3] Ctrl+C 또는 강제종료 처리
            print("\n\n⚠️ 비정상 종료 감지: 데이터를 안전하게 저장하고 종료합니다.")
            self.save_data()
            sys.exit(0)

if __name__ == "__main__":
    game = QuizGame()
    game.run()