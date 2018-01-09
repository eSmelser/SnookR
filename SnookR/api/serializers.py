from rest_framework import serializers

import accounts.models
from accounts.models import CustomUser
from substitutes import models as main_models
from substitutes.models import SessionEvent, Sub
from teams.models import Team
from invites.models import TeamInvite, SessionEventInvite
from messaging.models import Message

def must_have_id(data):
    if 'id' not in data:
        raise serializers.ValidationError({
            'id': 'This field is required',
        })


class CustomUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    id = serializers.ReadOnlyField()

    def to_representation(self, instance):
        """Add the instance's URL to the returned json."""
        json = super().to_representation(instance)
        json['url'] = instance.get_absolute_url
        json['thumbnail_url'] = instance.profile.thumbnail.url if instance.profile else None
        json['is_captain'] = instance.has_perm('teams.add_team')
        request = self.context.get('request', False)
        if request:
            json['is_current_user'] = request.user.id == instance.id

        json['invite_url'] = self.context.get('invite_url', None)
        json['unregister_url'] = self.context.get('unregister_url', None)
        return json


class TeamSerializer(serializers.Serializer):
    players = CustomUserSerializer(many=True)
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=True)
    team_captain = CustomUserSerializer(required=False)

    def create(self, validated_data):
        captain = accounts.models.CustomUser.objects.get(id=self.context['request'].user.id)
        name = validated_data.get('name')
        instance = Team.objects.create(team_captain=captain, name=name)

        players = []
        for player in validated_data.get('players', []):
            players.append(accounts.models.CustomUser.objects.get(**player))

        instance.players.add(*players)
        return instance


class TeamInviteSerializer(serializers.Serializer):
    team = TeamSerializer(required=True, validators=[must_have_id])
    invitee = CustomUserSerializer(required=True)
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(required=False)

    def create(self, validated_data):
        team_id = validated_data.get('team').get('id')
        username = validated_data.get('invitee').get('username')
        team = Team.objects.get(id=team_id)
        invitee = accounts.models.CustomUser.objects.get(username=username)
        return TeamInvite.objects.create(team=team, invitee=invitee)


class TeamInviteUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(required=True)

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.save()
        return instance


class TeamReadOnlySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class NonUserPlayerSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.ReadOnlyField()
    team = TeamReadOnlySerializer(required=True)

    def create(self, validated_data):
        obj = Team.objects.get(id=validated_data.get('team').get('id'))
        return main_models.NonUserPlayer.objects.create(team=obj, name=validated_data.get('name'))


class DivisionSerializer(serializers.Serializer):
    name = serializers.CharField()


class SessionSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.ReadOnlyField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    division = DivisionSerializer()


class SessionEventSerializer(serializers.Serializer):
    session = SessionSerializer(required=False)
    date = serializers.DateField(required=False)
    start_time = serializers.TimeField(required=False)
    id = serializers.IntegerField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['registerUrl'] = instance.get_register_url
        rep['unregisterUrl'] = instance.get_unregister_url
        rep['url'] = instance.get_absolute_url

        return rep


class SubSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(required=False)
    session_event = SessionEventSerializer(required=False)
    id = serializers.ReadOnlyField()

    class Meta:
        model = main_models.Sub
        fields = ['user', 'session_event', 'id']

    def create(self, validated_data):
        event = validated_data.get('session_event')
        event = SessionEvent.objects.get(id=event.get('id'))
        user = validated_data.get('user')
        user = CustomUser.objects.get(username=user.get('username'))
        return Sub.objects.create(session_event=event, user=user)



class SessionEventWritableSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class SubWritableSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(required=False)
    session_event = SessionEventWritableSerializer(required=True)
    id = serializers.IntegerField(required=True)

    class Meta:
        model = main_models.Sub
        fields = ['user', 'session_event', 'id']


class SessionEventInviteSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    sub = SubWritableSerializer()
    team = TeamSerializer()

    class Meta:
        model = SessionEventInvite
        fields = ['sub', 'team', 'id']

    def create(self, validated_data):
        sub = validated_data.get('sub', {})
        sub = main_models.Sub.objects.get(id=sub.get('id'))
        captain = validated_data.get('captain')
        captain = CustomUser.objects.get(username=captain.get('username'))
        return SessionEventInvite.objects.create(sub=sub, captain=captain)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['receiver', 'sender', 'text', 'timestamp', 'id']
