#!/usr/bin/env python

import io
import json
import datetime
import struct

from os.path import join as pjoin
from collections import OrderedDict

import grpc
import trillian_log_api_pb2
import trillian_log_api_pb2_grpc

from pathlib import Path
from flask import Flask, render_template, request

HOME_DIR = str(Path.home())

app = Flask(__name__)

LOG_ID_FILENAME = pjoin(HOME_DIR, '.log_id')

with io.open(LOG_ID_FILENAME, 'r') as f:
    LOG_ID = int(f.read())
    print('Read log ID {} from {}'.format(LOG_ID, LOG_ID_FILENAME))


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

    def get_recent_leaves(self, number_of_leaves):
        tree_size = self.get_tree_size()

        request = trillian_log_api_pb2.GetLeavesByIndexRequest(
            log_id=self.__log_id,
        )
        indexes = range(tree_size - 1, tree_size - 1 - number_of_leaves, -1)
        request.leaf_index.extend(indexes)

        response = self.__stub.GetLeavesByIndex(request)
        return response

    def get_tree_size(self):
        return self.get_signed_log_root()['tree_size']

    def get_signed_log_root(self):
        request = trillian_log_api_pb2.GetLatestSignedLogRootRequest(
            log_id=self.__log_id,
        )

        response = self.__stub.GetLatestSignedLogRoot(request)
        self._validate_log_root_signature(
            response.signed_log_root.log_root,
            response.signed_log_root.log_root_signature
        )

        log_root_decoded = self._deserialize_log_root(
            response.signed_log_root.log_root
        )

        return log_root_decoded

    def _validate_log_root_signature(self, log_root, signature):
        pass  # TODO

    def _deserialize_log_root(self, log_root):
        # TODO: unpack the whole structure
        tree_size, = struct.unpack('>Q', log_root[2:10])  # Q = uint64

        return {
            'tree_size': tree_size
        }


TRILLIAN = Trillian('localhost', '8090', LOG_ID)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add-log/', methods=['POST'])
def queue_timestamp_to_trillian():
    now = datetime.datetime.now()

    data = json.dumps(OrderedDict([
        ('timestamp', now.isoformat()),
        ('message', request.form['log_leaf']),
    ])).encode('utf-8')

    print('Adding `{}` to Log'.format(data))

    response = TRILLIAN.queue_leaf(data)

    return render_template('add_log.html', response=response)


@app.route('/recent-logs/')
def view_logs():
    response = TRILLIAN.get_recent_leaves(3)

    return render_template('add_log.html', response=response)
