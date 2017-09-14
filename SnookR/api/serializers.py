from rest_framework import serializers
from main.models import Team, TeamInvite, NonUserPlayer


class TeamSerializer(serializers.ModelSerializer):
    players = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    team_captain = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Team
        fields = '__all__'



class TeamInviteSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    invitee = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TeamInvite
        fields = ('id', 'status', 'invitee', 'team')

    """def create(self, validated_data):
        invitee = validated_data.pop('invitee')
        invitee = CustomUser.objects.get(id=invitee)

        team = validated_data.pop('team')
        team = Team.objects.get(id=team)
        
        return TeamInvite.objects.create(team=team, invitee=invitee, **validated_data)
    """