import json
from rest_framework import serializers
from main.models import Team, TeamInvite, CustomUser, NonUserPlayer


def must_have_id(data):
    if 'id' not in data:
        raise serializers.ValidationError({
            'id': 'This field is required',
        })


class CustomUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)


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