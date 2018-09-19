from rest_framework import serializers
from .models import Tenant, User, ClientInfo, Transaction

#ユーザー情報のシリアライザー
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('username','billing_target','watson_id','watson_pass','login_status')
        write_only_fields = ('password',)
        read_only_fields = ('is_superuser', 'is_monitor','is_active')

    def create(self, validated_data):
        user = super(AccountSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

#テナント情報のシリアライザー
class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model=Tenant
        fields="__all__"

#営業情報のシリアライザー
class ClientInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model=ClientInfo
        fields="__all__"

#トランザクションのシリアライザー
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Transaction
        fields="__all__"