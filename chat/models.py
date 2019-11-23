from django.db import models

from django.conf import settings
from django.db import models
from django.db.models import Q
from advert.models import Advert


class InboxManager(models.Manager):
    def get_or_new(self, user):
        qs = self.get_queryset().filter(owner=user) #.distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            obj = self.model(
                    owner=user,
                )
            obj.save()
            return obj, True
        return None, False


class Inbox(models.Model):
    owner        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inbox')
    updated      = models.DateTimeField(auto_now=True)
    timestamp    = models.DateTimeField(auto_now_add=True)

    objects      = InboxManager()

    @property
    def room_group_name(self):
        return f"inbox_{self.id}"

    def broadcast(self, msg=None):
        if msg is not None:
            broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
            return True
        return False

    @property
    def threads(self):
        return Thread.objects.by_user(self.owner)



    def get_latest_msg_all_threads(self):
        #Hämtar historik från alla mina egna chattar
        myThreads = self.threads.all().prefetch_related("messages", "messages__sender")\
        .select_related("first_inbox","second_inbox", "first_inbox__owner", "second_inbox__owner")

        latestMsgDict = {"data":[]}
        for thread in myThreads.all():
            #Går igenom alla threads och hämtar det senaste meddelandet från dessa
            thread_data = {}
            if thread.first_inbox.owner == self.owner:
                thread_data["thread_participant"] = thread.second_inbox.owner.username
                thread_data["thread_participant_id"] = thread.second_inbox.owner.id
            else:
                thread_data["thread_participant"] = thread.first_inbox.owner.username
                thread_data["thread_participant_id"] = thread.first_inbox.owner.id

            if thread.messages.all().exists():
                latestMsg = thread.messages.all().latest()

                thread_data["message"]   = latestMsg.message
                thread_data["sender"]    = latestMsg.sender.username
                thread_data["sender_id"] = latestMsg.sender.id
                latestMsgDict["data"].append(thread_data)

        return latestMsgDict

        def get_history_specific_thread(self,participant):
            #Hämta historiken från en specifik thread
            thread = Thread.objects.by_user(participant)\
            .prefetch_related("messages").select_related("messages__sender")

            messages = thread.messages.all().order_by("-timestamp")
            return messages
            #self.threads.filter(Q(first_inbox=participant.inbox)|Q(second_inbox=participant.inbox))\
            #.prefetch_related("messages").select_related("messages__sender").order_by("-timestamp")[0]




        # return ChatMessage.objects.filter(Q(incoming_inbox=self) | Q(outgoing_inbox=self))\
        # .order_by('-timestamp').only('sender','message','sender__username', 'receiver__username')

class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first_inbox=user.inbox) | Q(second_inbox=user.inbox)
        qlookup2 = Q(first_inbox=user.inbox) & Q(second_inbox=user.inbox)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    # method to grab the thread for the 2 users
    def get_or_new(self, user, other_user): # get_or_create
        if user == other_user:
            return None, None
        # looks based off of either username
        qlookup1 = Q(first_inbox__owner=user) & Q(second_inbox__owner=other_user)
        qlookup2 = Q(first_inbox__owner=other_user) & Q(second_inbox__owner=user)
        qs = self.get_queryset().filter(qlookup1 | qlookup2)\
        .select_related("first_inbox","second_inbox", "first_inbox__owner", "second_inbox__owner").distinct()
        if qs.count() == 1:
            thread = qs.first()
        elif qs.count() > 1:
            thread = qs.order_by('timestamp').first()
        else:
            thread = self.model(
                    first_inbox=user.inbox,
                    second_inbox=Inbox.objects.get_or_new(other_user)[0]
                )
            thread.save()

        if thread.first_inbox.owner == user:
            return thread, True
        else:
            return thread, False

        return None, False


class Thread(models.Model):
    first_inbox  = models.ForeignKey(Inbox, on_delete=models.CASCADE, related_name='first_thread')
    second_inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE, related_name='second_thread')
    updated      = models.DateTimeField(auto_now=True)
    timestamp    = models.DateTimeField(auto_now_add=True)

    objects      = ThreadManager()

    def __str__(self):
        return f'{self.id}'

    @property
    def room_group_name(self):
        return f'chat_{self.id}'

    @property
    def messages(self):
        return ChatMesage.objects.filter(thread=self)

    def broadcast(self, msg=None):
        if msg is not None:
            broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
            return True
        return False

    def get_history(self,startIndex=0,endIndex=12):
        moreMsgsExist = True
        messages = self.messages.all().order_by('-timestamp')
        messageCount = messages.count()

        if startIndex > messageCount:
            startIndex = messageCount -1
            endIndex = messageCount
            moreMsgsExist = False
            newStartIndex = startIndex
            newEndIndex = endIndex
            print('första')

        elif endIndex >= messageCount:
            endIndex = messageCount
            moreMsgsExist = False
            newStartIndex = endIndex
            newEndIndex = endIndex
            print('andra')

        if moreMsgsExist:
            print('tredje')
            newStartIndex = endIndex
            newEndIndex = endIndex + 10
            if newEndIndex > messageCount:
                print('fjärde')
                newEndIndex = messageCount

        messages = messages[startIndex:endIndex]

        msg_data = {"data":[]}

        for msg in messages.iterator():
            message={}
            #if msg.sender.username ==
            message["sender"]=msg.sender.username
            message["sender_id"]=msg.sender.id
            message["message"]=msg.message
            msg_data["data"].append(message)

        msg_data["pagination"] = {
        "more_msgs_exist": moreMsgsExist,
        "startIndex": newStartIndex,
        "endIndex": newEndIndex
        }

        return msg_data


class ChatMessage(models.Model):
    thread         = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    sender         = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender', on_delete=models.CASCADE)
    message        = models.TextField()
    timestamp      = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'
