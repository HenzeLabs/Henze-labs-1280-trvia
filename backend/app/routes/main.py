"""Main application routes."""

from flask import Blueprint, render_template, request, jsonify
from ..game.engine import game_engine

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main landing page."""
    return render_template('index.html')

@bp.route('/host')
def host():
    """Host dashboard."""
    return render_template('host.html')

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

@bp.route('/admin')
def admin():
    """Admin panel for managing questions and data."""
    return render_template('admin.html')