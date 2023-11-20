from dataclasses import dataclass
from typing import List

from environs import Env
from sqlalchemy.engine.url import URL


@dataclass
class DbConfig:
    """
    Database configuration class.
    This class holds the settings for the hhj, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        The host where the hhj server is located.
    password : str
        The password used to authenticate with the hhj.
    user : str
        The username used to authenticate with the hhj.
    database : str
        The name of the hhj.
    port : int
        The port where the hhj server is listening.
    """

    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    def construct_sqlalchemy_url(self, driver="asyncpg", host=None, port=None) -> str:
        """
        Constructs and returns a SQLAlchemy URL for this hhj configuration.

        :param driver: The name of the hhj driver (default is "asyncpg").
        :param host: The host for the connection.
        :param port: The host for the connection.
        :return: A SQLAlchemy hhj connection URL as a string.
        """
        if not host:
            host = self.host
        if not port:
            port = self.port
        uri = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=host,
            port=port,
            database=self.database,
        )
        return uri.render_as_string(hide_password=False)

    @staticmethod
    def from_env(env: Env):
        """
        Creates a database configuration object.

        :param env: An Env object containing environment settings.
        :return: A hhj configuration object.
        """
        host = env.str("DB_HOST")
        password = env.str("POSTGRES_PASSWORD")
        user = env.str("POSTGRES_USER")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)
        return DbConfig(
            host=host, password=password, user=user, database=database, port=port
        )


@dataclass
class TgBot:
    """
    Telegram bot configuration class.
    This class holds the settings for the token, admins, groups, etc.

    Attributes
    ----------
    token : str
        The token received from BotFather.
    """

    token: str
    youth_policy: str
    psychologist_support: str
    civic_education: str
    legal_support: str
    admins: List[int]
    all_groups: List[int]
    use_redis: bool

    @staticmethod
    def from_env(env: Env):
        """
        Creates a Telegram bot configuration object.

        :param env: An Env object containing environment settings.
        :return: A Telegram bot configuration object.
        """
        token = env.str("BOT_TOKEN")
        youth_policy = env.str("YOUTH_POLICY")
        psychologist_support = env.str("PSYCHOLOGIST_SUPPORT")
        civic_education = env.str("CIVIC_EDUCATION")
        legal_support = env.str("LEGAL_SUPPORT")
        admins = list(map(int, env.list("ADMINS")))
        all_groups = list(map(int, env.list("GROUPS")))
        use_redis = env.bool("USE_REDIS")
        return TgBot(
            token=token,
            youth_policy=youth_policy,
            psychologist_support=psychologist_support,
            civic_education=civic_education,
            legal_support=legal_support,
            admins=admins,
            all_groups=all_groups,
            use_redis=use_redis,
        )


@dataclass
class RedisConfig:
    """
    Redis configuration class.

    Attributes
    ----------
    redis_port : Optional(int)
        The port where Redis server is listening.
    redis_host : Optional(str)
        The host where Redis server is located.
    """

    redis_port: int
    redis_host: str

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this redis configuration.
        """
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        """
        Creates the RedisConfig object from environment variables.

        :param env: An Env object containing environment settings.
        :return: A redis configuration object.
        """
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(redis_port=redis_port, redis_host=redis_host)


@dataclass
class Config:
    """
    Config configuration class
    This class holds the settings for config.

    Attributes
    ----------
    tg_bot: TgBot
        The Telegram bot configuration object
    db: DbConfig
        The db configuration object
    redis: RedisConfig
        The Redis configuration object
    """

    tg_bot: TgBot
    db: DbConfig
    redis: RedisConfig


def load_config(path: str = None) -> Config:
    """
    Loads the application configuration from an environment file and creates a Config object.

    :param path: Path to the environment file (default is None).
    :return: A config configuration object.
    """
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot.from_env(env),
        db=DbConfig.from_env(env),
        redis=RedisConfig.from_env(env),
    )
