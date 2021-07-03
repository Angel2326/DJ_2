from django.conf import settings
from django.db import models

from mainapp.models import Product


class Order(models.Model):
    FORMING = 'FM'
    SENT_TO_PROCEED = 'STP'
    PROCEEDED = 'PRD'
    PAID = 'PD'
    READY = 'RD'
    CANCEL = 'CNC'
    DELIVERED = 'DVD'

    STATUSES = (
        (FORMING, 'ФОРМИРУТЕСЯ'),
        (SENT_TO_PROCEED, 'ОТПРАВЛЕН В ОБРАБОТКУ'),
        (PROCEEDED, 'ОБРАБОТАН'),
        (PAID, 'ОПЛАЧЕН'),
        (READY, 'ГОТОВ К ВЫДАЧЕ'),
        (CANCEL, 'ОТМЕНЕ'),
        (DELIVERED, 'ВЫДАН')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name='создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='обновлен')
    is_active = models.BooleanField(default=True, verbose_name='активен')

    status = models.CharField(choices=STATUSES, default=FORMING, verbose_name='статус', max_length=3)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def get_total_quantity(self):
        _items = self.orderitems.select_related()
        _totalquantity = sum(list(map(lambda x: x.quantity, _items)))
        return _totalquantity

    def get_total_cost(self):
        _items = self.orderitems.select_related()
        _totalcost = sum(list(map(lambda x: x.get_product_cost(), _items)))
        return _totalcost

    def delete(self):
        for item in self.orderitems.select_related():
            item.product.quantity += item.quantity
            item.product.save()
        self.is_active = False
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='orderitems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name='продукт')
    quantity = models.PositiveSmallIntegerField(default=0,
                                                verbose_name='количество')

    def get_product_cost(self):
        return self.product.price * self.quantity

# Create your models here.
