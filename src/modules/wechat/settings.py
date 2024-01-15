from pydantic_settings import BaseSettings


class WeChatApiSetting(BaseSettings):
    app_id: str
    app_secret: str
    redirect_uri: str = "http://127.0.0.1"


class OssAvatarBucket(BaseSettings):
    avatar_bucket: str = "avatar_bucket"
