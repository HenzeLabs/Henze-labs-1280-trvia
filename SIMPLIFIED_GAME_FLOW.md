# Simplified Game Flow

## Overview

The game has been streamlined to remove complex host and admin interfaces. Now it's just TV + Players.

## Game Flow

### 1. Start Game

- Go to `localhost:5001`
- Click **"Start New Game"** button
- Automatically creates room and redirects to TV view

### 2. TV View (`/tv/{room_code}`)

- **Main screen** everyone watches (put on TV/projector)
- Shows room code in big Netflix red letters
- Shows player count as players join
- Has **"Start Game"** and **"End Game"** buttons built-in
- Displays all questions, answers, and leaderboards
- No separate host interface needed!

### 3. Players Join

- Players go to `localhost:5001/join` on their phones
- Enter the room code shown on TV
- Enter their name
- Redirected to player view

### 4. Player View (`/player/{player_id}`)

- Personal view on player's phone
- See questions and submit answers
- View their own score
- Simple, mobile-friendly

## What Was Removed

### ❌ Removed Routes

- `/create` - Game creation page (now auto-created from home)
- `/host` - Host dashboard
- `/host/lobby` - Host lobby interface
- `/host/play` - Host game control panel
- `/host/results` - Host results view
- `/admin` - Admin panel

### ✅ Kept Routes

- `/` - Home page (Create or Join)
- `/join` - Player join page
- `/tv/{room_code}` - TV display (with built-in controls)
- `/player/{player_id}` - Player game view
- `/showcase` - Demo/showcase page

## Key Changes

### Home Page (`index.html`)

- **"Start New Game"** button auto-creates room via Socket.IO
- **"Join Game"** takes players to join page
- Removed showcase link from main menu

### TV View (`tv.html`)

- Added **Start Game** button (enabled when ≥1 player)
- Added **End Game** button (returns to home)
- Shows join instructions: "Players join at {host}/join"
- Fully self-contained - no host laptop needed

### Backend (`routes/main.py`)

- Removed all `/host/*` routes
- Removed `/admin` route
- Removed `/create` route
- Clean, simple route structure

## User Experience

1. **Open home page on TV browser** → Click "Start New Game"
2. **TV shows room code** (e.g., "ABC123")
3. **Players join on phones** → Go to `/join`, enter code
4. **TV shows player count** increasing
5. **Click "Start Game" on TV** when ready
6. **Game plays automatically** on TV
7. **Players answer on phones**
8. **TV shows results** and leaderboards
9. **Click "End Game"** when finished → Back to home

## Benefits

✨ **Simpler** - One screen to manage (TV)
✨ **Cleaner** - No confusing host/admin panels
✨ **Faster** - Instant game creation
✨ **Better UX** - All controls on the screen everyone watches
✨ **Less fragile** - No separate host device to disconnect

## Technical Notes

- Game creation happens via Socket.IO `create_room` event
- TV view handles both display AND control
- Uses Netflix design system throughout
- Mobile-first player views
- Desktop-first TV views
