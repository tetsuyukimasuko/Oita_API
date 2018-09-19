from rest_framework import routers
from .views import LoginViewSet, UserViewSet, TenantViewSet, ClientInfoViewSet, TransactionViewSet
from .views import AccountListViewSet,MonthlyTransactionViewSet,UserLoginViewSet,UserLogoutViewSet
from django.conf.urls import include, url

router=routers.DefaultRouter()
router.register(r'^auth',LoginViewSet)
router.register(r'^users',UserViewSet)
router.register(r'^users/(?P<user_id>\w{8,32})/login',UserLoginViewSet)
router.register(r'^users/(?P<user_id>\w{8,32})/logout',UserLogoutViewSet)
router.register(r'^tenants',TenantViewSet)
router.register(r'^clients',ClientInfoViewSet)
router.register(r'^clients/(?P<client_id>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/ids',AccountListViewSet)
router.register(r'^transactions',TransactionViewSet)
router.register(r'^transactions/(?P<watson_id>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/monthly',MonthlyTransactionViewSet)