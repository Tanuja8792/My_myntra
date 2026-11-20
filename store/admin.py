from django.contrib import admin
from .models import Category,Brand,Product,Address,Coupon,Order,OrderItem,Review,ReturnRequest,Notification

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=("name","category","brand","price","discount_percent","stock","is_active")
    list_filter=("category","brand","is_active")
    search_fields=("name","description")
    prepopulated_fields={"slug":("name",)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=("order_id","user","status","total","payment_method","created_at")
    list_filter=("status","payment_method","created_at")
    search_fields=("order_id","user__username")
    actions=["mark_shipped","mark_delivered"]
    @admin.action(description="Mark selected orders as shipped")
    def mark_shipped(self,request,queryset): queryset.update(status="shipped")
    @admin.action(description="Mark selected orders as delivered")
    def mark_delivered(self,request,queryset): queryset.update(status="delivered")

admin.site.register([Category,Brand,Address,Coupon,OrderItem,Review,ReturnRequest,Notification])
admin.site.site_header="My Myntra Store Administration"
admin.site.site_title="My Myntra Admin"
admin.site.index_title="Manage your fashion store"
