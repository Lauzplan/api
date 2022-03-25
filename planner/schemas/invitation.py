import requests
from planner.models import Invitation
import graphene
from graphene_django import DjangoObjectType, DjangoListField
from django.contrib.gis.db import models


def get_email(info):
    r = requests.get('https://lauzplan.eu.auth0.com/userinfo', headers={'Authorization': info.context.headers['Authorization']})
    return r.json()['email']


class InvitationType(DjangoObjectType):
    class Meta:
        model = Invitation


class AnswerInvitation(graphene.Mutation):
    class Arguments:
        invitation_id = graphene.ID(required=True)
        accept = graphene.Boolean(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, invitation_id, accept):
        invite = Invitation.objects.get(id=invitation_id, email=get_email(info))
        if(accept):
            invite.garden.users.add(info.context.user)

        invite.delete()
        return AnswerInvitation(ok=True)


class AddInvitation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        garden_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, email, garden_id):
        Invitation.objects.create(email=email, garden_id=garden_id)
        return AddInvitation(True)


class Query(graphene.ObjectType):
    invitations = DjangoListField(InvitationType)

    def resolve_invitations(self, info):
        return Invitation.objects.filter(email=get_email(info))


class Mutation(graphene.ObjectType):
    answer_invitation = AnswerInvitation.Field()
    add_invitation = AddInvitation.Field()
