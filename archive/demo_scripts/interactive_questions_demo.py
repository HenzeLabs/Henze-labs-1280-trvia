#!/usr/bin/env python3
"""
🗳️ INTERACTIVE 1280 WEST QUESTION TYPES 🗳️
New question types that require player interaction and voting
"""

class InteractiveQuestionHandler:
    """Handles interactive voting and discussion questions."""
    
    def __init__(self):
        self.friends = ['Lauren', 'Benny', 'Gina', 'Ian']
    
    def handle_most_likely_voting(self, question_data):
        """
        Handle 'Most Likely To' voting questions.
        Everyone votes secretly, then results are revealed.
        """
        return {
            'interaction_type': 'voting',
            'question_text': question_data['question_text'],
            'voting_options': self.friends,
            'instructions': [
                "📱 Everyone opens their phone",
                "🗳️ Vote for who this applies to most",
                "🤐 Voting is anonymous (for now...)",
                "📊 Results revealed after everyone votes",
                "💀 Prepare for drama when results show!"
            ],
            'reveal_format': {
                'show_percentages': True,
                'show_vote_counts': True,
                'allow_discussion': True,
                'roast_winner': True
            }
        }
    
    def handle_would_you_rather_discussion(self, question_data):
        """
        Handle 'Would You Rather' discussion questions.
        Everyone picks A or B and explains their choice.
        """
        return {
            'interaction_type': 'discussion',
            'question_text': question_data['question_text'],
            'option_a': question_data['option_a'],
            'option_b': question_data['option_b'],
            'instructions': [
                "🗣️ Everyone discusses out loud",
                "✋ Go around the room and pick A or B",
                "💭 Explain your reasoning (this is the fun part)",
                "😱 Judge each other's choices",
                "🔥 Roast anyone with a questionable answer"
            ],
            'discussion_format': {
                'time_limit': '5 minutes of chaos',
                'allow_arguments': True,
                'require_explanation': True,
                'roast_level': 'maximum'
            }
        }

def demo_interactive_questions():
    """Demo the new interactive question types."""
    print("🗳️ 1280 WEST INTERACTIVE QUESTION DEMO 🗳️")
    print("=" * 60)
    
    handler = InteractiveQuestionHandler()
    
    # Demo Most Likely To Voting
    print("📊 MOST LIKELY TO VOTING QUESTION:")
    print("-" * 40)
    
    voting_question = {
        'question_text': "Who is most likely to have a secret affair?",
        'category': 'DIRTY MOST LIKELY TO',
        'savage_level': 6
    }
    
    voting_result = handler.handle_most_likely_voting(voting_question)
    
    print(f"❓ {voting_result['question_text']}")
    print("\n🗳️ VOTING PROCESS:")
    for i, instruction in enumerate(voting_result['instructions'], 1):
        print(f"   {i}. {instruction}")
    
    print(f"\n👥 Voting Options:")
    for i, option in enumerate(voting_result['voting_options'], 1):
        print(f"   {i}. {option}")
    
    print("\n📊 RESULTS REVEAL FORMAT:")
    print("   ✅ Show vote percentages")
    print("   ✅ Show vote counts") 
    print("   ✅ Allow post-results discussion")
    print("   ✅ Roast the 'winner'")
    
    print("\n" + "=" * 60)
    
    # Demo Would You Rather Discussion
    print("🗣️ WOULD YOU RATHER DISCUSSION QUESTION:")
    print("-" * 40)
    
    discussion_question = {
        'question_text': "Would you rather have your browser history made public or your text messages made public?",
        'option_a': "Browser history public",
        'option_b': "Text messages public",
        'savage_level': 5
    }
    
    discussion_result = handler.handle_would_you_rather_discussion(discussion_question)
    
    print(f"❓ {discussion_result['question_text']}")
    print(f"\n   A) {discussion_result['option_a']}")
    print(f"   B) {discussion_result['option_b']}")
    
    print("\n💬 DISCUSSION PROCESS:")
    for i, instruction in enumerate(discussion_result['instructions'], 1):
        print(f"   {i}. {instruction}")
    
    print("\n🔥 DISCUSSION RULES:")
    print(f"   ⏰ Time limit: {discussion_result['discussion_format']['time_limit']}")
    print(f"   🥊 Arguments allowed: {discussion_result['discussion_format']['allow_arguments']}")
    print(f"   📝 Must explain choice: {discussion_result['discussion_format']['require_explanation']}")
    print(f"   🔥 Roast level: {discussion_result['discussion_format']['roast_level']}")
    
    print("\n🎯 INTERACTIVE QUESTION BENEFITS:")
    print("=" * 60)
    print("💀 More personal and targeted roasting")
    print("🗳️ Anonymous voting creates suspense")
    print("💬 Discussion questions spark debates")
    print("📊 Vote results show group dynamics") 
    print("🔥 Higher engagement than multiple choice")
    print("😈 More opportunities for savage moments")
    print("🎭 Creates memorable game moments")

def show_sample_voting_results():
    """Show what voting results would look like with 4 players."""
    print("\n📊 SAMPLE VOTING RESULTS:")
    print("=" * 60)
    print("Question: 'Who is most likely to have a secret affair?'")
    print("Players: Lauren, Benny, Gina, Ian (4 total votes)")
    print()
    print("🗳️ VOTING RESULTS:")
    print("   1. Lauren: ████████ 50% (2 votes)")
    print("   2. Benny: ██████ 25% (1 vote)")
    print("   3. Gina: ██████ 25% (1 vote)")
    print("   4. Ian: ░ 0% (0 votes)")
    print()
    print("🔥 ROAST PHASE ACTIVATED:")
    print("   💀 Lauren gets roasted for 'winning' with 2 votes")
    print("   😱 Everyone explains their votes")
    print("   🤔 Who were the 2 people that voted for Lauren?")
    print("   💥 Maximum drama achieved")
    print()
    print("🎯 Post-voting discussion topics:")
    print("   - Why did Lauren get the most votes?")
    print("   - Who voted for Lauren and why?")
    print("   - Benny and Gina tied with 1 vote each - awkward!")
    print("   - Poor Ian got zero votes (is he that innocent?)")
    print("   - Did anyone vote for themselves?")
    print()
    print("🎮 ALTERNATIVE RESULTS SCENARIO:")
    print("   🗳️ TIED RESULTS (2-2 split):")
    print("   1. Lauren: ████████ 50% (2 votes)")
    print("   2. Benny: ████████ 50% (2 votes)")
    print("   3. Gina: ░ 0% (0 votes)")
    print("   4. Ian: ░ 0% (0 votes)")
    print("   💥 TIE = DOUBLE ROASTING for Lauren & Benny!")

if __name__ == "__main__":
    demo_interactive_questions()
    show_sample_voting_results()