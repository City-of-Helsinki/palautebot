from datetime import datetime

from tweepy import API
from tweepy.binder import bind_api
from tweepy.error import TweepError
from tweepy.models import DirectMessage, ModelFactory
from tweepy.parsers import JSONParser, ModelParser


class CustomTweepyAPI(API):

    @property
    def direct_messages(self):
        """ :reference: https://dev.twitter.com/rest/reference/get/direct_messages
            :allowed_param:'since_id', 'max_id', 'count', 'full_text'
        """
        return bind_api(
            api=self,
            path='/direct_messages/events/list.json',
            payload_type='direct_message', payload_list=True,
            allowed_param=['count', 'cursor'],
            require_auth=True
        )


class CustomDirectMessage(DirectMessage):

    @classmethod
    def parse(cls, api, json):
        dm = cls(api)
        for k, v in json.items():
            if k == 'id':
                setattr(dm, 'id_str', v)
            elif k == 'created_timestamp':
                setattr(dm, 'created_at', datetime.fromtimestamp(int(v) / 1000.0))
            elif k == 'message_create':
                message_object = v
                for key, value in message_object.items():
                    if key == 'target':
                        setattr(dm, 'recipient', api.get_user(value['recipient_id']))
                    elif key == 'sender_id':
                        setattr(dm, 'sender', api.get_user(value))
                    elif key == 'message_data':
                        message_object = value
                        for data_key, data_value in message_object.items():
                            setattr(dm, data_key, data_value)
                    else:
                        setattr(dm, key, value)
            else:
                setattr(dm, k, v)
        return dm


class CustomModelFactory(ModelFactory):
    direct_message = CustomDirectMessage


class CustomModelParser(ModelParser):
    def parse(self, method, payload):
        try:
            if method.payload_type is None:
                return
            model = getattr(self.model_factory, method.payload_type)
        except AttributeError:
            raise TweepError('No model for this payload type: '
                             '%s' % method.payload_type)

        json = JSONParser.parse(self, method, payload)
        if isinstance(json, tuple):
            json, cursors = json
        else:
            cursors = None

        if method.payload_list:
            if 'events' in json:
                result = model.parse_list(method.api, json['events'])
            else:
                result = model.parse_list(method.api, json)
        else:
            result = model.parse(method.api, json)

        if cursors:
            return result, cursors
        else:
            return result


custom_parser = CustomModelParser(model_factory=CustomModelFactory)
