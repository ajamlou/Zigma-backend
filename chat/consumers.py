import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from .models import Inbox, ChatMessage, Thread
from django.contrib.auth.models import User, AnonymousUser
from rest_framework.authtoken.models import Token
from channels.exceptions import StopConsumer

class InboxConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)

        me = self.scope["user"]
        my_inbox, created = await self.get_inbox(me)
        self.my_inbox=my_inbox
        self.my_room = f"inbox_{my_inbox.id}"

        await self.channel_layer.group_add(
        self.my_room,
        self.channel_name
        )

        await self.send({
        "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        print("recieve", event)
        text_data = event.get("text")
        if text_data is not None:
            dict_data = json.loads(text_data)
            command = dict_data.get("command")
            if command is not None:
                if command == "get_history":
                    await self.get_message_history()

    async def get_message_history(self):
        msg_history = await self.get_inbox_history()

        # msg_data = {"data":[]}
        # for msg in allMsgs.iterator():
        #     message={}
        #     message["sender"]=msg.sender.username
        #     message["sender_id"]=msg.sender.id
        #     message['receiver']=msg.receiver.username
        #     message["receiver_id"]=msg.receiver.id
        #     message["message"]=msg.message
        #     msg_data["data"].append(message)

        await self.send({
        "type": "websocket.send",
        "text": json.dumps(msg_history, ensure_ascii=False)
        })

    async def chat_message(self,event):
        await self.send({
        "type":"websocket.send",
        "text":event['text']
        })

    async def websocket_disconnect(self,event):
        await self.channel_layer.group_discard(
            self.my_room,
            self.channel_name
            )
        raise StopConsumer

    @database_sync_to_async
    def get_inbox(self,user):#,advert_id):
        return Inbox.objects.get_or_new(user)#,advert_id)

    @database_sync_to_async
    def get_inbox_history(self):
        return self.my_inbox.get_latest_msg_all_threads()


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        me = self.scope["user"]
        you = self.scope["other_user"] = User.objects.filter(\
        username=self.scope['url_route']['kwargs']['username']).only('username')[0]

        if me == AnonymousUser():
            return

        shared_thread, meIsFirst = await self.get_thread(me, you)
        self.shared_thread = shared_thread

        if meIsFirst:
            my_room = f"inbox_{shared_thread.first_inbox.id}"
            your_room = f"inbox_{shared_thread.second_inbox.id}"
        else:
            my_room = f"inbox_{shared_thread.second_inbox.id}"
            your_room = f"inbox_{shared_thread.first_inbox.id}"

        self.my_room = my_room
        self.your_room = your_room



        #advert_id = self.scope['url_route']['kwargs']['advert_id']
        #if me.username != you.username:
        # your_inbox, created = await self.get_inbox(you)#,advert_id)
        # self.your_inbox=your_inbox
        # your_room = f"inbox_{your_inbox.id}"
        # self.your_room = your_room
        # else:
        #     self.your_inbox=self.my_inbox
        #     your_room = f"inbox_{self.your_inbox.id}"
        #     self.your_room = your_room

        await self.channel_layer.group_add(
        my_room,
        self.channel_name
        )

        await self.send({
        "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        print("receive", event)
        text_data = event.get("text")
        if text_data is not None:
            dict_data = json.loads(text_data)
            command = dict_data.get("command")
            if command is not None:
                if command == "get_history":
                    startIndex = dict_data.get("start_index") if dict_data.get("start_index") is not None else 0
                    endIndex = dict_data.get("end_index") if dict_data.get("end_index") is not None else startIndex + 10

                    await self.get_message_history(startIndex,endIndex)
            else:
                #{'type': 'websocket.receive', 'text': {'message':'hej hej!'}}
                me = self.scope['user']
                you = self.scope['other_user']
                msg = dict_data.get("message")
                response = {
                "message":msg,
                "sender":me.username,
                "sender_id":me.id
                }

                response_dump = json.dumps(response, ensure_ascii=False)

                await self.create_message(msg)

                await self.channel_layer.group_send(
                self.my_room,
                {
                "type":"chat_message",
                "text":response_dump
                }
                )

                await self.channel_layer.group_send(
                self.your_room,
                {
                "type":"chat_message",
                "text":response_dump
                }
                )

    async def chat_message(self,event):
        await self.send({
        "type":"websocket.send",
        "text":event['text']
        })

    async def get_message_history(self, startIndex,endIndex):
        msg_data = await self.get_inbox_history(startIndex,endIndex)

        await self.send({
        "type": "websocket.send",
        "text": json.dumps(msg_data, ensure_ascii=False)
        })



    async def websocket_disconnect(self,event):
        await self.channel_layer.group_discard(
            self.my_room,
            self.channel_name
            )
        raise StopConsumer

    @database_sync_to_async
    def get_thread(self,me,participant):#,advert_id):
        return Thread.objects.get_or_new(me, participant)#,advert_id)

    @database_sync_to_async
    def get_inbox_history(self, startIndex, endIndex):
        inbox_exchange_between_me_and_other = self.shared_thread.get_history(startIndex,endIndex)
        return inbox_exchange_between_me_and_other
            #return None

    @database_sync_to_async
    def create_message(self,msg):
        #Sparar msgs till databasen
        me = self.scope['user']
        you = self.scope['other_user']
        return ChatMessage.objects.create(\
        thread = self.shared_thread,
        sender=me,
        message=msg
        )#,advert_id)
