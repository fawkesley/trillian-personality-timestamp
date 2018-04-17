#!/usr/bin/env python

import io
import datetime
import sys
import time

from os.path import join as pjoin

import grpc
import trillian_log_api_pb2
import trillian_log_api_pb2_grpc

from pathlib import Path

HOME_DIR = str(Path.home())


class Trillian():
    def __init__(self, host, port, log_id):
        self.__channel = grpc.insecure_channel('{}:{}'.format(host, port))
        self.__stub = trillian_log_api_pb2_grpc.TrillianLogStub(self.__channel)
        self.__log_id = log_id

    def queue_leaf(self, data):
        leaf = trillian_log_api_pb2.LogLeaf(leaf_value=data)

        request = trillian_log_api_pb2.QueueLeafRequest(
            log_id=self.__log_id,
            leaf=leaf
        )
        return self.__stub.QueueLeaf(request)


def main(argv):
    with io.open(pjoin(HOME_DIR, '.log_id'), 'r') as f:
        log_id = int(f.read())

    trillian = Trillian('localhost', '8090', log_id)

    while True:
        now = datetime.datetime.now()
        timestamp_data = now.isoformat().encode('utf-8')

        print('Adding `{}` to Log'.format(timestamp_data))

        response = trillian.queue_leaf(timestamp_data)

        print(response)

        time.sleep(5)


if __name__ == '__main__':
    main(sys.argv)
