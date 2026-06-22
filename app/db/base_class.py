from sqlalchemy.orm import DeclarativeBase, declared_attr


class CustomBase:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Base(CustomBase, DeclarativeBase):
    pass
