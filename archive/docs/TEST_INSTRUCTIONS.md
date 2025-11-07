# Quick Test Instructions

## Start Here

1. **Start the server:**
   ```bash
   cd /Users/laurenadmin/1280_Trivia
   source .venv/bin/activate
   python3 run.py
   ```

2. **Open the host page:**
   - Go to: http://localhost:5001/host
   - Open browser DevTools (F12 or right-click → Inspect)
   - Go to the "Console" tab

3. **Check for initial messages:**
   You should see:
   ```
   Connected to server
   🚀 HostDashboard created and available globally
   ✅ Create Game button event listener bound
   ✅ Host name Enter key listener bound
   ```

4. **Create a game:**
   - Type your name in the "Host Name" field
   - Click "Create Game" (or press Enter)

5. **What you should see:**
   - Console messages showing the creation process
   - The setup screen should disappear
   - A game lobby should appear with:
     - A room code (like "ABC123")
     - Text: "Players join at: localhost:5001/join"
     - Player count: 0
     - A "Start Game" button (disabled until players join)

## Console Messages You Should See

When you click "Create Game", you should see:
```
🚀 createGame() function called!
Host name from input: YourName
✅ Host name valid, making API call...
📡 API response: {success: true, room_code: "XYZ789", message: "Game created! Room code: XYZ789"}
✅ Game created successfully!
🏠 Room code: XYZ789
🎯 Calling showGameLobby...
🎯 showGameLobby called with roomCode: XYZ789
🔍 Debugging elements...
All elements with 'game' in ID: [{id: "game-setup", visible: true}, ...]
Setup element: [object] Classes: section
Lobby element: [object] Classes: section hidden
Room code element: [object]
✅ Hidden game-setup
✅ Shown game-lobby
   Lobby classes after removal: section
   Lobby display style: grid
✅ Set room code to: XYZ789
```

**Key indicator:** Look for `Lobby display style: grid` - this confirms the CSS is working!

## If Nothing Happens

1. **Check for errors in the console** (they'll be in red)
2. **Hard refresh the page** (Cmd+Shift+R or Ctrl+Shift+R)
3. **Check the Network tab:**
   - Look for a request to `/api/game/create`
   - Click on it and check the response
4. **Make sure you entered a name** (not just spaces)

## Test the Full Flow

To test a complete game:

### Terminal 1: Run the server
```bash
source .venv/bin/activate
python3 run.py
```

### Browser Window 1: Host
1. Go to http://localhost:5001/host
2. Enter name: "Host Player"
3. Click "Create Game"
4. Note the room code (e.g., "ABC123")

### Browser Window 2: Player (Incognito/Private mode)
1. Go to http://localhost:5001/join
2. Enter the room code from the host
3. Enter name: "Player 1"
4. Click "Join Game"

### Back to Host Window
- You should see "Player 1" appear in the players list
- The "Start Game" button should become enabled
- Player count should show "1"

## Success Criteria

✅ Server starts without errors
✅ Host page loads
✅ Console shows initialization messages
✅ Entering name and creating game shows debug output
✅ Game lobby appears
✅ Room code is displayed
✅ No red errors in console

## Files That Were Modified

The following files were changed to fix the issue:

1. **frontend/templates/host.html** (line 555-560)
   - Removed duplicate `onclick` handler

2. **frontend/static/js/host.js** (line 60-70)
   - Added Enter key support for form submission

3. **frontend/static/js/app.js** (line 67-77)
   - Added error alert fallback for missing error containers

## Need Help?

See [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) for detailed troubleshooting steps.
