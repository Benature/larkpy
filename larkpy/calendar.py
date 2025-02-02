from __future__ import annotations
from .api import FeishuAPI
from typing_extensions import Literal
from typing import List, Dict
import json
from pathlib import Path
import requests
import datetime


class FeishuCalendar(FeishuAPI):

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

    def create_event(self,
                     start_time: datetime.datetime,
                     end_time: datetime.datetime,
                     summary: str = None,
                     description: str = None,
                     need_notification: bool = None,
                     visibility: Literal['default', 'public',
                                         'private'] = None,
                     attendee_ability: Literal['none', 'can_see_others',
                                               'can_invite_others',
                                               'can_modify_event'] = None,
                     free_busy_status: Literal['busy', 'free'] = None,
                     location: Dict[Literal['name', 'address', 'latitude',
                                            'longitude'], str | float] = None,
                     color: int = None,
                     reminders: List[Dict[Literal['minutes'], int]] = None,
                     recurrence: str = None,
                     attachments: List[Dict[Literal['file_token'],
                                            str]] = None,
                     timezone: str = None,
                     user_id_type: Literal['user_id', 'union_id',
                                           'open_id'] = 'user_id'):
        """新建日程
        https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/create?appId=cli_a7cd947b13f91013&lang=zh-CN
        """
        url = f"{self.url_calender}/{self.calendar_id}/events?user_id_type={user_id_type}"
        start_time = int(start_time.timestamp())
        end_time = int(end_time.timestamp())

        payload = {
            "summary": summary,
            "description": description,
            "need_notification": need_notification,
            "start_time": {
                "timestamp": start_time,
                "timezone": timezone
            },
            "end_time": {
                "timestamp": end_time,
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
