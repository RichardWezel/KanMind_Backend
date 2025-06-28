from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated


class IsAuthenticatedWithCustomMessage(BasePermission):
    """
    Erlaubt Zugriff nur für authentifizierte Benutzer.
    Gibt bei Nichtauthentifizierung eine benutzerdefinierte 401-Meldung zurück.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="Nicht autorisiert. Der Benutzer muss eingeloggt sein.")
        return True

class IsOwnerOrMemberOfBoard(BasePermission):
    """
    Erlaubt Zugriff nur für den Besitzer oder Mitglieder des Boards.
    """

    def has_object_permission(self, request, view, obj):
        # obj ist automatisch das Board-Objekt
        user = request.user


        if user == obj.owner_id or user in obj.members.all():
            return True
        
        raise NotAuthenticated(detail="Verboten. Der Benutzer muss entweder Mitglied des Boards oder der Eigentümer des Boards sein.")
