from django.urls import reverse
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from main.models import Team, CustomUser, TeamInvite
from api.serializers import TeamInviteSerializer, TeamSerializer

# for type hints
from rest_framework.request import Request


class UserListView(ListCreateAPIView):
    queryset = CustomUser.objects.all()
    parser_classes = (JSONParser,)

    def list(self, request: Request, *args, **kwargs):
        queryset = self.get_queryset()
        data = [user.as_json() for user in queryset]
        return Response(data)


class TeamCreateView(CreateAPIView):
    parser_classes = (JSONParser,)

    def post(self, request: Request, *args, **kwargs):
        team = Team.objects.create(name=request.data['teamName'], team_captain=request.user)
        players = self.create_players(request.data['players'])
        team.players.add(*players)
        team.add_unregistered_players(request.data['unregisteredPlayers'])
        self.create_invites(team, players)

        # A hack for getting the absolute url, using the request object
        url = request.build_absolute_uri(reverse('home'))

        serializer = TeamSerializer(team)
        serializer.data['redirectURL'] = url
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create_players(self, players):
        return [CustomUser.objects.get(id=p.get('id')) for p in players]

    def create_invites(self, team, players):
        for player in players:
            TeamInvite.objects.create(invitee=player, team=team)

class TeamInviteListView(ListCreateAPIView):
    serializer_class = TeamInviteSerializer

    def get_queryset(self):
        return TeamInvite.objects.filter(invitee=self.request.user)