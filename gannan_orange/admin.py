from django.contrib import admin
from .models import Variety, PlantingTech, Pest, SoilType, Category


# Register your models here.

class VarietyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'tech_names', 'pest_names')

    def tech_names(self, obj):
        return ", ".join([tech.name for tech in obj.planting_tech.all()])

    def pest_names(self, obj):
        return ", ".join([pest.name for pest in obj.pest.all()])


# 注册模型
admin.site.register(Variety, VarietyAdmin)
admin.site.register(PlantingTech)
admin.site.register(Pest)
admin.site.register(SoilType)
admin.site.register(Category)

