from rest_framework import serializers
from main.models import Team, TeamInvite, CustomUser, NonUserPlayer


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name')


class TeamSerializer(serializers.ModelSerializer):
    players = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)
    team_captain = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    id = serializers.IntegerField()

    class Meta:
        model = Team
        fields = ('id', 'name', 'players', 'team_captain')


class TeamInviteSerializer(serializers.ModelSerializer):
    team = TeamSerializer()
    invitee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = TeamInvite
        fields = ('id', 'status', 'invitee', 'team')

    def create(self, validated_data):
        invitee = validated_data.pop('invitee')
        team_id = validated_data.pop('team').get('id')
        team = Team.objects.get(id=team_id)
        obj, _ = TeamInvite.objects.get_or_create(team=team, invitee=invitee)
        return obj