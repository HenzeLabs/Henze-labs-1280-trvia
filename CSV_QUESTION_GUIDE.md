# CSV Question Management Guide

## Overview

All questions can now be managed through CSV files! This makes it super easy to add, edit, or remove questions without touching any code.

## CSV Files

### 1. `sex_trivia_questions.csv`
**Adult/sex-themed trivia questions**

**Columns:**
- `question` - The question text
- `correct_answer` - The correct answer
- `wrong_answer_1` - First wrong answer
- `wrong_answer_2` - Second wrong answer
- `wrong_answer_3` - Third wrong answer
- `difficulty` - Number 1-10 (1=easy, 10=hard)
- `notes` - Optional notes/context

**Example:**
```csv
question,correct_answer,wrong_answer_1,wrong_answer_2,wrong_answer_3,difficulty,notes
"Which country has the highest rate of casual sex?","Iceland","Brazil","France","Sweden",3,"Educational but spicy"
```

**Currently:** 10 questions (you can add more!)

### 2. `regular_trivia_questions.csv`
**Normal/general knowledge trivia**

**Columns:**
- `question` - The question text
- `correct_answer` - The correct answer
- `wrong_answer_1` - First wrong answer
- `wrong_answer_2` - Second wrong answer
- `wrong_answer_3` - Third wrong answer
- `difficulty` - Number 1-10
- `category` - Optional (e.g., "Geography", "Science", "Technology")
- `notes` - Optional notes

**Example:**
```csv
question,correct_answer,wrong_answer_1,wrong_answer_2,wrong_answer_3,difficulty,category,notes
"What is the capital of Australia?","Canberra","Sydney","Melbourne","Brisbane",4,"Geography","Trick question - not Sydney!"
```

**Currently:** 10 questions (you can add more!)

### 3. `poll_questions.csv`
**Vote-based "Who's most likely to..." poll questions**

**Columns:**
- `question` - The full question (should start with "Who's most likely to...")
- `savage_level` - Number 1-10 (how savage/inappropriate)
- `notes` - Optional context

**Example:**
```csv
question,savage_level,notes
"Who's most likely to eat ass on the first date?",10,"Classic savage"
"Who's most likely to hook up in a McDonald's bathroom?",8,"Classy locations"
```

**Currently:** 25 questions (you can add more!)

### 4. `most_likely_questions.csv`
**Scenarios for "Who's most likely to..." with correct/incorrect scoring**

**Columns:**
- `scenario` - The scenario (WITHOUT "Who's most likely to" prefix - that's added automatically)
- `savage_level` - Number 1-10
- `context` - Type of scenario (e.g., "dating", "1280 West specific", "drinking")
- `notes` - Optional context

**Example:**
```csv
scenario,savage_level,context,notes
"get the ick easily from a guy they're dating",7,"dating","Quick to judge"
"sleep with their ex Taylor who they share 2 dogs with (Benny)",9,"1280 West specific","Personal callout"
```

**Currently:** 51 scenarios (excellent variety!)

## How to Add Questions

### Step 1: Open the CSV file
Use any spreadsheet app (Excel, Google Sheets, Numbers) or text editor

### Step 2: Add a new row
Copy the format from existing rows

### Step 3: Save the file
Make sure to save as CSV format

### Step 4: Restart the server
```bash
python3 run_server.py
```

The new questions will be loaded automatically!

## Tips for Writing Good Questions

### Sex Trivia
- ✅ Educational but entertaining
- ✅ Facts with sources (studies, surveys, etc.)
- ❌ Avoid overly explicit/graphic language
- 💡 Example: "Which country has the highest rate of casual sex?"

### Regular Trivia
- ✅ Mix of difficulties
- ✅ Variety of categories (geography, science, pop culture, etc.)
- ❌ Avoid questions that are too obscure
- 💡 Example: "What is the capital of Australia?" (trick question!)

### Poll Questions
- ✅ Should be funny/savage
- ✅ Open to interpretation (no "correct" answer)
- ✅ Personal but not too specific (unless it's a 1280 West inside joke)
- 💡 Example: "Who's most likely to hook up in a McDonald's bathroom?"

### Most Likely Scenarios
- ✅ Relatable to your friend group
- ✅ Can include specific names/references (Benny, Gina, Ian, Lauren, Tom, etc.)
- ✅ Mix of savage levels (not all 10s!)
- 💡 Example: "sleep with their ex Taylor who they share 2 dogs with (Benny)"

## Current Question Counts

| Type | CSV Questions | Hardcoded Fallback | Total Available |
|------|---------------|-------------------|-----------------|
| Sex Trivia | 10 | 20 | 30 |
| Regular Trivia | 10 | 20 | 30 |
| Poll Questions | 25 | 25 | 50 |
| Most Likely | 51 | 50 | 101 |
| **TOTAL** | **96** | **115** | **211** |

## Game Distribution (15 questions)

With CSV files loaded:
- 6 Regular Trivia (from CSV if available)
- 3 Sex Trivia (from CSV if available)
- 3 Most Likely (from CSV if available)
- 1 Receipt from chats
- 1 Personalized question (from questionnaire)
- 1 Poll question (from CSV if available)

## Benefits of CSV System

✅ **Easy to edit** - No code knowledge needed
✅ **Collaborative** - Multiple people can add questions
✅ **Version control** - Track changes over time
✅ **Bulk import** - Add dozens of questions at once
✅ **Fallback** - If CSV missing, hardcoded questions still work
✅ **Quick updates** - Just restart server, no code changes

## Next Steps

1. **Fill out the CSV files** - Aim for 50+ questions per category
2. **Test the questions** - Play a game to see how they flow
3. **Iterate** - Remove bad questions, add more good ones
4. **Share** - Get friends to contribute questions

## Pro Tips

### For Maximum Variety (300+ unique questions across 20 games):

1. **Sex Trivia:** Add 50+ questions (currently 10)
2. **Regular Trivia:** Add 100+ questions (currently 10)
3. **Poll Questions:** Keep at 50 (currently 25 - add 25 more!)
4. **Most Likely:** Already great at 51!

### Quick Wins:

1. **Search for trivia** - Find existing trivia question banks online
2. **Ask ChatGPT** - "Give me 50 adult-themed trivia questions"
3. **Crowdsource** - Have friends submit their favorites
4. **Mix it up** - Different difficulties, topics, styles

The more questions you add, the less repetition players will see!
