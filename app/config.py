from dataclasses import dataclass
from environs import Env

@dataclass
class Bot:
    token: str

@dataclass
class Config:
    bot: Bot

def load_config(path=None):
    env = Env()
    env.read_env(path)

    return Config(bot=Bot(token=env('BOT_TOKEN')))
