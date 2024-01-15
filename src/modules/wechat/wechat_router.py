# 小程序扫码登录绑定

import base64
import json
import random
import string
import traceback

from fastapi import APIRouter, Depends
from fastapi import (
    WebSocket,
    WebSocketDisconnect,
)
from wechatpy.client import WeChatClient
from wechatpy.exceptions import WeChatClientException
from wechatpy.exceptions import WeChatOAuthException

from auth import AuthBearer
from auth import get_current_user
from auth.jwt_token_handler import create_access_token
from conf.base_model import ResponseStatusTypeCode
from conf.base_model import ResponseStruct
from sql_model.models import ManagewechatPlatformAuth
from src.wechat.db import ManagewechatPlatformAuthApi
from src.wechat.db import UserModelApi
from src.wechat.models import LoginResponse
from src.wechat.models import ManagewechatModel
from src.wechat.models import NewUserPlatformAuthModel
from src.wechat.models import UserIdentity
from src.wechat.models import WechatLoginModel
from src.wechat.models import WechatMiniLoginModel
from src.wechat.settings import WeChatApiSetting
from src.wechat.wxa import WeChatWxa
from utils.secret_all.aes import aes_decrypt
from utils.storage.redis_cache import RedisLock
from utils.storage.redis_cache import cache
from sql_model.database import DBApi
from utils.others.time_handler import time_util
from logging import getLogger

logger = getLogger(__name__)

wechat_router = APIRouter()


@wechat_router.get(
    "/wechat/weixin/inactive/unlimited_qr_code",
    tags=["wechat"],
    response_model=ResponseStruct,
    description="获取小程序码",
    summary="未登录获取小程序码,用于登录账户",
)
def get_unlimited_mini_app_access_token():
    """
    A function that gets an unlimited mini app access token.

    Parameters:
    - `scene_code` (str): The scene code for generating the mini app access token.

    Returns:
    - `dict`: A dictionary containing the encoded content of the mini app access token.
    """
    wechat_app = WeChatApiSetting()
    client = WeChatClient(
        appid=wechat_app.app_id, secret=wechat_app.app_secret, timeout=5
    )
    client.fetch_access_token()
    wxa = WeChatWxa(client=client)
    choice_scene = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(10)
    )
    scene_code = f"login-{choice_scene}"
    res = wxa.get_wxa_code_unlimited(
        scene=scene_code, page="scanCode/pages/pcLogin/pcLogin"
    )

    return {
        "data": {
            "scene": scene_code,
            "mini_code": base64.b64encode(res.content).decode(),
        }
    }


@wechat_router.get(
    "/wechat/weixin/active/unlimited_qr_code",
    tags=["wechat"],
    response_model=ResponseStruct,
    dependencies=[Depends(AuthBearer())],
    description="获取小程序码",
    summary="已登录获取小程序码,用于绑定账户",
)
def get_unlimited_mini_app_access_token(
    current_user: UserIdentity = Depends(get_current_user),
):
    """
    Get unlimited mini app access token.

    Args:
        current_user (UserIdentity): The current user identity.

    Returns:
        dict: The response data containing the encoded content.
    """
    locked = RedisLock().set_lock(
        lock_name=f"wechat:get_unlimited_mini_app_access_token:{current_user.user_id}"
    )
    if not locked:
        return {
            "message": "操作太快,请稍后再试",
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
        }

    wechat_app = WeChatApiSetting()

    auth_api = ManagewechatPlatformAuthApi()
    user_auth = auth_api.get_special_platform_auth(
        platform="wechat",
        manage_wechat_id=current_user.user_id,
        app_id=wechat_app.app_id,
    )
    if user_auth:
        return {
            "message": "已经绑定过账户",
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
        }
    client = WeChatClient(
        appid=wechat_app.app_id, secret=wechat_app.app_secret, timeout=5
    )
    client.fetch_access_token()
    wxa = WeChatWxa(client=client)
    choice_scene = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(10)
    )
    scene_code = f"binding-{current_user.user_id}-{choice_scene}"
    res = wxa.get_wxa_code_unlimited(
        scene=scene_code, page="scanCode/pages/bindWXwechat/bindWXwechat"
    )
    cache.set(scene_code, current_user.user_id, ex=2 * 60 * 50)
    return {
        "data": {
            "scene": scene_code,
            "mini_code": base64.b64encode(res.content).decode(),
        }
    }


def get_user_open_id(code):
    """
    小程序登陆有data和iv
    :param code:
    :return:
    """
    wechat_app = WeChatApiSetting()
    client = WeChatClient(
        appid=wechat_app.app_id, secret=wechat_app.app_secret, timeout=5
    )
    res = client.wxa.code_to_session(code)
    # user_info = client.user.get(user_id=res["openid"])
    # logger.info(f"user_info:{user_info}")
    logger.info(f"code_to_session: {res}")
    open_id = res["openid"]
    return open_id


@wechat_router.post(
    "/wechat/mini_scan/login",
    tags=["wechat"],
    response_model=LoginResponse,
    description="小程序扫码登陆",
    summary="小程序扫码登陆",
)
def get_wechat_open_id(wechat: WechatLoginModel):
    code = wechat.code
    logger.info(f"code: {code}")
    scene_code = wechat.scene_code
    logger.info(f"scene_code: {scene_code}")
    wechat_app = WeChatApiSetting()
    app_id = wechat_app.app_id
    try:
        open_id = get_user_open_id(code=code)
    except WeChatOAuthException as e:
        logger.error(e.errmsg)
        return {
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
            "message": f"获取微信信息失败: {e.errmsg}",
        }
    except WeChatClientException as e:
        logger.error(e.errmsg)
        return {
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
            "message": f"获取微信信息失败: {e.errmsg}",
        }
    auth_api = ManagewechatPlatformAuthApi()
    user_auth = auth_api.get_special_platform_auth(
        platform="wechat", open_id=open_id, app_id=app_id
    )
    is_bind_user_id = cache.get(scene_code)
    # 绑定过程
    if is_bind_user_id:
        user_id = is_bind_user_id
        if user_auth:
            user_id = user_auth.manage_wechat_id
            if int(is_bind_user_id) != int(user_auth.manage_wechat_id):
                return {
                    "message": "已经绑定过其他账户",
                    "type": ResponseStatusTypeCode().failed,
                    "code": 406,
                }
        else:
            auth_api.create_platform_auth(
                new_platform_auth=NewUserPlatformAuthModel(
                    manage_wechat_id=is_bind_user_id,
                    app_id=app_id,
                    platform="wechat",
                    open_id=open_id,
                )
            )

    else:
        # 登录过程
        if not user_auth:
            # 如果没有绑定,不允许登录
            return {
                "message": "请绑定后再次尝试",
                "type": ResponseStatusTypeCode().failed,
                "code": 406,
            }

        user_id = user_auth.manage_wechat_id
    special_user = UserModelApi().get_special_user(id=user_id)
    if not special_user:
        return {
            "message": "账户不存在, 请确认后重试",
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
        }
    if special_user.is_active == 0:
        return {
            "message": "账号已被禁用,请联系管理员",
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
        }
    if not special_user.role_id:
        return {
            "message": "账号未授权角色,请联系管理员",
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
        }
    data = dict(
        email=special_user.email,
        user_id=special_user.id,
        user_name=special_user.name_cn,
        role_en=special_user.role_name_en,
        store_id=special_user.store_id,
        store_name=special_user.store_name,
    )
    token = create_access_token(data)
    data = ManagewechatModel.model_validate(special_user).model_dump(
        exclude=["t_created", "t_modified", "password"]
    )
    data["phone_number"] = aes_decrypt(data["phone_number"])
    data["birthday"] = time_util.datetime_to_string_yymmdd(dt=data["birthday"])
    logger.info(f"用户登录成功, 用户信息: {data}")
    cache.set(
        f"{scene_code}_user_data",
        json.dumps({"user_info": data, "token": token}, ensure_ascii=False),
        ex=5 * 60,
    )
    return {"data": {"user_info": data, "token": token}}


@wechat_router.post(
    "/wechat/mini/unbind",
    tags=["wechat"],
    response_model=ResponseStruct,
    description="解绑微信",
    summary="解绑微信",
)
def mini_program_unbind(current_user: UserIdentity = Depends(get_current_user)):
    auth_api = ManagewechatPlatformAuthApi()
    wechat_app = WeChatApiSetting()
    app_id = wechat_app.app_id
    user_auth = auth_api.get_special_platform_auth(
        platform="wechat", app_id=app_id, manage_wechat_id=current_user.user_id
    )
    if not user_auth:
        return {
            "message": "绑定关系不存在",
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
        }

    DBApi().delete_one(
        condition={"id": user_auth.id}, db_model=ManagewechatPlatformAuth
    )
    return {"message": "解绑成功"}


@wechat_router.post(
    "/wechat/mini/login",
    tags=["wechat"],
    response_model=LoginResponse,
    description="小程序登陆",
    summary="小程序登陆",
)
def mini_program_login(wechat: WechatMiniLoginModel):
    code = wechat.code
    logger.info(f"code: {code}")
    wechat_app = WeChatApiSetting()
    app_id = wechat_app.app_id
    try:
        open_id = get_user_open_id(code=code)
    except WeChatOAuthException as e:
        logger.error(e.errmsg)
        return {
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
            "message": f"获取微信信息失败: {e.errmsg}",
        }
    except WeChatClientException as e:
        logger.error(e.errmsg)
        return {
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
            "message": f"获取微信信息失败: {e.errmsg}",
        }
    auth_api = ManagewechatPlatformAuthApi()
    user_auth = auth_api.get_special_platform_auth(
        platform="wechat", open_id=open_id, app_id=app_id
    )
    # 登录过程
    if not user_auth:
        # 如果没有绑定,不允许登录
        return {
            "message": "请在管理后台绑定后再次尝试",
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
        }
    user_id = user_auth.manage_wechat_id
    special_user = UserModelApi().get_special_user(id=user_id)
    if not special_user:
        return {
            "message": "账户不存在, 请确认后重试",
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
        }
    if special_user.is_active == 0:
        return {
            "message": "账号已被禁用,请联系管理员",
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
        }
    if not special_user.role_id:
        return {
            "message": "账号未授权角色,请联系管理员",
            "type": ResponseStatusTypeCode().failed,
            "code": 406,
        }
    data = dict(
        email=special_user.email,
        user_id=special_user.id,
        user_name=special_user.name_cn,
        role_en=special_user.role_name_en,
        store_id=special_user.store_id,
        store_name=special_user.store_name,
    )
    token = create_access_token(data)
    data = ManagewechatModel.model_validate(special_user).model_dump()
    data["phone_number"] = aes_decrypt(data["phone_number"])
    return {"data": {"user_info": data, "token": token}}


@wechat_router.websocket("/wechat/{scene_code}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    scene_code: str,
):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Message text was: {data}, for scene_code: {scene_code}")
            user_data = cache.get(f"{scene_code}_user_data")
            logger.info(f"user_data: {user_data}")
            if user_data:
                await websocket.send_text(
                    json.dumps(
                        {
                            "message": "登陆成功",
                            "type": ResponseStatusTypeCode().success,
                            "code": 200,
                            "data": json.loads(user_data),
                        },
                        ensure_ascii=False,
                    )
                )
            else:
                await websocket.send_text(json.dumps({"type": "health", "data": 1}))
    except WebSocketDisconnect as e:
        traceback.print_exc()
        logger.error("websocket disconnect")
    except Exception as e:
        traceback.print_exc()
        logger.error(e)


@wechat_router.get(
    "/wechat/binding_info",
    tags=["wechat"],
    response_model=ResponseStruct,
    summary="获取绑定信息",
)
def get_auth_binding(current_user: UserIdentity = Depends(get_current_user)):
    auth_api = ManagewechatPlatformAuthApi()
    wechat_app = WeChatApiSetting()
    app_id = wechat_app.app_id
    user_auth = auth_api.get_special_platform_auth(
        platform="wechat", app_id=app_id, manage_wechat_id=current_user.user_id
    )
    return {
        "message": "success",
        "data": True if user_auth else False,
    }
