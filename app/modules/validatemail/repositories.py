from app.modules.validatemail.models import Validatemail
from core.repositories.BaseRepository import BaseRepository


class ValidatemailRepository(BaseRepository):
    def __init__(self):
        super().__init__(Validatemail)