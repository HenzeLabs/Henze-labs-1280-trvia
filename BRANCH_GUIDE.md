# Branch Structure

This repository has two main branches for different purposes:

## `main` Branch - Personal 1280 Game

**Purpose:** Private game for 1280 West Condos friends  
**Features:**

- iMessage parsing for personalized questions
- Private chat data integration
- Custom friend group references
- NOT for public distribution

**To use:**

```bash
git checkout main
python run_server.py
```

---

## `product` Branch - Sellable Product

**Purpose:** Clean, public-ready version for commercial sale  
**Features:**

- Pre-game survey system (no iMessage dependency)
- Generic question packs
- User accounts & payment integration
- No personal/private data
- Ready for deployment

**To use:**

```bash
git checkout product
python run_server.py
```

---

## Workflow

### Playing with 1280 Friends:

```bash
git checkout main
# Use your personal version with all the inside jokes
```

### Working on Product Features:

```bash
git checkout product
# Build sellable features here
```

### Syncing Generic Improvements:

If you make a bug fix or improvement that should be in BOTH versions:

```bash
# From product branch
git checkout main
git cherry-pick <commit-hash>
# Or merge specific files
```

---

## Key Differences

| Feature         | `main` (1280)    | `product` (Sellable) |
| --------------- | ---------------- | -------------------- |
| Question Source | iMessage parsing | Survey system        |
| Data Privacy    | Private chats    | User-submitted only  |
| Deployment      | Local only       | Cloud-ready          |
| User Accounts   | Not needed       | Required             |
| Payment         | Free             | Freemium model       |
| Branding        | "1280 Trivia"    | Configurable         |

---

## Never Commit to Product Branch:

- ❌ Personal iMessage data
- ❌ Friend names/phone numbers
- ❌ Private chat exports
- ❌ Hardcoded contact maps
- ❌ Personal CSV files

## Safe to Commit:

- ✅ Generic trivia questions
- ✅ Survey system code
- ✅ UI improvements
- ✅ Bug fixes
- ✅ Documentation
