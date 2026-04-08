from django.contrib import admin

from .models import (
	AuthorizedEmail,
	CaseStudy,
	Event,
	GlossaryTerm,
	SeniorAdvisor,
	TargetCompany,
	Task,
	TaskComment,
	Whitepaper,
	WhitepaperComment,
)


@admin.register(AuthorizedEmail)
class AuthorizedEmailAdmin(admin.ModelAdmin):
	list_display = ("email", "is_active", "created_at")
	list_filter = ("is_active",)
	search_fields = ("email", "notes")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ("title", "category", "status", "priority", "owner_name", "due_date")
	list_filter = ("category", "status", "priority")
	search_fields = ("title", "description", "owner_name", "tags")


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
	list_display = ("task", "user_name", "created_at")
	search_fields = ("task__title", "user_name", "text")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ("name", "event_type", "start_date", "location", "status")
	list_filter = ("event_type", "status", "industry")
	search_fields = ("name", "description", "location")


@admin.register(Whitepaper)
class WhitepaperAdmin(admin.ModelAdmin):
	list_display = ("title", "topic", "status", "progress", "author_name", "published_date")
	list_filter = ("status", "topic")
	search_fields = ("title", "topic", "author_name", "tags")


@admin.register(WhitepaperComment)
class WhitepaperCommentAdmin(admin.ModelAdmin):
	list_display = ("whitepaper", "user_name", "created_at")
	search_fields = ("whitepaper__title", "user_name", "text")


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
	list_display = ("term", "category", "created_at")
	list_filter = ("category",)
	search_fields = ("term", "definition", "example")


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
	list_display = ("title", "category", "author", "is_published", "created_at")
	list_filter = ("category", "is_published")
	search_fields = ("title", "summary", "author")


@admin.register(TargetCompany)
class TargetCompanyAdmin(admin.ModelAdmin):
	list_display = ("name", "industry", "status", "contact_person", "potential_value")
	list_filter = ("industry", "status")
	search_fields = ("name", "contact_person", "notes")


@admin.register(SeniorAdvisor)
class SeniorAdvisorAdmin(admin.ModelAdmin):
	list_display = ("name", "company", "status")
	list_filter = ("status",)
	search_fields = ("name", "expertise", "company")
