"""Main application routes."""

from flask import Blueprint, render_template, request, jsonify
from ..game.engine import game_engine

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main landing page."""
    return render_template('index.html')

@bp.route('/join')
def join():
    """Player join page."""
    return render_template('join.html')

@bp.route('/player/<player_id>')
def player_dashboard(player_id):
    """Player dashboard."""
    session = game_engine.get_player_session(player_id)
    if not session:
        return render_template('error.html', message="Invalid player session")
    
    return render_template('player.html', player_id=player_id)

@bp.route('/tv/<room_code>')
def tv_spectator(room_code):
    """TV/Spectator view - large screen display for everyone to watch."""
    # Verify room exists
    session = game_engine.get_session(room_code)
    if not session:
        return render_template('error.html', message="Game not found")
    return render_template('tv.html', room_code=room_code)

@bp.route('/showcase')
def showcase():
    """Showcase page showing all game screens and states."""
    return render_template('showcase.html')