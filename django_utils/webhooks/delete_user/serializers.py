from rest_framework import serializers


class InquireDeleteUserSerializer(serializers.Serializer):
    userid = serializers.CharField()


class SubscribeUserDeleteSerializer(InquireDeleteUserSerializer):
    pass
