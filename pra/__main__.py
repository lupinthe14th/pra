#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import os
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser
from logging import DEBUG, INFO, basicConfig, getLogger

import pytz
from redminelib import Redmine
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from .setting import APIKEY, ENDPOINT, VERIFY


class ActivityList(metaclass=ABCMeta):
    def __init__(self, endpoint=None, apikey=None, verify=True):
        self.endpoint = endpoint
        self.apikey = apikey
        self.verify = verify
        os.environ["REQUESTS_CA_BUNDLE"] = "/etc/ssl/certs/ca-certificates.crt"

    def client(self):
        if not self.verify:
            disable_warnings(InsecureRequestWarning)
            del os.environ["REQUESTS_CA_BUNDLE"]

        return Redmine(self.endpoint, key=self.apikey, requests={"verify": self.verify})

    @abstractmethod
    def today(self):
        raise NotImplementedError


class ActivityIssueList(ActivityList):
    """Issueのアクティビティリストに関するクラス.
    """

    def today(self, **kwargs):
        """ログイン者の当日以降に更新されたIssueを取得する.

        notes
        -----
        日時の時は、UTCなので00:00:00で固定。当日09:00:00以降更新があったのを抽出する。

        """
        filter = {
            "updated_on": "{0}{1}".format(
                ">=", datetime.date.today().strftime("%Y-%m-%dT00:00:00Z")
            ),
            "assigned_to_id": "me",
            "status_id": "*",
        }
        filter.update(**kwargs)
        return self.client().issue.filter(**filter)


def main():
    meta = {"endpoint": ENDPOINT, "apikey": APIKEY, "verify": VERIFY}

    params = {"sort": "updated_on:desc"}

    ail = ActivityIssueList(**meta)
    for l in ail.today(**params):
        if list(l):
            print("- `{0} #{1} <{2}>`_".format(l.subject, l.id, l.url))
            print()
            print("   :ステータス: {}".format(l.status))
            print(
                "   :Last update: {}".format(
                    pytz.utc.localize(l.updated_on)
                    .astimezone(pytz.timezone("Asia/Tokyo"))
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
            )

        print()


if __name__ == "__main__":

    logger = getLogger(__name__)
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", help="debug mode", action="store_true")
    args = parser.parse_args()
    if args.debug:
        basicConfig(level=DEBUG)
    else:
        basicConfig(level=INFO)
    main()


# vim: set fileencoding=utf-8 :
