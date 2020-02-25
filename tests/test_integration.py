from __future__ import absolute_import

import pytest

import ricloud
from ricloud.samples.utils import await_response


USER_IDENTIFIER = "testing@reincubate.com"
SOURCE_IDENTIFIER = "john.appleseed@reincubate.com"


@pytest.mark.integration
class TestIntegration(object):
    def test_ok(self):
        user = ricloud.User.create(identifier=USER_IDENTIFIER)

        assert isinstance(user, ricloud.User)
        assert user.identifier == USER_IDENTIFIER

        session = ricloud.Session.create(
            source={
                "user": user,
                "type": "mocks.mock",
                "identifier": SOURCE_IDENTIFIER,
            },
            payload={"password": "abcd1234"},
        )

        assert isinstance(session, ricloud.Session)

        await_response(session)

        assert session.state == "active"

        info_poll = ricloud.Poll.create(session=session, payload={"info_types": ["*"]})

        assert isinstance(info_poll, ricloud.Poll)

        await_response(info_poll)

        assert info_poll.state == "completed"
