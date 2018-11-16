test_direct_message_json = """{
    "created_at": "Mon Aug 27 17:21:03 +0000 2012",
    "entities": {
        "hashtags": [],
        "urls": [{"expanded_url": "https://twitter.com/fooman/status/98765"}],
        "user_mentions": []
    },
    "id": 240136858829479936,
    "id_str": "240136858829479936",
    "recipient": {
        "contributors_enabled": false,
        "created_at": "Thu Aug 23 19:45:07 +0000 2012",
        "default_profile": false,
        "default_profile_image": false,
        "description": "Keep calm and test",
        "favourites_count": 0,
        "follow_request_sent": false,
        "followers_count": 0,
        "following": false,
        "friends_count": 10,
        "geo_enabled": true,
        "id": 776627022,
        "id_str": "776627022",
        "is_translator": false,
        "lang": "en",
        "listed_count": 0,
        "location": "San Francisco, CA",
        "name": "Mick Jagger",
        "notifications": false,
        "profile_background_color": "000000",
        "profile_background_image_url": "http://a0.twimg.com/profile_background_images/644522235/cdjlccey99gy36j3em67.jpeg",
        "profile_background_image_url_https": "https://si0.twimg.com/profile_background_images/644522235/cdjlccey99gy36j3em67.jpeg",
        "profile_background_tile": true,
        "profile_image_url": "http://a0.twimg.com/profile_images/2550226257/y0ef5abcx5yrba8du0sk_normal.jpeg",
        "profile_image_url_https": "https://si0.twimg.com/profile_images/2550226257/y0ef5abcx5yrba8du0sk_normal.jpeg",
        "profile_link_color": "000000",
        "profile_sidebar_border_color": "000000",
        "profile_sidebar_fill_color": "000000",
        "profile_text_color": "000000",
        "profile_use_background_image": false,
        "protected": false,
        "screen_name": "s0c1alm3dia",
        "show_all_inline_media": false,
        "statuses_count": 0,
        "time_zone": "Pacific Time (US & Canada)",
        "url": "http://cnn.com",
        "utc_offset": -28800,
        "verified": false
    },
    "recipient_id": 776627022,
    "recipient_screen_name": "s0c1alm3dia",
    "sender": {
        "contributors_enabled": true,
        "created_at": "Sat May 09 17:58:22 +0000 2009",
        "default_profile": false,
        "default_profile_image": false,
        "description": "I taught your phone that thing you like.  The Mobile Partner Engineer @Twitter. ",
        "favourites_count": 584,
        "follow_request_sent": false,
        "followers_count": 10621,
        "following": false,
        "friends_count": 1181,
        "geo_enabled": true,
        "id": 38895958,
        "id_str": "38895958",
        "is_translator": false,
        "lang": "en",
        "listed_count": 190,
        "location": "San Francisco",
        "name": "Sean Cook",
        "notifications": false,
        "profile_background_color": "1A1B1F",
        "profile_background_image_url": "http://a0.twimg.com/profile_background_images/495742332/purty_wood.png",
        "profile_background_image_url_https": "https://si0.twimg.com/profile_background_images/495742332/purty_wood.png",
        "profile_background_tile": true,
        "profile_image_url": "http://a0.twimg.com/profile_images/1751506047/dead_sexy_normal.JPG",
        "profile_image_url_https": "https://si0.twimg.com/profile_images/1751506047/dead_sexy_normal.JPG",
        "profile_link_color": "2FC2EF",
        "profile_sidebar_border_color": "181A1E",
        "profile_sidebar_fill_color": "252429",
        "profile_text_color": "666666",
        "profile_use_background_image": true,
        "protected": false,
        "screen_name": "theSeanCook",
        "show_all_inline_media": true,
        "statuses_count": 2608,
        "time_zone": "Pacific Time (US & Canada)",
        "url": null,
        "utc_offset": -28800,
        "verified": false
    },
    "sender_id": 38895958,
    "sender_screen_name": "theSeanCook",
    "text": "https://twitter.com/fooman/status/98765"
}"""

new_direct_message_api_response = """{
    "events": [
        {
            "type": "message_create",
            "id": "12345678987654321",
            "created_timestamp": "1542113610846",
            "message_create": {
                "target": {
                    "recipient_id": "123456789"
                },
                "sender_id": "987654321",
                "source_app_id": "268278",
                "message_data": {
                    "text": "https:\/\/t.co\/SxhSwDrnGu",
                    "entities": {
                        "hashtags": [],
                        "symbols": [],
                        "user_mentions": [],
                        "urls": [
                            {
                                "url": "https:\/\/t.co\/SxhSwDrnGu",
                                "expanded_url": "https:\/\/twitter.com\/fooman\/status\/1042411246337884160",
                                "display_url": "twitter.com\/fooman\u2026",
                                "indices": [0,23]
                            }
                        ]
                    }
                }
            }
        }    
    ],
    "apps": {
        "268278": {
            "id": "268278",
            "name": "Twitter Web Client",
            "url": "http:\/\/twitter.com"
        }
    }
}"""
