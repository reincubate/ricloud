import responses
import json

from ricloud.conf import settings


def register_502_response():

    responses.add(
                method=responses.POST,
                url=settings.get('endpoints', 'login'),
                body=r"""
                        {
                            "key": "ae354ef8-b7b6-4a40-843f-96dddff3c64f",
                            "devices": {
                                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa": {
                                    "latest-backup": "2014-06-25 22:19:31.000000",
                                    "model": "N88AP",
                                    "device_name": "John Appleseed's iPhone",
                                    "colour": "white",
                                    "name": "iPhone 3GS"
                                }
                            }
                        }
                    """
                )

    responses.add(
        method=responses.POST,
        url=settings.get('endpoints', 'download_data'),
        status=502,
    )


def register_valid_responses():


    print settings.get('endpoints', 'deactivation')
    device_id = '1'
    responses.add(
                method=responses.POST,
                url=settings.get('endpoints', 'deactivation'),
                json={
                    'message': 'Device: %s has been deactivated' % device_id
                     },
                status=200,
            )

    print settings.get('endpoints', 'activation')
    device_id = '1'
    responses.add(
                method=responses.POST,
                url=settings.get('endpoints', 'activation'),
                json={
                    'message': 'Device: %s has been activated' % device_id
                     },
                status=200,
            )

    print settings.get('endpoints', 'login')
    responses.add(
                method=responses.POST,
                url=settings.get('endpoints', 'login'),
                body=r"""
                        {
                            "key": "ae354ef8-b7b6-4a40-843f-96dddff3c64f",
                            "devices": {
                                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa": {
                                    "latest-backup": "2014-06-25 22:19:31.000000",
                                    "model": "N88AP",
                                    "device_name": "John Appleseed's iPhone",
                                    "colour": "white",
                                    "name": "iPhone 3GS"
                                }
                            }
                        }
                    """
                )

    responses.add(
            method=responses.POST,
            url=settings.get('endpoints', 'download_data'),
            body=r"""
                    {
                        "call_history": [
                            {
                                "duration": 0.0,
                                "answered": false,
                                "from_me": false,
                                "date": "2014-10-11 10:16:28.659735",
                                "address": "07123456789"
                            },
                            {
                                "duration": 48.0,
                                "answered": true,
                                "from_me": false,
                                "date": "2014-10-11 10:40:48.496651",
                                "address": null
                            }
                        ],
                        "contacts": [
                             {
                                "records": [
                                    {
                                        "type": "Phone",
                                        "value": "07123 456789"
                                    }
                                ],
                                "first_name": "Test",
                                "last_name": "User"
                            }
                        ],
                        "sms": [
                            {
                                "date": "2014-10-08 00:39:38.000000",
                                "text": "Hi this is a test text",
                                "from_me": false,
                                "number": "+447123456789",
                                "attachments": []
                            },
                            {
                                "date": "2014-10-11 09:58:14.000000",
                                "text": "Your WhatsApp code is 416-741 but you can simply tap on this link to verify your device:\n\nv.whatsapp.com/416741",
                                "from_me": false,
                                "number": "99999",
                                "attachments": []
                            },
                            {
                                "date": "2014-10-11 10:43:50.000000",
                                "text": "Foor and bar",
                                "from_me": true,
                                "number": "+447123456789",
                                "attachments": []
                            },
                            {
                                "date": "2014-10-11 10:52:44.000000",
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur non tortor dolor. Maecenas pretium sapien lorem, nec tristique arcu malesuada eget. Vestibulum at pretium augue. Fusce tempor vehicula cursus. Ut luctus nisi nec neque mattis malesuada. Sed dignissim, lectus maximus fringilla sodales, nunc tortor convallis lectus, vel fermentum augue est et orci. Nulla ut quam dictum, eleifend neque in, dignissim turpis. Duis vel arcu tortor. Nam eget malesuada eros, eu pharetra risus. Nulla facilisi. Aliquam erat volutpat. Nullam porta urna eu lorem consequat, eget tempus turpis sodales. Praesent cursus magna a consectetur venenatis. Phasellus dignissim libero nec purus sodales mattis pellentesque blandit arcu. Quisque neque nisi, viverra et interdum eu, vestibulum non magna. In sed viverra neque. Morbi sollicitudin lacus in elit porta, sollicitudin tincidunt lectus efficitur. Vestibulum venenatis euismod nunc, quis pretium nunc dignissim a. Nam nec dictum libero, vel aliquet risus. Sed aliquet lorem ut libero ultrices dictum.",
                                "from_me": false,
                                "number": "+4471234567890",
                                "attachments": []
                            }
                        ],
                        "photos": [
                            {
                                "filename": "IMG_0001.JPG",
                                "file_id": "343e26971dfe9c395c425c0ccf799df63ae6261e"
                            }
                        ],
                        "browser_history": [
                            {
                                "url": "https://www.google.co.uk/search?q=test&ie=UTF-8&oe=UTF-8&hl=en&client=safari",
                                "last_visit": "2014-10-11 20:00:28.417141",
                                "title": "test - Google Search"
                            },
                            {
                                "url": "http://m.bbc.co.uk/news/",
                                "last_visit": "2014-10-12 09:40:47.248116",
                                "title": "Home - BBC News"
                            }
                        ],
                        "installed_apps": [
                            {
                                "name": "Google Maps",
                                "description": "The Google Maps app for iPhone and iPad makes navigating your world faster and easier. Find the best spots in town and the information you need to get there.\n\n\u2022 Comprehensive, accurate maps in 220 countries and territories\n\u2022 Voice-guided GPS navigation for driving, biking, and walking\n\u2022 Transit directions and maps for over 15,000 cities and towns\n\u2022 Live traffic conditions, incident reports, and automatic rerouting to find the best route\n\u2022 Detailed information on more than 100 million places\n\u2022 Street View and indoor imagery for restaurants, museums, and more\n\n* Some features not available in all countries\n* Continued use of GPS running in the background can dramatically decrease battery life.",
                                "advisory-rating": "12+",
                                "author": "Google, Inc."
                            },
                            {
                                "name": "Spotify Music",
                                "description": "\ufeffSpotify is the best way to listen to music on mobile or tablet. \n\nSearch for any track, artist or album and listen for free. Make and share playlists. Build your biggest, best ever music collection. \n\nGet inspired with personal recommendations, and readymade playlists for just about everything.\n\nListen absolutely free with ads, or get Spotify Premium.\n\nFree on mobile\n\u2022 Play any artist, album, or playlist in shuffle mode.\n\nFree on tablet\n\u2022 Play any song, any time.\n\nPremium features\n\u2022 Play any song, any time on any device: mobile, tablet or computer.\n\u2022 Enjoy ad-free music. \n\u2022 Listen offline. \n\u2022 Get better sound quality.\n\nLove Spotify?\u00a0\nLike us on Facebook: http://www.facebook.com/spotify\u00a0\nFollow us on Twitter: http://twitter.com/spotify",
                                "advisory-rating": "12+",
                                "author": "Spotify Ltd."
                            }
                        ]
                    }
            """
        )

    responses.add(
            method=responses.POST,
            url=settings.get('endpoints', 'download_file'),
            body="I am a file..."
        )


def register_2fa_responses():
    responses.add(
                method=responses.POST,
                url=settings.get('endpoints', 'login'),
                body=r"""{
                        "error": "2fa-required",
                        "message": "This account has Two Factor authentication enabled, please select a device to challenge.",
                        "data": {
                            "trustedDevices": ["********02"],
                            "key": "ae354ef8-b7b6-4a40-843f-96dddff3c64f"
                        }
                    }
                """,
                status=409
                )

