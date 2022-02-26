from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import AuthenticationFailed, ValidationError

from blog.models import Ad, CustomUser
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']

    def save(self, **kwargs):
        user = CustomUser(username=self.validated_data['username'],
                          email=self.validated_data['email'],
                          )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise ValidationError('passwords mismatch!')

        user.set_password(password2)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class AdSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Ad
        fields = ('id', 'title', 'user_name', 'price', 'discount', 'description', 'image', 'created_at', 'moderated',
                  'is_active')

    def get_price(self, obj):
        return obj.get_price

    def get_user_name(self, obj):
        return obj.user.username

    def create(self, validated_data):
        instance = Ad.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        if validated_data.get('price') > 0:
            instance.price = validated_data.get('price')
            instance.title = validated_data.get('title')
            instance.description = validated_data.get('description')
            instance.image = validated_data.get('image')
            # instance.user = validated_data.get('user')
            # instance.created_at = validated_data.get('created_at')
            instance.moderated = validated_data.get('moderated')
            instance.is_active = validated_data.get('is_active')
            instance.discount = validated_data.get('discount')
            instance.save()

            return instance
        else:
            raise serializers.ValidationError({"error": 'price is not valid'})
