#!/usr/bin/env python3
"""
🕵️ 1280 WEST FRIEND GROUP INTEL GATHERING 🕵️
Strategic questions to improve game content without spoiling gameplay
"""

def gather_friend_intel():
    """Ask strategic questions about the friend group to improve content."""
    
    print("🕵️ 1280 WEST FRIEND GROUP INTEL GATHERING 🕵️")
    print("=" * 60)
    print("I'll ask you questions about your friend group to make better")
    print("trivia content WITHOUT spoiling the actual game questions!")
    print()
    
    intel_questions = [
        # Personality traits for "Most Likely To" questions
        {
            'category': 'PERSONALITY TRAITS',
            'questions': [
                "Who's the most impulsive with money/shopping?",
                "Who takes the longest to respond to group plans?", 
                "Who's most likely to overshare personal details?",
                "Who gets hangry (angry when hungry) the most?",
                "Who's the most paranoid about germs/cleanliness?",
                "Who complains about work the most?",
                "Who's most likely to cancel plans last minute?",
                "Who has the messiest living space?",
                "Who's most likely to start drama accidentally?",
                "Who's the worst at keeping secrets?"
            ]
        },
        
        # Dating/relationship patterns
        {
            'category': 'DATING & RELATIONSHIPS',
            'questions': [
                "Who has the worst taste in dating partners?",
                "Who falls for people too quickly?",
                "Who's most likely to drunk text an ex?",
                "Who gives the worst dating advice?",
                "Who's most likely to stalk someone on social media?",
                "Who's most picky about potential dates?",
                "Who's most likely to have a one night stand?",
                "Who overshares about their sex life?",
                "Who's most likely to cheat (hypothetically)?",
                "Who's most desperate to find a relationship?"
            ]
        },
        
        # Social habits & quirks
        {
            'category': 'SOCIAL HABITS',
            'questions': [
                "Who's the lightweight when drinking?",
                "Who makes the worst decisions when drunk?",
                "Who's most likely to embarrass themselves in public?",
                "Who talks the most in group settings?",
                "Who's most likely to start a fight when drunk?",
                "Who's the most judgmental about others?",
                "Who's most likely to hook up with a friend's ex?",
                "Who's most likely to get kicked out of somewhere?",
                "Who's the worst influence on the group?",
                "Who's most likely to get arrested?"
            ]
        },
        
        # 1280 West specific
        {
            'category': '1280 WEST BUILDING LIFE',
            'questions': [
                "Who's had the most awkward elevator encounters?",
                "Who's most likely to complain to the HOA?",
                "Who's brought home the most questionable dates?",
                "Who's most likely to have loud sex that neighbors hear?",
                "Who's most paranoid about building security?",
                "Who uses the gym the least (if there is one)?",
                "Who's most likely to get noise complaints?",
                "Who hoards the most packages in their apartment?",
                "Who's most likely to hook up with someone in the building?",
                "Who knows the most building gossip?"
            ]
        },
        
        # Work/career stuff  
        {
            'category': 'WORK & CAREER',
            'questions': [
                "Who complains about their job the most?",
                "Who's most likely to get fired?", 
                "Who's most likely to sleep with a coworker?",
                "Who takes the most sick days (real or fake)?",
                "Who's most likely to quit without notice?",
                "Who talks about work outside of work too much?",
                "Who's most likely to get promoted?",
                "Who's worst at managing money/budgeting?",
                "Who's most likely to start their own business and fail?",
                "Who's most likely to retire early vs work forever?"
            ]
        },
        
        # Physical/health habits
        {
            'category': 'LIFESTYLE & HABITS',
            'questions': [
                "Who eats the most junk food?",
                "Who's most likely to not shower for days?",
                "Who works out the least?",
                "Who has the worst eating habits?",
                "Who's most likely to get food poisoning?",
                "Who takes the most selfies?",
                "Who spends the most time on their phone?",
                "Who has the worst fashion sense?",
                "Who's most likely to develop a weird obsession?",
                "Who's most likely to join a cult or MLM?"
            ]
        }
    ]
    
    print("📝 INTEL GATHERING CATEGORIES:")
    print()
    for i, category in enumerate(intel_questions, 1):
        print(f"{i}. {category['category']}")
        print(f"   Sample: \"{category['questions'][0]}\"")
    
    print()
    print("🎯 HOW THIS HELPS:")
    print("• Creates accurate 'Most Likely To' questions")
    print("• Improves personality-based content")
    print("• Makes roasts more targeted and funny")
    print("• Ensures questions fit your actual dynamics")
    print("• Keeps content fresh and relevant")
    print()
    print("💭 EXAMPLE OUTPUT:")
    print("Instead of generic: 'Who's most likely to drunk text?'")
    print("We get specific: 'Who's most likely to drunk text their ex at 3am?'")
    print("Based on: Your answer that Benny does this")
    print()
    print("🔒 SPOILER PROTECTION:")
    print("• No actual game questions revealed")
    print("• You stay surprised during gameplay") 
    print("• Questions get better without ruining fun")
    print("• Win-win for content quality!")

def ask_sample_intel():
    """Ask a few sample intel questions."""
    print("\n🎯 SAMPLE INTEL GATHERING:")
    print("-" * 40)
    
    sample_questions = [
        ("PERSONALITY", "Who's the most impulsive with money/shopping?"),
        ("DATING", "Who has the worst taste in dating partners?"),
        ("SOCIAL", "Who makes the worst decisions when drunk?"),
        ("1280 WEST", "Who's brought home the most questionable dates?"),
        ("WORK", "Who's most likely to sleep with a coworker?")
    ]
    
    for category, question in sample_questions:
        print(f"\n[{category}] {question}")
        print("Options: Lauren, Benny, Gina, Ian")
        print("(This would help create targeted 'Most Likely To' questions)")
    
    print("\n💡 BENEFIT:")
    print("Your answers help me create questions like:")
    print("• 'Who's most likely to drunk order $200 worth of sushi?' (if you say Lauren is impulsive)")
    print("• 'Who's most likely to date someone half their age?' (if you say Ian has bad taste)")
    print("• 'Who's most likely to hook up in the building elevator?' (building-specific)")

if __name__ == "__main__":
    gather_friend_intel()
    ask_sample_intel()