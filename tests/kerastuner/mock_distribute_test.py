# Copyright 2019 The Keras Tuner Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test mock running KerasTuner in a distributed tuning setting."""

import os
import pytest
import tensorflow as tf
import time
from .mock_distribute import mock_distribute


@pytest.fixture(scope='module')
def tmp_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('integration_test')


def test_mock_distribute(tmp_dir):
    def process_fn():
        tuner_id = os.environ['KERASTUNER_TUNER_ID']
        if 'worker' in tuner_id:
            # Give the chief process time to write its value,
            # as we do not join on the chief since it will run
            # a server.
            time.sleep(2)
        fname = os.path.join(tmp_dir, tuner_id)
        with tf.io.gfile.GFile(fname, 'w') as f:
            f.write(tuner_id)

    mock_distribute(process_fn, num_workers=3)

    for tuner_id in {'chief', 'worker0', 'worker1', 'worker2'}:
        fname = os.path.join(tmp_dir, tuner_id)
        with tf.io.gfile.GFile(fname, 'r') as f:
            assert f.read() == tuner_id