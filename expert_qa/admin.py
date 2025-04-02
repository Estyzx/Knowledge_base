from django.contrib import admin

from expert_qa.models import ExpertProfile,Question,Answer

# Register your models here.
admin.site.register(ExpertProfile)
admin.site.register(Question)
admin.site.register(Answer)