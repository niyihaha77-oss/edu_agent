from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import PydanticModel


class Te(BaseSettings):
    deepseek_api_key:str
    model_config = SettingsConfigDict(env_file='')

print(Te())