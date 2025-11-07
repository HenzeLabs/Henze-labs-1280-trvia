#!/usr/bin/env python3
"""
Interactive Terminal Game - Play 1280 Trivia in the terminal!
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"
API_BASE = f"{BASE_URL}/api"

class Color:
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
    print(f"\n{Color.BOLD}{Color.CYAN}{'='*80}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{text.center(80)}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{'='*80}{Color.END}\n")

def print_question(q_num, total, category, question):
    print(f"\n{Color.BOLD}Question {q_num}/{total}{Color.END}")
    print(f"{Color.YELLOW}Category: {category}{Color.END}")
    print(f"\n{Color.BOLD}{question}{Color.END}\n")

def print_answer(letter, text, is_selected=False, is_correct=False, is_wrong=False):
    prefix = f"{Color.BOLD}{letter}){Color.END}"

    if is_correct:
        print(f"  {prefix} {Color.GREEN}{text} ✓{Color.END}")
    elif is_wrong:
        print(f"  {prefix} {Color.RED}{text} ✗{Color.END}")
    elif is_selected:
        print(f"  {prefix} {Color.CYAN}{text} ←{Color.END}")
    else:
        print(f"  {prefix} {text}")

def play_game():
    print_header("🎮 1280 TRIVIA - TERMINAL EDITION")

    # Get player name
    player_name = input(f"{Color.BOLD}Enter your name: {Color.END}").strip()
    if not player_name:
        player_name = "Player"

    # Create game with 5 questions for quick play
    print(f"\n{Color.CYAN}Creating game...{Color.END}")
    try:
        response = requests.post(f"{API_BASE}/game/create", json={
            "host_name": "Terminal Host",
            "num_questions": 5  # Quick 5-question game
        })
        data = response.json()
        room_code = data['room_code']
        host_token = data['host_token']

        print(f"{Color.GREEN}✓ Game created! Room code: {Color.BOLD}{room_code}{Color.END}")
    except Exception as e:
        print(f"{Color.RED}Error creating game: {e}{Color.END}")
        return

    # Join as player
    print(f"{Color.CYAN}Joining game...{Color.END}")
    try:
        response = requests.post(f"{API_BASE}/game/join", json={
            "room_code": room_code,
            "player_name": player_name
        })
        data = response.json()
        player_id = data['player_id']

        print(f"{Color.GREEN}✓ Joined as {Color.BOLD}{player_name}{Color.END}")
    except Exception as e:
        print(f"{Color.RED}Error joining game: {e}{Color.END}")
        return

    # Start game
    print(f"{Color.CYAN}Starting game...{Color.END}")
    try:
        response = requests.post(
            f"{API_BASE}/game/start/{room_code}",
            headers={'X-Host-Token': host_token}
        )
        print(f"{Color.GREEN}✓ Game started!{Color.END}")
    except Exception as e:
        print(f"{Color.RED}Error starting game: {e}{Color.END}")
        return

    # Play through questions
    score = 0
    total_questions = 5

    for q_num in range(1, total_questions + 1):
        # Get question
        try:
            response = requests.get(f"{API_BASE}/game/question/{room_code}/player/{player_id}")
            question_data = response.json()

            category = question_data['category']
            question_text = question_data['question_text']
            answers = question_data['answers']

            print_question(q_num, total_questions, category, question_text)

            # Display answers
            letters = ['A', 'B', 'C', 'D']
            for i, answer in enumerate(answers):
                print_answer(letters[i], answer)

            # Get player's answer
            while True:
                user_input = input(f"\n{Color.BOLD}Your answer (A/B/C/D): {Color.END}").strip().upper()
                if user_input in ['A', 'B', 'C', 'D']:
                    break
                print(f"{Color.RED}Please enter A, B, C, or D{Color.END}")

            # Submit answer
            answer_index = ord(user_input) - ord('A')
            selected_answer = answers[answer_index]

            response = requests.post(f"{API_BASE}/game/answer", json={
                "player_id": player_id,
                "answer": selected_answer
            })
            result = response.json()

            # Show result
            print()
            if result.get('is_poll'):
                print(f"{Color.CYAN}🗳️  Vote recorded! (Poll questions don't have right/wrong answers){Color.END}")
            elif result.get('is_correct'):
                points = result.get('points_earned', 0)
                score += points
                print(f"{Color.GREEN}✅ CORRECT! +{points} points{Color.END}")
            else:
                correct = result.get('correct_answer', '')
                print(f"{Color.RED}❌ Wrong! Correct answer: {correct}{Color.END}")

            print(f"\n{Color.BOLD}Current Score: {score} points{Color.END}")

            # Advance to next question (host action)
            if q_num < total_questions:
                input(f"\n{Color.CYAN}Press Enter for next question...{Color.END}")
                requests.post(
                    f"{API_BASE}/game/next/{room_code}",
                    headers={'X-Host-Token': host_token}
                )

        except Exception as e:
            print(f"{Color.RED}Error: {e}{Color.END}")
            break

    # Show final results
    print_header("🏆 GAME COMPLETE")

    try:
        response = requests.get(f"{API_BASE}/game/summary/{room_code}")
        summary = response.json()

        print(f"{Color.BOLD}Final Score: {Color.GREEN}{score} points{Color.END}")
        print(f"{Color.CYAN}Total Questions: {total_questions}{Color.END}")
        print(f"{Color.CYAN}Questions Answered Correctly: {score // 100}{Color.END}")  # Rough estimate

    except Exception as e:
        print(f"{Color.BOLD}Final Score: {Color.GREEN}{score} points{Color.END}")

    print(f"\n{Color.BOLD}Thanks for playing 1280 Trivia!{Color.END}\n")
    print(f"{Color.CYAN}💡 To play with friends, visit: {Color.BOLD}http://localhost:5001{Color.END}\n")

if __name__ == '__main__':
    try:
        play_game()
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}Game cancelled. Thanks for playing!{Color.END}\n")
    except Exception as e:
        print(f"\n{Color.RED}Error: {e}{Color.END}\n")
