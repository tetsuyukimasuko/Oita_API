from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
import json
from .models import Tenant, User, ClientInfo, Transaction
from .serializers import TenantSerializer, UserSerializer, ClientInfoSerializer, TransactionSerializer
from django.http import HttpResponse, Http404
import requests
from .permissions import IsAdminOrTargetUser, IsAdminOrMonitor, IsAdminOrMonitorOrPost
import datetime


# Create your views here.

#認証
class LoginViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    #認証済みユーザーじゃないとアクセスできない
    permission_classes=(IsAuthenticated,)

    #GETのみ許可
    def list(self, request, *args, **kwargs):
        return Response({"status" : "successfully authenticated."}, status=status.HTTP_200_OK)
    
    #残りは全て禁止
    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'GET' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'DELETE' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'PUT' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'POST' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

#アカウント情報の参照
class UserViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    #管理者か、そのアカウント本人しか参照できない
    def get_permissions(self):
        return (IsAdminOrTargetUser(),)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

#ログインステータスの切り替え
#ログインする
class UserLoginViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    def list(self, request, user_id):
        target=User.objects.get(pk=user_id)
        if request.user==target:
            target.login_status=True
            target.save()
            return Response({"status" : "successfully logged in."}, status=status.HTTP_200_OK)
        else:
            return Response({'detail' : '権限がありません。'},status=status.HTTP_403_FORBIDDEN)
    
    #残りは全て禁止
    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'GET' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'DELETE' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'PUT' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'POST' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

#ログインステータスの切り替え
#ログアウトする
class UserLogoutViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    #GETのみ許可
    def list(self, request, user_id):
        target=User.objects.get(pk=user_id)
        if request.user==target:
            target.login_status=False
            target.save()
            return Response({"status" : "successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({'detail' : '権限がありません。'},status=status.HTTP_403_FORBIDDEN)
    
    #残りは全て禁止
    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'GET' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'DELETE' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'PUT' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'POST' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

#テナント情報の参照
#管理者しか見られない
class TenantViewSet(viewsets.ModelViewSet):
    queryset=Tenant.objects.all()
    serializer_class=TenantSerializer

    #AdminUserのみ操作可能。
    permission_classes=(IsAdminUser,)

#営業情報の参照
#管理者しか見られない
class ClientInfoViewSet(viewsets.ModelViewSet):
    queryset=ClientInfo.objects.all()
    serializer_class=ClientInfoSerializer

    #AdminUserのみ操作可能。
    permission_classes=(IsAdminUser,)

#トランザクションの参照
#管理者は全トランザクションを参照でき、ユーザーは自分のトランザクションを参照できる。
class TransactionViewSet(viewsets.ModelViewSet):
    queryset=Transaction.objects.all()
    serializer_class=TransactionSerializer

    #管理者かretrieve、postのみ許可
    def get_permissions(self):
        return (IsAdminOrMonitorOrPost()),

    #retrieve
    def retrieve(self, request, pk):

        #ここでいうpkはトランザクションIDではなくwatsonIDですよん。
        #watsonIDが同じものをリストとして取り出す。
        try:
            trans=Transaction.objects.filter(watson_id=pk)
        except:
            return Response({'detail' : '変換記録がありません。'},status=status.HTTP_404_NOT_FOUND)

        #指定したwatsonIDを持つuserを持ってきて、そのuserのclientを取得
        us=User.objects.get(watson_id=pk)
        client=us.client

        #ユーザーのwatsonidが自分自身か、またはその人が属する組織のアカウントかつその人がモニターなら
        if request.user.watson_id==pk or (request.user.is_monitor and request.user.client==client)or request.user.is_staff:
            return Response(trans.values(),status=status.HTTP_200_OK) 
        else:
            return Response({'detail' : '権限がありません。'},status=status.HTTP_403_FORBIDDEN)

#同じ組織に属するユーザーの情報を全部もってくる
#フロントでは、このメソッドでユーザーIDを全部持ってきてから、
#各ユーザーIDのトランザクションを参照すればよい。
class AccountListViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    #管理者かretrieveのみ許可。
    def get_permissions(self):
        return (IsAdminOrMonitor()),

    def list(self, request, client_id):
        #指定したクライアントIDのobjをもってくる
        client=ClientInfo.objects.get(pk=client_id)
        user_list=User.objects.filter(client=client)

        #指定したクライアントidが、リクエスト側のクライアントidと一致するか否か
        if(request.user.client==client or request.user.is_staff):
            return Response(user_list.values('username','client','billing_target','watson_id'),status=status.HTTP_200_OK) 
        else:
            return Response({'detail' : '権限がありません。'},status=status.HTTP_403_FORBIDDEN)

#年と月を指定すると、その月に応じた使用量を返す。
#管理者およびモニターのみアクセス可能。
class MonthlyTransactionViewSet(viewsets.ModelViewSet):
    queryset=Transaction.objects.all()
    serializer_class=TransactionSerializer

    #管理者かretrieveのみ許可。
    def get_permissions(self):
        return (IsAdminOrMonitor()),

    def list(self, request, watson_id):
        #watsonIDが同じものをリストとして取り出す。
        try:
            trans=Transaction.objects.filter(watson_id=watson_id)
        except:
            return Response({'detail' : '変換記録がありません。'},status=status.HTTP_404_NOT_FOUND)


        return Response(trans.values(),status=status.HTTP_200_OK)

    def retrieve(self, request, watson_id,pk):

        #ここでいうpkは年月。2018-09みたいになる。
        try:
            year, month=pk.split("-")
            year=int(year)
            month=int(month)
            gte=datetime.datetime(year,month,1,0,0,0)
            start=str(year)+"-"+str(month)
            if month==12:
                month=1
                year+=1
            else:
                month+=1
            lte=datetime.datetime(year,month,1,0,0,0)
            end=str(year)+"-"+str(month)
            tr=Transaction.objects.filter(requested_time__gte=gte, requested_time__lte=lte)
        except:
            return Response({'detail' : '無効なパラメータです。'},status=status.HTTP_404_NOT_FOUND)

        total=0.0
        price=0.0
        dict_used_seconds=0.0
        dict_used_price=0.0

        for t in tr:
            total+=t.recognized_seconds
            if t.dict_used:
                price+=t.recognized_seconds*0.05
                dict_used_seconds+=t.recognized_seconds
                dict_used_price+=t.recognized_seconds*0.05
            else:
                price+=t.recognized_seconds*0.02

        #指定したwatsonIDを持つuserを持ってきて、そのuserのclientを取得
        us=User.objects.get(watson_id=watson_id)
        client=us.client

        #ユーザーのwatsonidが自分自身か、またはその人が属する組織のアカウントかつその人がモニターなら
        if request.user.watson_id==pk or (request.user.is_monitor and request.user.client==client)or request.user.is_staff:
            return Response({"start" : start, "end" : end,
                         "total_transaction_seconds" : total,
                        "total_estimated_price" : price,
                        "dict_used_seconds" : dict_used_seconds,
                        "dict_used_price" : dict_used_price },
                        status=status.HTTP_200_OK)
        else:
            return Response({'detail' : '権限がありません。'},status=status.HTTP_403_FORBIDDEN)
