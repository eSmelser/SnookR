from rest_framework import serializers
#from main.models import Team, TeamInvite, CustomUser, NonUserPlayer, Session, SessionEvent
from main import models

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
        return json


class TeamSerializer(serializers.Serializer):
    players = CustomUserSerializer(many=True)
    team_captain = CustomUserSerializer(required=True)
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=True)

    def create(self, validated_data):
        captain = CustomUser.objects.get(**validated_data.get('team_captain'))
        name = validated_data.get('name')
        instance = Team.objects.create(team_captain=captain, name=name)

        players = []
        for player in validated_data.get('players', []):
            players.append(CustomUser.objects.get(**player))

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
        invitee = CustomUser.objects.get(username=username)
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
        return NonUserPlayer.objects.create(team=obj, name=validated_data.get('name'))


class DivisionSerializer(serializers.Serializer):
    name = serializers.CharField()


class SessionSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.ReadOnlyField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    division = DivisionSerializer()


class SessionEventSerializer(serializers.Serializer):
    session = SessionSerializer()
    date = serializers.DateField()
    start_time = serializers.TimeField()
    id = serializers.ReadOnlyField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['register_url'] = instance.get_register_url
        rep['unregister_url'] = instance.get_unregister_url

        return rep


class SubSerializer(serializers.Serializer):
    user = CustomUserSerializer()
    session_event = SessionEventSerializer()
