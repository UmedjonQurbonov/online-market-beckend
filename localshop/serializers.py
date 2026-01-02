from rest_framework import serializers
from .models import *

class ShopSerializer(serializers.ModelSerializer):
    owner_info = serializers.SerializerMethodField()


    class Meta:
        model = Shop
        fields = ['id', 'owner','owner_info', 'name', 'description', 'logo', 'rating']
        extra_kwargs = {
            'owner': {'write_only': True},
            'rating': {'read_only': True},
        }

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Название слишком короткое")
        if Shop.objects.filter(name=value).exists():
            raise serializers.ValidationError("Магазин с таким именем уже существует")
        return value


    def validate(self, data):
        if data['owner'] is None:
            raise serializers.ValidationError("Владелец обязателен")
        return data    

    def get_owner_info(self, obj):
        return {
            'id': obj.owner.id,
            'username': obj.owner.username,
            'email': obj.owner.email
        } 

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Название слишком короткое")
        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError("Категория с таким именем уже существует")
        return value
    
class ProductImageSerializer(serializers.ModelSerializer):
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['product', 'image', 'product_info']

    def get_product_info(self, obj):
        return {
            'id': obj.product.id,
            'title': obj.product.title,
            'price': obj.product.price,
            'stock': obj.product.stock,
            'description': obj.product.description,
        }    

class ProductSerializer(serializers.ModelSerializer):
    shop_info = serializers.SerializerMethodField()
    category_info = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'shop', 'shop_info', 'category', 'category_info', 'title', 'article', 'description', 'price', 'stock', 'is_active', 'images']
        extra_kwargs = {
            'is_active': {'read_only': True},
        }

    def validate_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Название слишком короткое")
        return value      

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Цена не должна быть отрицательной')
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Количество на складе не может быть отрицательным')
        return value
    
    def get_shop_info(self, obj):
        return {
            'id': obj.shop.id,
            'name': obj.shop.name,
            'logo': obj.shop.logo.url if obj.shop.logo else None,
            'rating': obj.shop.rating
        } 
    
    def get_category_info(self, obj):
        return {
            'id': obj.category.id,
            'name': obj.category.name,
            'description': obj.category.description,
        } 


class CartSerializer(serializers.ModelSerializer):
    buyer_info = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'buyer', 'buyer_info']

    def get_buyer_info(self, obj):
        return {
            'id': obj.buyer.id,
            'first_name': obj.buyer.first_name,
            'last_name': obj.buyer.last_name,
            'email': obj.buyer.email,
        }

class CartItemSerializator(serializers.ModelSerializer):
    cart_info = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'cart_info','product', 'product_info', 'quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество товара должно быть хотя бы 1")
        return value

    def validate(self, data):
        if data['quantity'] > data['product'].stock:
            raise serializers.ValidationError("На складе нет такого количества товара")
        return data

    def get_cart_info(self, obj):
        return {
            'id': obj.cart.id,
            'buyer': {
            'id': obj.cart.buyer.id,
            'first_name': obj.cart.buyer.first_name,
            'last_name': obj.cart.buyer.last_name,
            'email': obj.cart.buyer.email,
        }
        }    
    
    def get_product_info(self, obj):
        return {
            'id': obj.product.id,
            'title': obj.product.title,
            'price': obj.product.price,
            'stock': obj.product.stock,
            'description': obj.product.description,
        }   

class OrderSerializer(serializers.ModelSerializer):
    buyer_info = serializers.SerializerMethodField()
    cart_info = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'cart', 'cart_info', 'buyer', 'buyer_info', 'status', 'total_price', 'created_at']
        extra_kwargs = {
            'total_price': {'read_only': True},
        }

    def validate_status(self, value):
        allowed_statuses = [choice[0] for choice in Order.STATUS_CHOISE]
        if value not in allowed_statuses:
            raise serializers.ValidationError("Недопустимый статус заказа")
        return value

    def validate(self, data):
        cart = data.get('cart')
        buyer = data.get('buyer')

        if cart.buyer != buyer:
            raise serializers.ValidationError("Покупатель не совпадает с владельцем корзины")
        if not cart.items.exists():
            raise serializers.ValidationError("Невозможно создать заказ с пустой корзиной")
        return data


    def get_buyer_info(self, obj):
        return {
            'id': obj.buyer.id,
            'first_name': obj.buyer.first_name,
            'last_name': obj.buyer.last_name,
            'email': obj.buyer.email,
        }

    def get_cart_info(self, obj):
        return {
            'id': obj.cart.id,
            'items': [
                {
                    'product_id': item.product.id,
                    'title': item.product.title,
                    'quantity': item.quantity,
                    'price': item.product.price,
                    'subtotal': item.quantity * item.product.price
                } for item in obj.cart.items.all()
            ]
        }

    def create(self, validated_data):
        cart = validated_data['cart']
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())
        validated_data['total_price'] = total_price
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['status_display'] = instance.get_status_display()
        return rep


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_info', 'price_at_purchase', 'quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество товара должно быть хотя бы 1")
        return value

    def validate_price_at_purchase(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        return value

    def get_product_info(self, obj):
        return {
            'id': obj.product.id,
            'title': obj.product.title,
            'description': obj.product.description,
            'price_current': obj.product.price,
            'stock': obj.product.stock,
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['subtotal'] = instance.price_at_purchase * instance.quantity
        return rep
    

class ReviewSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'author', 'author_info', 'product', 'product_info', 'rating', 'text', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5")
        return value

    def validate_text(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Текст отзыва слишком короткий")
        return value

    def get_author_info(self, obj):
        return {
            'id': obj.author.id,
            'first_name': obj.author.first_name,
            'last_name': obj.author.last_name,
            'email': obj.author.email,
        }

    def get_product_info(self, obj):
        return {
            'id': obj.product.id,
            'title': obj.product.title,
            'price': obj.product.price,
            'stock': obj.product.stock,
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['created_at_formatted'] = instance.created_at.strftime("%Y-%m-%d %H:%M")
        return rep 
