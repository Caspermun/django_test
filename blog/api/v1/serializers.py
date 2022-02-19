from blog.models import Ad
from rest_framework import serializers


class AdSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ('id', 'title', 'user', 'user_name', 'price', 'discount', 'description', 'image', 'created_at', 'moderated',
                  'is_active')

    def get_price(self, obj):
        return obj.get_price

    def get_user_name(self, obj):
        return obj.user.username

    def create(self, validated_data):
        moderated = validated_data.pop('moderated')
        instance = Ad.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        if validated_data.get('price') > 0:
            instance.price = validated_data.get('price')
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({"error": 'price is not valid'})
