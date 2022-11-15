from pydantic import BaseSettings


# TODO: add jwt secret to .env file
class Settings(BaseSettings):
    database_url: str = 'sqlite:///database.sqlite3'
    jwt_secret: str = '30a0ad574719b93ca85680f685c6f0e415a1671c391652f39b8cbb56f3f837eb'
    jwt_algorithm: str = 'HS256'
    jwt_expiration: int = 3600


settings = Settings()
