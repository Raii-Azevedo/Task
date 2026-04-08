from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("tasks/", views.task_board, name="task_board"),
    path("tasks/<int:pk>/", views.task_detail, name="task_detail"),
    path("tasks/<int:pk>/delete/", views.delete_task, name="delete_task"),
    path("events/", views.event_list, name="event_list"),
    path("knowledge/whitepapers/", views.whitepaper_list, name="whitepaper_list"),
    path("knowledge/whitepapers/<int:pk>/", views.whitepaper_detail, name="whitepaper_detail"),
    path("knowledge/whitepapers/<int:pk>/delete/", views.delete_whitepaper, name="delete_whitepaper"),
    path("knowledge/glossary/", views.glossary_list, name="glossary_list"),
    path("knowledge/case-studies/", views.case_study_list, name="case_study_list"),
    path("companies/", views.company_list, name="company_list"),
    path("advisors/", views.advisor_list, name="advisor_list"),
]