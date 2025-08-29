from __future__ import annotations
from .api import LarkAPI
from typing_extensions import Literal
from typing import List, Dict
import json
from pathlib import Path
import requests
import datetime
import dateutil


class LarkCalendar(LarkAPI):

    def __init__(self, app_id, app_secret, calendar_id: str = None) -> None:
        super().__init__(app_id, app_secret)
        self.calendar_id = calendar_id

        self.url_calender = "https://open.feishu.cn/open-apis/calendar/v4/calendars"

    def query_calendar_list(self, page_size: int = 500) -> Dict:
        response = self.request("GET",
                                f"{self.url_calender}?page_size={page_size}")
        resp = response.json()
        if resp.get("code") == 0:
            return resp['data']['calendar_list']
        print(resp)
        return resp

    def create_event(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        summary: str = None,
        description: str = None,
        need_notification: bool = None,
        visibility: Literal['default', 'public', 'private'] = None,
        attendee_ability: Literal['none', 'can_see_others',
                                  'can_invite_others',
                                  'can_modify_event'] = None,
        free_busy_status: Literal['busy', 'free'] = None,
        location: Dict[Literal['name', 'address', 'latitude', 'longitude'],
                       str | float] = None,
        color: int = None,
        reminders: List[Dict[Literal['minutes'], int]] = None,
        recurrence: str = None,
        attachments: List[Dict[Literal['file_token'], str]] = None,
        timezone: str = 'Asia/Shanghai',
        user_id_type: Literal['user_id', 'union_id', 'open_id'] = 'user_id',
        whole_day: bool = False,
    ) -> requests.models.Response:
        """新建日程
        https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/create?appId=cli_a7cd947b13f91013&lang=zh-CN
        
        Args:
            start_time (datetime.datetime): 日程开始时间
            end_time (datetime.datetime): 日程结束时间
            summary (str, optional): 日程标题. Defaults to None.
            description (str, optional): 日程描述. Defaults to None.
            need_notification (bool, optional): 是否需要提醒. Defaults to None.
            visibility (Literal['default', 'public', 'private'], optional): 日程可见性. Defaults to None.
            attendee_ability (Literal['none', 'can_see_others', 'can_invite_others', 'can_modify_event'], optional): 参与者权限. Defaults to None.
            free_busy_status (Literal['busy', 'free'], optional): 忙闲状态. Defaults to None.
            location (Dict[Literal['name', 'address', 'latitude', 'longitude'], str | float], optional): 日程地点. Defaults to None.
            color (int, optional): 日程颜色. Defaults to None.
            reminders (List[Dict[Literal['minutes'], int]], optional): 提醒. Defaults to None.
            recurrence (str, optional): 重复. Defaults to None.
            attachments (List[Dict[Literal['file_token'], str]], optional): 日程附件. Defaults to None.
            timezone (str, optional): 时区. Defaults to None.
            user_id_type (Literal['user_id', 'union_id', 'open_id'], optional): 用户 ID 类型. Defaults to 'user_id'.
            whole_day (bool, optional): 是否全天日程. Defaults to False.

        Returns:
            requests.models.Response: 响应
        """
        url = f"{self.url_calender}/{self.calendar_id}/events?user_id_type={user_id_type}"
        if whole_day:
            start_date = start_time.strftime("%Y-%m-%d")
            end_date = end_time.strftime("%Y-%m-%d")
            start_timestamp = None
            end_timestamp = None
        else:
            start_date = None
            end_date = None
            if start_time.tzinfo is None or timezone is not None:
                start_time = start_time.replace(
                    tzinfo=dateutil.tz.gettz(timezone))
            if end_time.tzinfo is None or timezone is not None:
                end_time = end_time.replace(tzinfo=dateutil.tz.gettz(timezone))
            start_timestamp = int(start_time.timestamp())
            end_timestamp = int(end_time.timestamp())

        payload = {
            "summary": summary,
            "description": description,
            "need_notification": need_notification,
            "start_time": {
                "date": start_date,
                "timestamp": start_timestamp,
                "timezone": timezone
            },
            "end_time": {
                "date": end_date,
                "timestamp": end_timestamp,
                "timezone": timezone
            },
            "visibility": visibility,
            "attendee_ability": attendee_ability,
            "free_busy_status": free_busy_status,
            "color": color,
            "location": location,
            "reminders": reminders,
            "recurrence": recurrence,
            "attachments": attachments,
        }

        # remove None value
        for k in list(payload.keys()):
            if isinstance(payload[k], dict):
                for kk in list(payload[k].keys()):
                    if payload[k][kk] is None:
                        del payload[k][kk]
            else:
                if payload[k] is None:
                    del payload[k]

        response = self.request("POST", url, payload)
        # resp = response.json()
        return response

    def search_event(self,
                     start_time: datetime.datetime = None,
                     end_time: datetime.datetime = None,
                     anchor_time: datetime.datetime = None,
                     page_token: str = None,
                     sync_token: str = None,
                     page_size: int = None,
                     user_id_type: str = None) -> requests.models.Response:
        """获取日程列表
        https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/list
        
        Args:
            start_time (datetime.datetime, optional): 开始时间. Defaults to None.  
                该方式只能一次性返回数据，无法进行分页。一次性返回的数据大小受page_size限制，超过限制的数据将被截断。  
                在使用start_time和end_time时，不能与page_token或sync_token一起使用。  
                在使用start_time和end_time时，不能与anchor_time一起使用。  
            end_time (datetime.datetime, optional): 结束时间. Defaults to None.  
                该方式只能一次性返回数据，无法进行分页。一次性返回的数据大小受page_size限制，超过限制的数据将被截断。  
                在使用start_time和end_time时，不能与page_token或sync_token一起使用。  
                在使用start_time和end_time时，不能与anchor_time一起使用。  
            anchor_time (datetime.datetime, optional): 锚点时间. Defaults to None.
                该参数不可与start_time和end_time一起使用。
            page_token (str, optional): 分页标记. Defaults to None.
            sync_token (str, optional): 同步标记. Defaults to None.
            page_size (int, optional): 分页大小. Defaults to None.
            user_id_type (str, optional): 用户 ID 类型. Defaults to None.

        Returns:
            requests.models.Response: 响应
        """
        if start_time is not None:
            if end_time is None:
                assert anchor_time is None, "anchor_time should be None when start_time is not None and end_time is None"
                anchor_timestamp = int(start_time.timestamp())
                start_timestamp = None
                end_timestamp = None
            else:
                start_timestamp = int(start_time.timestamp())
                end_timestamp = int(end_time.timestamp())
                anchor_timestamp = None

        params = dict(start_time=start_timestamp,
                      end_time=end_timestamp,
                      anchor_time=anchor_timestamp,
                      page_token=page_token,
                      sync_token=sync_token,
                      user_id_type=user_id_type,
                      page_size=page_size)
        print(params)
        assert (
            not (start_timestamp is None) ^ (end_timestamp is None)
        ), "start_time and end_time should be both None or both not None"
        if start_timestamp is not None:
            assert anchor_timestamp is None, "anchor_time should be None when start_time is not None"
        else:
            assert anchor_timestamp is not None, "anchor_time should not be None when end_time is not None"

        response = self.request(
            "GET",
            f"{self.url_calender}/{self.calendar_id}/events",
            params=params)
        return response

    def query_event(self,
                    query: str,
                    filter: Dict = None,
                    start_time: datetime.datetime = None,
                    end_time: datetime.datetime = None,
                    user_ids: List[str] = None,
                    room_ids: List[str] = None,
                    chat_ids: List[str] = None,
                    timezone: str = 'Asia/Shanghai',
                    user_id_type: str = None,
                    page_token: str = None,
                    page_size: int = None,
                    whole_day: bool = False):
        """搜索日程"""
        # 'https://open.feishu.cn/open-apis/calendar/v4/calendars/feishu.cn_3X9LjdmllhKRY9WIjL2odh@group.calendar.feishu.cn/events/search?page_size=20'
        params = dict(user_id_type=user_id_type,
                      page_token=page_token,
                      page_size=page_size)
        filter = filter or {}
        for key, value in {
                "start_time": start_time,
                "end_time": end_time
        }.items():
            if value is not None:
                if key in filter:
                    raise ValueError(f"{key} is already in filter")
                if whole_day:
                    filter[key] = {"date": value.strftime("%Y-%m-%d")}
                else:
                    if value.tzinfo is None or timezone is not None:
                        value = value.replace(
                            tzinfo=dateutil.tz.gettz(timezone))
                    filter[key] = {"timestamp": int(value.timestamp())}

        if timezone is not None:
            for key in ["start_time", "end_time"]:
                if key in filter:
                    filter[key]["timezone"] = timezone

        for key, value in {
                "user_ids": user_ids,
                "room_ids": room_ids,
                "chat_ids": chat_ids
        }.items():
            if value is not None:
                if key in filter:
                    raise ValueError(f"{key} is already in filter")
                filter[key] = value

        payload = dict(query=query, filter=filter)
        response = self.request(
            "POST", f"{self.url_calender}/{self.calendar_id}/events/search",
            payload, params)
        return response
