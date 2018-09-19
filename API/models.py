from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
import uuid as uuid_lib

#修正版UserManager

class MyUserManager(UserManager):
    def _create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)

        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        return self._create_user(username, password, **extra_fields)

#テナントテーブル
#ユーザー登録よりまず先にテナント登録を行う。
class Tenant(models.Model):
    tenant_name=models.CharField(max_length=32,verbose_name=_('テナント名')) #テナント名
    billing_id=models.UUIDField(default=uuid_lib.uuid4,editable=False,primary_key=True,verbose_name=_('テナントID')) #請求先ID。主キー
    email=models.EmailField(_('email address'), blank=False)

    def __str__(self):
        return self.tenant_name

    class Meta:
        verbose_name = _('テナント情報')
        verbose_name_plural = _('テナント情報')


#営業情報テーブル
class ClientInfo(models.Model):
    client_id=models.UUIDField(default=uuid_lib.uuid4,editable=False,primary_key=True,verbose_name=_('お客様ID'))
    client_name=models.CharField(max_length=32,verbose_name=_('お客様名'))
    license_num=models.IntegerField(verbose_name=_('購入ライセンス数'))
    service_start_date=models.DateTimeField(verbose_name=_('契約開始日'))
    service_expire_date=models.DateTimeField(verbose_name=_('次回契約更新タイミング'))

    def __str__(self):
        return self.client_name

    class Meta:
        verbose_name = _('お客様情報')
        verbose_name_plural = _('お客様情報')

#アカウントテーブル
#AbstractBaseUserを改造する
class User(AbstractBaseUser, PermissionsMixin):

    #username_validator = UnicodeUsernameValidator()

    #ユーザーID
    username=models.CharField(
        _('ユーザーID'),
        max_length=32,
        unique=True,
        primary_key=True,
        help_text=_(
            'Required. 32 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that user id already exists."),
        },
        )

    #メールアドレス
    #djangoのUser仕様上必ず必要になる。管理サイトでいじれないようにすればいいか。
    email = models.EmailField(_('email address'), blank=True,unique=False)

    #閲覧者権限
    #累積使用量を確認できるか否か。お客様の中で、アカウントを取りまとめる人に付与する。
    is_monitor=models.BooleanField(
        _('トランザクション閲覧権限'),
        default=False,
        help_text=_(
            'トランザクションを参照できるかどうかを指定します。'),
    )

    #アカウントが有効か否か
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    #請求先
    #テナントへのForeignkey
    billing_target=models.ForeignKey(Tenant, on_delete=models.CASCADE,verbose_name=_('請求先テナント'),null=True, blank=True)

    #クライアント
    client=models.ForeignKey(ClientInfo, on_delete=models.CASCADE,verbose_name=_('お客様名'),null=True, blank=True)

    #ワトソンID。ハイフン込み
    watson_id=models.CharField(max_length=36,verbose_name=_('WatsonユーザーID'))

    #ワトソンpassword
    watson_pass=models.CharField(max_length=12,verbose_name=_('Watsonパスワード'))

    #ログインステータス
    login_status=models.BooleanField(default=False,verbose_name=_('ログインステータス'))

    #管理者権限
    is_superuser=models.BooleanField(default=False,verbose_name=_('管理者権限'))

    #is_staff
    is_staff=models.BooleanField(default=False,verbose_name=_('スタッフ権限'))

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    EMAIL_FIELD='email'

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')




#トランザクションテーブル
class Transaction(models.Model):
    #トランザクションID
    transaction_id=models.UUIDField(default=uuid_lib.uuid4,editable=False,primary_key=True,verbose_name=_('トランザクションID'))
    #ワトソンID
    watson_id=models.CharField(max_length=36,verbose_name=_('WatsonユーザーID'))
    #変換日時
    requested_time=models.DateTimeField(_('変換日時'), default=timezone.now)
    #秒数
    recognized_seconds=models.FloatField(_('変換秒数'))
    #辞書を使用したか否か
    dict_used=models.BooleanField(_('辞書'),default=False,blank=True)

    def __str__(self):
        return str(self.transaction_id)

    class Meta:
        verbose_name = _('トランザクション')
        verbose_name_plural = _('トランザクション')
