from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserLogModel(Base):
    __tablename__ = "user_log"
    uid = Column(String(64), primary_key=True)
    log_id = Column(Integer)
    unix_ts = Column(Integer)
    user_id = Column(Integer)
    event_name = Column(String(8))

    def __repr__(self):
        return f"<UserLog(id={self.uid}, log_id='{self.log_id}', user_id='{self.user_id}', event_name={self.event_name})>"
