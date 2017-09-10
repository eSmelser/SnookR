from django.urls import reverse
from main.models import Team, CustomUser, TeamInvite
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

# for type hints
from rest_framework.request import Request


class UserListView(ListCreateAPIView):
    queryset = CustomUser.objects.all()
    parser_classes = (JSONParser,)

    def list(self, request: Request, *args, **kwargs):
        queryset = self.get_queryset()
        data = [user.as_json() for user in queryset]
        return Response(data)

    def post(self, request: Request, *args, **kwargs):
        team = Team.objects.create(name=request.data['teamName'], team_captain=request.user)
        players = self.create_players()
        team.players.add(*players)
        team.add_unregistered_players(self.request.data['unregisteredPlayers'])
        self.create_invites(team, players)

        # A hack for getting the absolute url, using the request object
        url = request.build_absolute_uri(reverse('home'))
        return Response({'redirectURL': url}, status=status.HTTP_201_CREATED)

    def create_players(self):
        return [CustomUser.objects.get(id=p.get('id')) for p in self.request.data['players']]

    def create_invites(self, team, players):
        for player in players:
            TeamInvite.objects.create(invitee=player, team=team)
