from database.all_for_session import SqlAlchemyBase
from sqlalchemy import Column, Integer, String, ForeignKey


class Photo(SqlAlchemyBase):
    """Таблица, представляющая фотографии"""

    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
