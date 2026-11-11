from backend.config import Settings, get_settings

if __name__ == '__main__':


    print(get_settings().database_url)
    print(get_settings().deepseek_api_key)
