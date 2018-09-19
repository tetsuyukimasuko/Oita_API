from rest_framework import permissions
from .models import Tenant, ClientInfo, Transaction
 
 #管理者およびインスタンスに紐づくユーザーしかアクセスできない
 #https://richardtier.com/2014/02/25/django-rest-framework-user-endpoint/
class IsAdminOrTargetUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow user to list all users if logged in user is staff
        return view.action == 'retrieve' or request.user.is_staff
 
    def has_object_permission(self, request, view, obj):
        # allow logged in user to view own details, allows staff to view all records
        return request.user.is_staff or obj == request.user

#リストは管理者しか見られないけど、インスタンスはモニターであれば見られる。
class IsAdminOrMonitor(permissions.BasePermission):
    def has_permission(self, request, view):
        return view.action == 'retrieve' or request.user.is_staff
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user.is_monitor

#上記のパーミッションに加え、新規ポストなら許可。
class IsAdminOrMonitorOrPost(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action=="create":
            return True
        return view.action == 'retrieve' or request.user.is_staff
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user.is_monitor