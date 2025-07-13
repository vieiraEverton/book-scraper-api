from sqlmodel import Session, select
from api.models.user import User
from api.security import get_password_hash, verify_password

class UserService:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, username: str, password: str, is_admin: bool=False) -> User:
        hashed = get_password_hash(password)
        user = User(username=username, hashed_password=hashed, is_admin=is_admin)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> User | None:
        stmt = select(User).where(User.username == username)
        user = self.session.exec(stmt).first()
        if user and verify_password(password, user.hashed_password):
            return user
        return None

    def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.session.exec(stmt).first()

