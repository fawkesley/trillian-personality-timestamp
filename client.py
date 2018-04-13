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


def main(argv):
    with io.open(pjoin(HOME_DIR, '.log_id'), 'r') as f:
        log_id = int(f.read())

    channel = grpc.insecure_channel('localhost:8090')
    stub = trillian_log_api_pb2_grpc.TrillianLogStub(channel)

    while True:
        now = datetime.datetime.now()
        timestamp_data = now.isoformat().encode('utf-8')

        print('Adding `{}` to Log'.format(timestamp_data))

        leaf = trillian_log_api_pb2.LogLeaf(leaf_value=timestamp_data)

        request = trillian_log_api_pb2.QueueLeafRequest(
            log_id=log_id,
            leaf=leaf
        )
        response = stub.QueueLeaf(request)
        print(response)

        time.sleep(5)


if __name__ == '__main__':
    main(sys.argv)
