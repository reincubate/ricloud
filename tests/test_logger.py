from ricloud.handlers import StreamError, RiCloudHandler
from ricloud.listener import Listener


class TestsLogger(object):

    def test_write(self, mocker):
        mock_logger = mocker.patch('ricloud.utils.LogFile')
        mock_RiCloudHandler = mocker.patch('ricloud.ricloud.RiCloudHandler')
        listener = Listener(
            {'__ALL__': mock_RiCloudHandler},
            log=mock_logger
        )
        listener.on_heartbeat()
        mock_logger.write.assert_called_once_with('-*- Heartbeat -*-')

    def test_error(self, mocker):
        mock_logger = mocker.patch('ricloud.utils.LogFile')
        mock_RiCloudHandler = RiCloudHandler(api=None)
        mock_RiCloudHandler.handle = mocker.patch('ricloud.ricloud.RiCloudHandler.handle')
        mock_RiCloudHandler.handle.side_effect = StreamError("Test Error")
        listener = Listener(
            {'__ALL__': mock_RiCloudHandler},
            log=mock_logger
        )
        listener.on_message('{"type": "__ALL__"}', "")
        mock_logger.error.assert_called_once_with("Test Error")
