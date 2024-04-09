'''Fetch latest N players and their simple stats.'''


from datetime import datetime

from fastapi import BackgroundTasks

from mgxhub import db
from mgxhub.db.operation import get_latest_players
from webapi import app

# pylint: disable=E1102

PLAYERS_CACHE: list[list, float] = [[], 0]  # [cache, last_updated_time]


@app.get("/player/latest")
async def get_new_players(background_tasks: BackgroundTasks, limit: int = 20) -> dict:
    '''Newly found players.

    Including name, name_hash, first_found, won games, total games, and 1v1 games counts.

    Args:
        limit: maximum number of players to be included.

    Defined in: `webapi/routers/player_latest.py`
    '''

    current_time = datetime.now().isoformat()

    min_limit = max(limit, 150)

    session = db()
    if PLAYERS_CACHE[0] and len(PLAYERS_CACHE[0]) >= limit:
        if PLAYERS_CACHE[1] and (datetime.now().timestamp() - PLAYERS_CACHE[1] > 300):
            background_tasks.add_task(get_latest_players, session, min_limit)
        return {
            'players': PLAYERS_CACHE[0][:limit],
            'generated_at': current_time
        }

    PLAYERS_CACHE[0] = get_latest_players(session, min_limit)
    PLAYERS_CACHE[1] = datetime.now().timestamp()

    return {'players': PLAYERS_CACHE[0], 'generated_at': current_time}
