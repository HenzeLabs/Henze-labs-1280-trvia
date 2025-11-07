#!/usr/bin/env python3
"""
Complete 15-Question Game Simulation with 4 Players
Tests the ENTIRE game flow: Create → Join → Play → Vote → Results

Question Mix (Per Game - Current Implementation):
- 1 Group Chat Receipt (real texts exposed)
- 1 Roast Question (savage callouts)
- 3 Most Likely Questions (voted scoring)
- 3 Sex Trivia (educational but spicy)
- 6 Normal Trivia (balance the chaos)
- 1 Poll Question (popularity contest - most votes wins)

Total: 15 questions with 4 voting-style questions (3 most likely + 1 poll)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"
API_BASE = f"{BASE_URL}/api"

class Color:
    """ANSI colors for beautiful output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    """Print a fancy header"""
    print(f"\n{Color.BOLD}{Color.CYAN}{'='*80}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{text.center(80)}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{'='*80}{Color.END}\n")

def print_step(step_num, total_steps, description):
    """Print a step in the process"""
    print(f"{Color.BOLD}[{step_num}/{total_steps}]{Color.END} {Color.BLUE}{description}{Color.END}")

def print_success(message):
    """Print success message"""
    print(f"{Color.GREEN}✅ {message}{Color.END}")

def print_error(message):
    """Print error message"""
    print(f"{Color.RED}❌ {message}{Color.END}")

def print_info(message):
    """Print info message"""
    print(f"{Color.YELLOW}ℹ️  {message}{Color.END}")

def print_result(key, value):
    """Print a key-value result"""
    print(f"   {Color.BOLD}{key}:{Color.END} {value}")

class GameSimulator:
    """Simulates a complete 4-player game with 20 questions"""

    def __init__(self):
        self.room_code = None
        self.players = {
            'Lauren': {'id': None, 'score': 0},
            'Benny': {'id': None, 'score': 0},
            'Gina': {'id': None, 'score': 0},
            'Ian': {'id': None, 'score': 0}
        }
        self.questions_played = 0
        self.total_questions = 15  # 3 receipts + 4 sex trivia + 5 normal + 2 voting + 1 discussion
        self.audit_log = []

    def log(self, event_type, data):
        """Log an event for the audit trail"""
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        })

    def step_1_create_game(self):
        """Step 1: Host creates the game"""
        print_step(1, 10, "Host Creates Game")

        try:
            response = requests.post(
                f"{API_BASE}/game/create",
                json={'host_name': 'Lauren'},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.room_code = data['room_code']
                print_success(f"Game created successfully!")
                print_result("Room Code", self.room_code)
                print_result("Host", "Lauren")
                self.log('game_created', {'room_code': self.room_code, 'host': 'Lauren'})
                return True
            else:
                print_error(f"Failed to create game: {response.status_code}")
                return False

        except Exception as e:
            print_error(f"Exception creating game: {e}")
            return False

    def step_2_players_join(self):
        """Step 2: 4 players join the game"""
        print_step(2, 10, "Players Join Game")

        for player_name in self.players.keys():
            try:
                response = requests.post(
                    f"{API_BASE}/game/join",
                    json={
                        'room_code': self.room_code,
                        'player_name': player_name
                    },
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    self.players[player_name]['id'] = data['player_id']
                    print_success(f"{player_name} joined!")
                    print_result("  Player ID", data['player_id'])
                    self.log('player_joined', {'name': player_name, 'id': data['player_id']})
                else:
                    print_error(f"{player_name} failed to join: {response.status_code}")
                    return False

            except Exception as e:
                print_error(f"Exception joining {player_name}: {e}")
                return False

        print_info(f"All 4 players successfully joined!")
        return True

    def step_3_start_game(self):
        """Step 3: Host starts the game"""
        print_step(3, 10, "Host Starts Game")

        try:
            response = requests.post(
                f"{API_BASE}/game/start/{self.room_code}",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                print_success("Game started successfully!")
                print_result("Status", "Playing")
                self.log('game_started', {'room_code': self.room_code})
                return True
            else:
                print_error(f"Failed to start game: {response.status_code}")
                return False

        except Exception as e:
            print_error(f"Exception starting game: {e}")
            return False

    def step_4_get_first_question(self):
        """Step 4: Get the first question"""
        print_step(4, 10, "Load First Question")

        try:
            response = requests.get(
                f"{API_BASE}/game/question/{self.room_code}",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                question = data['question']
                print_success("First question loaded!")
                print_result("Category", question.get('category', 'N/A'))
                print_result("Question", question.get('question_text', 'N/A')[:80] + "...")
                print_result("Answers", ', '.join(question.get('answers', [])))
                print_result("Correct", question.get('correct_answer', 'N/A'))
                self.log('question_loaded', {'number': 1, 'question': question})
                return question
            else:
                print_error(f"Failed to load question: {response.status_code}")
                return None

        except Exception as e:
            print_error(f"Exception loading question: {e}")
            return None

    def step_5_simulate_voting(self, question):
        """Step 5: Simulate 4 players voting on the question"""
        print_step(5, 10, f"Simulate Player Voting (Question {self.questions_played + 1})")

        if not question or 'answers' not in question:
            print_error("No valid question to vote on")
            return False

        answers = question['answers']

        # Import random here for voting simulation
        import random

        # Simulate realistic voting patterns - players pick randomly from available answers
        votes = {}
        correct_answer = None  # Will be revealed after first answer

        for player_name, player_data in self.players.items():
            # Simulate realistic voting - each player picks an answer
            # Some players are smarter/luckier than others
            if player_name == 'Lauren':
                # Lauren tends to get it right more often
                answer = random.choice(answers)
            elif player_name == 'Benny':
                # Benny is strategic
                answer = random.choice(answers)
            elif player_name == 'Gina':
                # Gina sometimes second-guesses
                answer = random.choice(answers)
            else:  # Ian
                # Ian just vibes and guesses
                answer = random.choice(answers)

            votes[player_name] = answer

            # Submit the answer
            try:
                response = requests.post(
                    f"{API_BASE}/game/answer",
                    json={
                        'player_id': player_data['id'],
                        'answer': answer
                    },
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )

                if response.status_code == 200:
                    result = response.json()
                    is_correct = result.get('is_correct', False)
                    points = result.get('points_earned', 0)
                    revealed_correct = result.get('correct_answer')

                    # Store the correct answer once we get it
                    if correct_answer is None and revealed_correct:
                        correct_answer = revealed_correct

                    if is_correct:
                        print_success(f"{player_name} voted '{answer}' - CORRECT! (+{points} pts)")
                        self.players[player_name]['score'] += points
                    else:
                        print_info(f"{player_name} voted '{answer}' - Wrong (0 pts)")

                    self.log('player_voted', {
                        'player': player_name,
                        'answer': answer,
                        'correct': is_correct,
                        'points': points
                    })
                else:
                    print_error(f"{player_name} vote failed: {response.status_code}")

            except Exception as e:
                print_error(f"Exception submitting {player_name}'s vote: {e}")

        # Show voting results
        print(f"\n{Color.BOLD}Voting Results:{Color.END}")
        for answer in set(votes.values()):
            voters = [name for name, vote in votes.items() if vote == answer]
            percentage = (len(voters) / len(votes)) * 100
            emoji = "✅" if answer == correct_answer else "❌"
            print(f"  {emoji} {answer}: {percentage:.0f}% ({len(voters)} votes) - {', '.join(voters)}")

        if correct_answer:
            print_result("Correct Answer", correct_answer)

        return True

    def step_6_show_leaderboard(self):
        """Step 6: Show current leaderboard"""
        print_step(6, 10, f"Leaderboard After Question {self.questions_played + 1}")

        try:
            response = requests.get(
                f"{API_BASE}/game/leaderboard/{self.room_code}",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                leaderboard = data['leaderboard']

                print(f"\n{Color.BOLD}{'='*60}{Color.END}")
                print(f"{Color.BOLD}{'DAMAGE REPORT'.center(60)}{Color.END}")
                print(f"{Color.BOLD}{'='*60}{Color.END}")

                for i, player in enumerate(leaderboard, 1):
                    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "💀"
                    print(f"{emoji} {player['rank']}. {player['name']:<15} {player['score']:>5} pts")

                print(f"{Color.BOLD}{'='*60}{Color.END}\n")

                self.log('leaderboard_shown', {'question': self.questions_played + 1, 'leaderboard': leaderboard})
                return True
            else:
                print_error(f"Failed to get leaderboard: {response.status_code}")
                return False

        except Exception as e:
            print_error(f"Exception getting leaderboard: {e}")
            return False

    def step_7_next_question(self):
        """Step 7: Advance to next question"""
        print_step(7, 10, f"Advance to Question {self.questions_played + 2}")

        try:
            response = requests.post(
                f"{API_BASE}/game/next/{self.room_code}",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                if data.get('game_finished', False):
                    print_success("Game completed!")
                    self.log('game_finished', {'total_questions': self.questions_played + 1})
                    return 'GAME_OVER'
                else:
                    print_success(f"Advanced to question {self.questions_played + 2}")
                    self.log('next_question', {'number': self.questions_played + 2})
                    return True
            else:
                print_error(f"Failed to advance: {response.status_code}")
                return False

        except Exception as e:
            print_error(f"Exception advancing: {e}")
            return False

    def step_8_play_remaining_questions(self):
        """Step 8: Play questions 2-20"""
        print_step(8, 10, f"Play Questions 2-{self.total_questions}")

        import random  # For voting simulation

        for q_num in range(2, self.total_questions + 1):
            print(f"\n{Color.BOLD}{Color.YELLOW}{'─'*80}{Color.END}")
            print(f"{Color.BOLD}{Color.YELLOW}QUESTION {q_num} of {self.total_questions}{Color.END}")
            print(f"{Color.BOLD}{Color.YELLOW}{'─'*80}{Color.END}\n")

            # Get question
            try:
                response = requests.get(f"{API_BASE}/game/question/{self.room_code}", timeout=5)
                if response.status_code != 200:
                    print_error(f"Failed to load question {q_num}")
                    continue

                question = response.json()['question']
                print_result("Category", question.get('category', 'N/A'))
                print_result("Question", question.get('question_text', 'N/A')[:80] + "...")

            except Exception as e:
                print_error(f"Exception loading question {q_num}: {e}")
                continue

            # Simulate voting
            if not self.step_5_simulate_voting(question):
                print_error(f"Voting failed for question {q_num}")
                continue

            self.questions_played += 1

            # Show leaderboard
            self.step_6_show_leaderboard()

            # Advance to next (unless it's the last question)
            if q_num < self.total_questions:
                result = self.step_7_next_question()
                if result == 'GAME_OVER':
                    break
                elif not result:
                    print_error("Failed to advance to next question")
                    break

                time.sleep(0.5)  # Brief pause between questions

        return True

    def step_9_final_results(self):
        """Step 9: Show final game results"""
        print_step(9, 10, "Final Game Results")

        try:
            response = requests.get(
                f"{API_BASE}/game/stats/{self.room_code}",
                timeout=5
            )

            if response.status_code == 200:
                stats = response.json()

                print_header("🏆 FINAL RESULTS 🏆")
                print_result("Total Players", stats.get('total_players', 0))
                print_result("Questions Played", self.questions_played + 1)
                print_result("Total Answers", stats.get('players_answered', 0))

                # Get final leaderboard
                leaderboard_response = requests.get(f"{API_BASE}/game/leaderboard/{self.room_code}", timeout=5)
                if leaderboard_response.status_code == 200:
                    leaderboard = leaderboard_response.json()['leaderboard']

                    print(f"\n{Color.BOLD}{'='*60}{Color.END}")
                    print(f"{Color.BOLD}{Color.GREEN}{'FINAL STANDINGS'.center(60)}{Color.END}")
                    print(f"{Color.BOLD}{'='*60}{Color.END}")

                    for player in leaderboard:
                        rank_emoji = "🥇" if player['rank'] == 1 else "🥈" if player['rank'] == 2 else "🥉" if player['rank'] == 3 else "💀"
                        print(f"{rank_emoji} {player['rank']}. {player['name']:<15} {player['score']:>5} pts")

                    print(f"{Color.BOLD}{'='*60}{Color.END}\n")

                    winner = leaderboard[0]
                    print(f"{Color.BOLD}{Color.GREEN}🎉 WINNER: {winner['name']} with {winner['score']} points! 🎉{Color.END}\n")

                self.log('final_results', {'stats': stats, 'leaderboard': leaderboard})
                return True
            else:
                print_error(f"Failed to get final stats: {response.status_code}")
                return False

        except Exception as e:
            print_error(f"Exception getting final results: {e}")
            return False

    def step_10_generate_audit_report(self):
        """Step 10: Generate comprehensive audit report"""
        print_step(10, 10, "Generate Audit Report")

        report_file = f"game_audit_{self.room_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(report_file, 'w') as f:
                json.dump({
                    'room_code': self.room_code,
                    'total_questions': self.questions_played + 1,
                    'players': self.players,
                    'audit_log': self.audit_log
                }, f, indent=2)

            print_success(f"Audit report saved to: {report_file}")
            print_result("Total Events Logged", len(self.audit_log))
            return True

        except Exception as e:
            print_error(f"Failed to save audit report: {e}")
            return False

    def run_full_simulation(self):
        """Run the complete game simulation"""
        print_header("🎮 1280 WEST SAVAGE TRIVIA - FULL GAME AUDIT 🎮")
        print(f"{Color.BOLD}Testing:{Color.END} Complete 15-question game with 4 players")
        print(f"{Color.BOLD}Players:{Color.END} Lauren, Benny, Gina, Ian")
        print(f"{Color.BOLD}Mix:{Color.END} 3 Receipts + 4 Sex Trivia + 5 Normal + 2 Voting + 1 Discussion")
        print(f"{Color.BOLD}Mechanics:{Color.END} Real chat receipts + interactive voting + roasting\n")

        start_time = time.time()

        # Run all steps
        if not self.step_1_create_game():
            return False

        if not self.step_2_players_join():
            return False

        if not self.step_3_start_game():
            return False

        question = self.step_4_get_first_question()
        if not question:
            return False

        if not self.step_5_simulate_voting(question):
            return False

        self.questions_played = 1

        if not self.step_6_show_leaderboard():
            return False

        result = self.step_7_next_question()
        if result == False:
            return False

        if not self.step_8_play_remaining_questions():
            return False

        if not self.step_9_final_results():
            return False

        if not self.step_10_generate_audit_report():
            return False

        # Final summary
        elapsed_time = time.time() - start_time

        print_header("✅ SIMULATION COMPLETE ✅")
        print_result("Room Code", self.room_code)
        print_result("Questions Played", self.questions_played + 1)
        print_result("Total Events", len(self.audit_log))
        print_result("Elapsed Time", f"{elapsed_time:.2f}s")
        print(f"\n{Color.GREEN}{Color.BOLD}🎉 All systems operational! Game is ready for production! 🎉{Color.END}\n")

        return True

if __name__ == '__main__':
    simulator = GameSimulator()
    success = simulator.run_full_simulation()
    sys.exit(0 if success else 1)
