# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for subscription management."""

__author__ = 'Sean Lip'

from core.domain import exp_domain
from core.domain import exp_services
from core.domain import feedback_services
from core.domain import rights_manager
from core.domain import subscription_services
from core.platform import models
(user_models,) = models.Registry.import_models([
    models.NAMES.user
])
from core.tests import test_utils


class SubscriptionsTest(test_utils.GenericTestBase):
    """Tests for subscription management."""

    OWNER_2_EMAIL = 'owner2@example.com'
    OWNER2_USERNAME = 'owner2'

    def setUp(self):
        super(SubscriptionsTest, self).setUp()
        self.signup(self.OWNER_EMAIL, self.OWNER_USERNAME)
        self.signup(self.EDITOR_EMAIL, self.EDITOR_USERNAME)
        self.signup(self.VIEWER_EMAIL, self.VIEWER_USERNAME)
        self.signup(self.OWNER_2_EMAIL, self.OWNER2_USERNAME)

        self.owner_id = self.get_user_id_from_email(self.OWNER_EMAIL)
        self.editor_id = self.get_user_id_from_email(self.EDITOR_EMAIL)
        self.viewer_id = self.get_user_id_from_email(self.VIEWER_EMAIL)
        self.owner_2_id = self.get_user_id_from_email(self.OWNER_2_EMAIL)

    def _get_thread_ids_subscribed_to(self, user_id):
        subscriptions_model = user_models.UserSubscriptionsModel.get(
            user_id, strict=False)
        return (
            subscriptions_model.feedback_thread_ids
            if subscriptions_model else [])

    def _get_activity_ids_subscribed_to(self, user_id):
        subscriptions_model = user_models.UserSubscriptionsModel.get(
            user_id, strict=False)
        return (
            subscriptions_model.activity_ids
            if subscriptions_model else [])

    def test_subscribe_to_feedback_thread(self):
        USER_ID = 'user_id'
        self.assertEqual(self._get_thread_ids_subscribed_to(USER_ID), [])

        FEEDBACK_THREAD_ID = 'fthread_id'
        subscription_services.subscribe_to_thread(USER_ID, FEEDBACK_THREAD_ID)
        self.assertEqual(
            self._get_thread_ids_subscribed_to(USER_ID), [FEEDBACK_THREAD_ID])

        # Repeated subscriptions to the same thread have no effect.
        subscription_services.subscribe_to_thread(USER_ID, FEEDBACK_THREAD_ID)
        self.assertEqual(
            self._get_thread_ids_subscribed_to(USER_ID), [FEEDBACK_THREAD_ID])

        FEEDBACK_THREAD_2_ID = 'fthread_id_2'
        subscription_services.subscribe_to_thread(
            USER_ID, FEEDBACK_THREAD_2_ID)
        self.assertEqual(
            self._get_thread_ids_subscribed_to(USER_ID),
            [FEEDBACK_THREAD_ID, FEEDBACK_THREAD_2_ID])

    def test_subscribe_to_activity(self):
        USER_ID = 'user_id'
        self.assertEqual(self._get_activity_ids_subscribed_to(USER_ID), [])

        ACTIVITY_ID = 'activity_id'
        subscription_services.subscribe_to_activity(USER_ID, ACTIVITY_ID)
        self.assertEqual(
            self._get_activity_ids_subscribed_to(USER_ID), [ACTIVITY_ID])

        # Repeated subscriptions to the same activity have no effect.
        subscription_services.subscribe_to_activity(USER_ID, ACTIVITY_ID)
        self.assertEqual(
            self._get_activity_ids_subscribed_to(USER_ID), [ACTIVITY_ID])

        ACTIVITY_2_ID = 'activity_id_2'
        subscription_services.subscribe_to_activity(USER_ID, ACTIVITY_2_ID)
        self.assertEqual(
            self._get_activity_ids_subscribed_to(USER_ID),
            [ACTIVITY_ID, ACTIVITY_2_ID])

    def test_get_activity_ids_subscribed_to(self):
        USER_ID = 'user_id'
        self.assertEqual(
            subscription_services.get_activity_ids_subscribed_to(USER_ID), [])

        ACTIVITY_ID = 'activity_id'
        subscription_services.subscribe_to_activity(USER_ID, ACTIVITY_ID)
        self.assertEqual(
            subscription_services.get_activity_ids_subscribed_to(USER_ID), 
                [ACTIVITY_ID])

        ACTIVITY_2_ID = 'activity_id_2'
        subscription_services.subscribe_to_activity(USER_ID, ACTIVITY_2_ID)
        self.assertEqual(
            subscription_services.get_activity_ids_subscribed_to(USER_ID), 
            [ACTIVITY_ID, ACTIVITY_2_ID])

    def test_thread_and_activity_subscriptions_are_tracked_individually(self):
        USER_ID = 'user_id'
        FEEDBACK_THREAD_ID = 'fthread_id'
        ACTIVITY_ID = 'activity_id'
        self.assertEqual(self._get_thread_ids_subscribed_to(USER_ID), [])

        subscription_services.subscribe_to_thread(USER_ID, FEEDBACK_THREAD_ID)
        subscription_services.subscribe_to_activity(USER_ID, ACTIVITY_ID)
        self.assertEqual(
            self._get_thread_ids_subscribed_to(USER_ID), [FEEDBACK_THREAD_ID])
        self.assertEqual(
            self._get_activity_ids_subscribed_to(USER_ID), [ACTIVITY_ID])

    def test_posting_to_feedback_thread_results_in_subscription(self):
        # The viewer posts a message to the thread.
        MESSAGE_TEXT = 'text'
        feedback_services.create_thread(
            'exp_id', 'state_name', self.viewer_id, 'subject', MESSAGE_TEXT)

        thread_ids_subscribed_to = self._get_thread_ids_subscribed_to(
            self.viewer_id)
        self.assertEqual(len(thread_ids_subscribed_to), 1)
        thread_id = thread_ids_subscribed_to[0]
        self.assertEqual(
            feedback_services.get_messages(thread_id)[0]['text'], MESSAGE_TEXT)

        # The editor posts a follow-up message to the thread.
        NEW_MESSAGE_TEXT = 'new text'
        feedback_services.create_message(
            thread_id, self.editor_id, '', '', NEW_MESSAGE_TEXT)

        # The viewer and editor are now both subscribed to the thread.
        self.assertEqual(
            self._get_thread_ids_subscribed_to(self.viewer_id), [thread_id])
        self.assertEqual(
            self._get_thread_ids_subscribed_to(self.editor_id), [thread_id])

    def test_creating_exploration_results_in_subscription(self):
        EXP_ID = 'exp_id'
        USER_ID = 'user_id'

        self.assertEqual(
            self._get_activity_ids_subscribed_to(USER_ID), [])
        exp_services.save_new_exploration(
            USER_ID,
            exp_domain.Exploration.create_default_exploration(
                EXP_ID, 'Title', 'Category'))
        self.assertEqual(
            self._get_activity_ids_subscribed_to(USER_ID), [EXP_ID])

    def test_adding_new_owner_or_editor_role_results_in_subscription(self):
        EXP_ID = 'exp_id'
        exploration = exp_domain.Exploration.create_default_exploration(
            EXP_ID, 'Title', 'Category')
        exp_services.save_new_exploration(self.owner_id, exploration)

        self.assertEqual(
            self._get_activity_ids_subscribed_to(self.owner_2_id), [])
        rights_manager.assign_role(
            self.owner_id, EXP_ID, self.owner_2_id, rights_manager.ROLE_OWNER)
        self.assertEqual(
            self._get_activity_ids_subscribed_to(self.owner_2_id), [EXP_ID])

        self.assertEqual(
            self._get_activity_ids_subscribed_to(self.editor_id), [])
        rights_manager.assign_role(
            self.owner_id, EXP_ID, self.editor_id, rights_manager.ROLE_EDITOR)
        self.assertEqual(
            self._get_activity_ids_subscribed_to(self.editor_id), [EXP_ID])

    def test_adding_new_viewer_role_does_not_result_in_subscription(self):
        EXP_ID = 'exp_id'
        exploration = exp_domain.Exploration.create_default_exploration(
            EXP_ID, 'Title', 'Category')
        exp_services.save_new_exploration(self.owner_id, exploration)

        self.assertEqual(
            self._get_activity_ids_subscribed_to(self.viewer_id), [])
        rights_manager.assign_role(
            self.owner_id, EXP_ID, self.viewer_id, rights_manager.ROLE_VIEWER)
        self.assertEqual(
            self._get_activity_ids_subscribed_to(self.viewer_id), [])

    def test_deleting_activity_does_not_delete_subscription(self):
        EXP_ID = 'exp_id'
        exploration = exp_domain.Exploration.create_default_exploration(
            EXP_ID, 'Title', 'Category')
        exp_services.save_new_exploration(self.owner_id, exploration)
        self.assertEqual(
            self._get_activity_ids_subscribed_to(self.owner_id), [EXP_ID])

        exp_services.delete_exploration(self.owner_id, EXP_ID)
        self.assertEqual(
            self._get_activity_ids_subscribed_to(self.owner_id), [EXP_ID])
