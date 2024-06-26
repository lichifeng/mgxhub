'''Rating table router'''

from datetime import datetime

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from mgxhub.db import db_dep
from mgxhub.db.operation import get_rating_table as get_ratings
from webapi import app


@app.get("/rating/table", tags=['rating'])
async def get_rating_table(
    version_code: str = 'AOC10',
    matchup: str = 'team',
    order: str = 'desc',
    page: int = Query(0, ge=0),
    page_size: int = Query(100, ge=1),
    db: Session = Depends(db_dep)
) -> dict:
    '''Fetch rating table

    Keys:
        - **ratings**: [index, name, name_hash, rating, total, wins, streak,
                        streak_max, highest, lowest, first_played, last_played]
        - **total**: Total number of ratings.

    Defined in: `mgxhub/db/operation/get_rating_table.py`
    '''

    result = get_ratings(db, version_code, matchup, order, page, page_size)
    current_time = datetime.now().isoformat()

    return {'ratings': result[0], 'total': result[1], 'generated_at': current_time}
