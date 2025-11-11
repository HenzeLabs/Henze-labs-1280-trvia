# Content & Gameplay Audit v1.7

## Context
Post-security hardening. This audit focuses on **game integrity, content safety, fairness, and player experience** rather than security vulnerabilities.

**Target Audience:** Lauren, Ian, Benny, and Gina at 1280 West Condos
**Question Sources:** CSV files + iMessage chat parsing + personalized questionnaires

## Audit Scope

### 1. Content Safety & Privacy
- [ ] Do generated questions expose PII (phone numbers, addresses, private info)?
- [ ] Are questions offensive, inappropriate, or discriminatory?
- [ ] Can the iMessage parser leak sensitive conversation content?
- [ ] Are player names from chat data properly anonymized?
- [ ] Do questions reveal information players wouldn't want public?

### 2. Question Quality
- [ ] Are questions actually answerable by the target audience?
- [ ] Is the correct answer always in the options?
- [ ] Are distractors plausible but clearly wrong?
- [ ] Do questions make grammatical sense?
- [ ] Are questions too easy, too hard, or well-balanced?
- [ ] Can questions be ambiguous or have multiple correct answers?

### 3. Answer Validation Logic
- [ ] Can players exploit case sensitivity (e.g., "Alice" vs "alice")?
- [ ] Are unicode/emoji answers handled correctly?
- [ ] Can whitespace manipulation bypass validation?
- [ ] Are duplicate answers from same player handled?
- [ ] Can players change answers after submission?
- [ ] Does the system handle ties in answer timing correctly?

### 4. Game Balance & Fairness
- [ ] Is the point distribution fair (base + speed bonus)?
- [ ] Can early questions disproportionately affect final scores?
- [ ] Does the Final Sprint mechanic work as intended (2x points)?
- [ ] Are timer durations appropriate for question difficulty?
- [ ] Can network latency give unfair advantages?
- [ ] Is the tie-breaker (total_answer_time) deterministic and fair?

### 5. Question Generation Pipeline
- [ ] Does the parser correctly extract context from iMessage data?
- [ ] Are generated questions diverse (not repetitive)?
- [ ] Can the generator produce enough questions for a full game?
- [ ] Are there quality control filters before questions go live?
- [ ] Can admins review/edit/reject generated questions?
- [ ] Does the system handle edge cases (empty chats, single participant)?

### 8. CSV Question Loading (Lauren, Ian, Benny, Gina)
- [ ] Are CSV files loading correctly from archive/private_data?
- [ ] Do questions reference the correct friend names (Lauren, Ian, Benny, Gina)?
- [ ] Are personalized callouts accurate (e.g., "Benny's ex Taylor")?
- [ ] Is the question mix appropriate (sex trivia, regular trivia, polls, most likely)?
- [ ] Are savage_level ratings accurate for the friend group?
- [ ] Do CSV questions have proper sanitization (XSS prevention)?
- [ ] Can the system handle malformed CSV files gracefully?
- [ ] Are there enough questions to avoid repetition (50+ per category)?
- [ ] Do "most likely" questions work for all 4 friends as answer options?
- [ ] Are 1280 West-specific references clear to the group?

### 9. Ratchet/Crazy/Raunchy/Ridiculous Level Calibration
- [ ] Are savage_level ratings (1-10) properly distributed across questions?
- [ ] Do level 1-3 questions feel tame/safe for warm-up?
- [ ] Do level 4-6 questions escalate to moderately raunchy/funny?
- [ ] Do level 7-9 questions hit peak ratchet/ridiculous territory?
- [ ] Are level 10 questions truly savage/unhinged?
- [ ] Is there a good progression from tame → wild throughout the game?
- [ ] Are sex trivia questions appropriately raunchy but not cringe?
- [ ] Do "most likely" questions hit the right level of savage callouts?
- [ ] Are inside jokes ridiculous enough to be funny but not mean-spirited?
- [ ] Does the game feel like a fun roast session vs. actual bullying?

### 10. Question Mix & Distribution (Inside Jokes + Sex + Regular)
- [ ] Does each game have the right ratio: ~40% regular trivia, ~30% sex trivia, ~30% inside jokes?
- [ ] Are inside jokes specific enough to be funny but broad enough to be answerable?
- [ ] Do sex trivia questions feel educational/interesting vs. just shock value?
- [ ] Are regular trivia questions engaging (not boring filler)?
- [ ] Is there variety within each category (not all the same style)?
- [ ] Do questions flow well together (not jarring transitions)?
- [ ] Are "receipt" questions from iMessage chats actually funny/embarrassing?
- [ ] Do personalized questions from questionnaires land well?
- [ ] Are poll questions open-ended enough for debate?
- [ ] Does the Final Sprint feel climactic with high-energy questions?

### 6. Player Experience
- [ ] Are error messages helpful and non-technical?
- [ ] Can players understand why their answer was wrong?
- [ ] Is the leaderboard update timing fair to all players?
- [ ] Do disconnected players get a fair chance to rejoin?
- [ ] Are UI timers synchronized with server timers?
- [ ] Can colorblind players distinguish answer options?

### 7. Edge Cases & Stress Testing
- [ ] What happens with 0 questions in the database?
- [ ] Can the game handle 1 player? 100 players?
- [ ] What if all players answer incorrectly?
- [ ] What if all players answer at the exact same millisecond?
- [ ] Can the game recover from mid-question crashes?
- [ ] What happens if the host disconnects during gameplay?

## Test Scenarios

### Content Safety Tests
1. Parse a chat with phone numbers, emails, addresses
2. Generate questions from sensitive conversations
3. Check for profanity, slurs, or inappropriate content
4. Verify PII is filtered before question display

### Answer Validation Tests
1. Submit "Alice", "alice", "ALICE", " Alice ", "Alice\n"
2. Submit emoji answers: "😀", "👍", "Alice 🎉"
3. Submit unicode: "Café", "北京", "Москва"
4. Submit answer after timer expires
5. Submit multiple answers rapidly

### Game Balance Tests
1. Play with 2 players, 10 players, 50 players
2. Measure score distribution across difficulty levels
3. Test Final Sprint point multiplier
4. Verify tie-breaker with identical scores
5. Simulate network delays (50ms, 500ms, 2000ms)

### Question Quality Tests
1. Generate 100 questions and manually review
2. Check for unanswerable questions
3. Verify correct answer is always present
4. Test with empty/minimal chat data
5. Check for duplicate or near-duplicate questions

### CSV Loading Tests
1. Load all CSV files from archive/private_data/
2. Verify friend names (Lauren, Ian, Benny, Gina) are correct
3. Test with malformed CSV (missing columns, bad encoding)
4. Check XSS sanitization on CSV content
5. Verify question distribution matches expected ratios
6. Test "most likely" questions with all 4 friends as options
7. Validate personalized callouts (Benny/Taylor, 1280 West references)
8. Check savage_level filtering works correctly

### Ratchet Level Calibration Tests
1. **Sample 10 questions from each savage_level (1-10)**
   - Level 1-3: Should be safe for grandma
   - Level 4-6: Should make you laugh but not gasp
   - Level 7-9: Should be "oh shit" territory
   - Level 10: Should be absolutely unhinged
2. **Play 5 full games and rate the vibe:**
   - Does it feel like a fun Jackbox game?
   - Are there awkward/cringe moments?
   - Do players laugh or get uncomfortable?
3. **Check savage_level distribution in CSV files:**
   - Count questions per level (should be bell curve: more 5-7, fewer 1-3 and 9-10)
4. **Test escalation throughout game:**
   - Early questions should be tamer
   - Final Sprint should be peak chaos

### Question Mix Tests
1. **Play 10 games and track question types:**
   - Count: Regular trivia, Sex trivia, Inside jokes, Receipts, Polls
   - Target: ~6 regular, ~3 sex, ~3 inside jokes, ~1 receipt, ~1 poll, ~1 personalized
2. **Inside joke quality check:**
   - Are they specific to Lauren/Ian/Benny/Gina?
   - Are they funny or just confusing?
   - Do all 4 friends understand the reference?
3. **Sex trivia quality check:**
   - Educational vs. just gross?
   - Funny vs. uncomfortable?
   - Appropriate for the friend group?
4. **Regular trivia quality check:**
   - Engaging vs. boring filler?
   - Good difficulty mix?
   - Interesting facts vs. obscure nonsense?
5. **Flow test:**
   - Do questions transition smoothly?
   - Is there variety (not 3 sex questions in a row)?
   - Does the game maintain energy throughout?

## Deliverable Format

```markdown
## ISSUE #X: [Title]
**Severity**: CRITICAL | HIGH | MEDIUM | LOW | COSMETIC
**Category**: Safety | Quality | Validation | Balance | Generation | UX | Edge Case

**Description**: [What is the problem?]

**Impact**: [How does this affect players or game integrity?]

**Reproduction**:
1. Step 1
2. Step 2
3. Observe behavior

**Evidence**: [Screenshots, logs, or code location]

**Recommended Fix**: [How to improve it]

**Priority**: [Must-fix before launch | Should-fix | Nice-to-have]
```

## Success Criteria
- Identify 5-10 content/gameplay issues OR confirm game is production-ready
- Prioritize fixes by player impact
- Provide actionable recommendations with examples
- Focus on real-world playability, not theoretical edge cases

## Out of Scope
- Security vulnerabilities (covered in v1.6 audit)
- Performance optimization (unless it affects fairness)
- UI/UX design preferences (unless accessibility issue)
- Feature requests (focus on existing functionality)
