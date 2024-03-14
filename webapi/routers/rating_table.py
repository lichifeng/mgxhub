'''Rating table router'''

from datetime import datetime

from mgxhub.db.operation import get_rating_table as get_ratings
from webapi import app


@app.get("/rating/table")
async def get_rating_table(
    version_code: str = 'AOC10',
    matchup: str = 'team',
    order: str = 'desc',
    page: int = 0,
    page_size: int = 100
) -> dict:
    '''Fetch rating table

    Defined in: `mgxhub/db/operation/get_rating_table.py`
    '''

    ratings = get_ratings(version_code, matchup, order, page, page_size)
    current_time = datetime.now().isoformat()
    return {'ratings': ratings, 'generated_at': current_time}