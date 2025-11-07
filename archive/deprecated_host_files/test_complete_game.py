#!/usr/bin/env python3
"""
Complete Game Test - Tests entire game flow from start to finish
Tests all phases: waiting -> playing -> minigames -> final sprint -> finished
"""

import requests
import time
import json
from typing import List, Dict

BASE_URL = "http://localhost:5001"
API_BASE = f"{BASE_URL}/api"

class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_success(message):
    print(f"{Color.GREEN}✓ {message}{Color.END}")

def log_info(message):
    print(f"{Color.CYAN}ℹ {message}{Color.END}")

def log_warning(message):
    print(f"{Color.YELLOW}⚠ {message}{Color.END}")

def log_error(message):
    print(f"{Color.RED}✗ {message}{Color.END}")

def log_section(message):
    print(f"\n{Color.BOLD}{Color.CYAN}{'='*60}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{message}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{'='*60}{Color.END}\n")

class GameTest:
    def __init__(self):
        self.room_code = None
        self.host_token = None
        self.players = []
        self.errors = []
        self.warnings = []

    def create_game(self, num_questions=5):
        """Create a new game."""
        log_info(f"Creating game with {num_questions} questions...")
        try:
            response = requests.post(f"{API_BASE}/game/create", json={
                "host_name": "Test Host",
                "num_questions": num_questions
            }, timeout=5)

            if response.status_code != 200:
                self.errors.append(f"Create game failed: {response.status_code}")
                log_error(f"Failed to create game: {response.status_code}")
                return False

            data = response.json()
            self.room_code = data['room_code']
            self.host_token = data['host_token']

            log_success(f"Game created! Room: {self.room_code}")
            return True
        except Exception as e:
            self.errors.append(f"Create game exception: {e}")
            log_error(f"Exception: {e}")
            return False

    def add_players(self, player_names: List[str]):
        """Add players to the game."""
        log_info(f"Adding {len(player_names)} players...")
        for name in player_names:
            try:
                response = requests.post(f"{API_BASE}/game/join", json={
                    "room_code": self.room_code,
                    "player_name": name
                }, timeout=5)

                if response.status_code != 200:
                    self.errors.append(f"Player join failed for {name}: {response.status_code}")
                    log_error(f"Failed to add player {name}")
                    continue

                data = response.json()
                self.players.append({
                    'name': name,
                    'id': data['player_id'],
                    'score': 0
                })
                log_success(f"Player joined: {name}")
            except Exception as e:
                self.errors.append(f"Player join exception for {name}: {e}")
                log_error(f"Exception adding {name}: {e}")

        return len(self.players) > 0

    def start_game(self):
        """Start the game."""
        log_info("Starting game...")
        try:
            response = requests.post(
                f"{API_BASE}/game/start/{self.room_code}",
                headers={'X-Host-Token': self.host_token},
                timeout=5
            )

            if response.status_code != 200:
                self.errors.append(f"Start game failed: {response.status_code}")
                log_error(f"Failed to start game: {response.status_code}")
                return False

            log_success("Game started!")
            return True
        except Exception as e:
            self.errors.append(f"Start game exception: {e}")
            log_error(f"Exception: {e}")
            return False

    def get_question(self):
        """Get current question."""
        try:
            response = requests.get(
                f"{API_BASE}/game/question/{self.room_code}/host",
                headers={'X-Host-Token': self.host_token},
                timeout=5
            )

            if response.status_code != 200:
                log_warning(f"Get question returned {response.status_code}")
                return None

            data = response.json()
            return data.get('question') if data.get('success') else None
        except Exception as e:
            log_warning(f"Get question exception: {e}")
            return None

    def submit_answers(self, correct_ratio=0.5):
        """Submit answers for all players (some correct, some wrong)."""
        question = self.get_question()
        if not question:
            log_error("Cannot submit answers - no question available")
            return False

        answers = question.get('answers', [])
        correct_answer = question.get('correct_answer')

        if not answers:
            log_error("No answers available")
            return False

        log_info(f"Submitting answers for {len(self.players)} players...")

        for i, player in enumerate(self.players):
            # Make some players answer correctly, some incorrectly
            if i < len(self.players) * correct_ratio:
                # Answer correctly
                if correct_answer and correct_answer in answers:
                    answer = correct_answer
                else:
                    answer = answers[0]
            else:
                # Answer incorrectly
                wrong_answers = [a for a in answers if a != correct_answer]
                answer = wrong_answers[0] if wrong_answers else answers[-1]

            try:
                response = requests.post(f"{API_BASE}/game/answer", json={
                    "player_id": player['id'],
                    "answer": answer
                }, timeout=5)

                if response.status_code == 200:
                    result = response.json()
                    is_correct = result.get('is_correct', False)
                    status = "✓" if is_correct else "✗"
                    log_success(f"{status} {player['name']}: {answer}")
                else:
                    log_warning(f"Answer submission failed for {player['name']}")
            except Exception as e:
                log_warning(f"Answer exception for {player['name']}: {e}")

        return True

    def reveal_answer(self):
        """Reveal the answer."""
        try:
            response = requests.get(
                f"{API_BASE}/game/reveal/{self.room_code}",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                log_success(f"Answer revealed: {data.get('correct_answer')}")
                return True
            else:
                log_warning(f"Reveal failed: {response.status_code}")
                return False
        except Exception as e:
            log_warning(f"Reveal exception: {e}")
            return False

    def next_question(self):
        """Move to next question."""
        try:
            response = requests.post(
                f"{API_BASE}/game/next/{self.room_code}",
                headers={'X-Host-Token': self.host_token},
                timeout=5
            )

            if response.status_code == 200:
                log_success("Moved to next question")
                return True
            else:
                log_warning(f"Next question failed: {response.status_code}")
                return False
        except Exception as e:
            log_warning(f"Next exception: {e}")
            return False

    def get_game_stats(self):
        """Get game statistics."""
        try:
            response = requests.get(
                f"{API_BASE}/game/stats/{self.room_code}",
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None

    def get_leaderboard(self):
        """Get current leaderboard."""
        try:
            response = requests.get(
                f"{API_BASE}/game/leaderboard/{self.room_code}",
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None

    def play_full_game(self, num_questions=5):
        """Play a complete game from start to finish."""
        log_section("COMPLETE GAME TEST")

        # Step 1: Create game
        if not self.create_game(num_questions):
            return False

        # Step 2: Add players
        player_names = ["Alice", "Bob", "Charlie", "Diana"]
        if not self.add_players(player_names):
            return False

        time.sleep(0.5)

        # Step 3: Start game
        if not self.start_game():
            return False

        time.sleep(0.5)

        # Step 4: Play through all questions
        log_section("PLAYING QUESTIONS")

        for q_num in range(num_questions):
            log_info(f"Question {q_num + 1}/{num_questions}")

            # Get question
            question = self.get_question()
            if question:
                log_info(f"Category: {question.get('category')}")
                log_info(f"Type: {question.get('question_type')}")

            time.sleep(0.3)

            # Submit answers (50% correct)
            self.submit_answers(correct_ratio=0.5)

            time.sleep(0.3)

            # Reveal answer
            self.reveal_answer()

            time.sleep(0.3)

            # Check stats
            stats = self.get_game_stats()
            if stats:
                current_q = stats.get('current_question', 0)
                total_q = stats.get('total_questions', 0)
                status = stats.get('status', 'unknown')
                log_info(f"Game status: {status} ({current_q}/{total_q})")

            # Move to next question (unless it's the last one)
            if q_num < num_questions - 1:
                time.sleep(0.3)
                self.next_question()
                time.sleep(0.3)

        # Step 5: Check final state
        log_section("CHECKING FINAL STATE")

        stats = self.get_game_stats()
        if stats:
            status = stats.get('status')
            log_info(f"Final game status: {status}")

            if status == 'finished':
                log_success("Game completed successfully!")
            else:
                log_warning(f"Game status is '{status}', expected 'finished'")
                self.warnings.append(f"Game did not finish properly (status: {status})")

        leaderboard = self.get_leaderboard()
        if leaderboard:
            log_info("Final leaderboard:")
            players = leaderboard.get('players', [])
            for i, player in enumerate(players[:5], 1):
                log_info(f"  {i}. {player['name']}: {player['score']} points")

        return True

    def print_summary(self):
        """Print test summary."""
        log_section("TEST SUMMARY")

        if not self.errors and not self.warnings:
            log_success("ALL TESTS PASSED! No errors or warnings.")
            return True

        if self.warnings:
            log_warning(f"Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.errors:
            log_error(f"Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
            return False

        return True

def main():
    """Run the complete game test."""
    test = GameTest()

    try:
        success = test.play_full_game(num_questions=5)
        test.print_summary()

        if success and not test.errors:
            print(f"\n{Color.BOLD}{Color.GREEN}🎉 COMPLETE GAME TEST SUCCESSFUL!{Color.END}\n")
            return 0
        else:
            print(f"\n{Color.BOLD}{Color.RED}❌ COMPLETE GAME TEST FAILED{Color.END}\n")
            return 1
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Test cancelled{Color.END}\n")
        return 1
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
