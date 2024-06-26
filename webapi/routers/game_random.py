'''Fetch random games'''

from datetime import datetime

from fastapi import Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from mgxhub.db import db_dep
from mgxhub.model.orm import Game
from webapi import app

# pylint: disable=E1102


@app.get("/game/random", tags=['game'])
async def fetch_rand_games(
    threshold: int = Query(10, gt=0),
    limit: int = Query(50, gt=0),
    db: Session = Depends(db_dep)
) -> dict:
    '''Fetch random games

    - **threshold**: Minimum duration of the game, in minutes. Default is 10.
    - **limit**: Maximum number of games to fetch. Default is 50.

    Defined in: `webapi/routers/game_random.py`
    '''

    result = db.query(
        Game.game_guid, Game.version_code,
        Game.created, Game.map_name, Game.matchup,
        Game.duration, Game.speed
    ).filter(
        Game.duration > threshold * 60
    ).order_by(
        func.random()
    ).limit(limit).all()

    games = [list(row) for row in result]
    current_time = datetime.now().isoformat()

    return {'games': games, 'generated_at': current_time}
