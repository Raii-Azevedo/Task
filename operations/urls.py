from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views


urlpatterns = [
    path("login/", views.CorporateLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", login_required(views.dashboard), name="dashboard"),
    path("tasks/", login_required(views.task_board), name="task_board"),
    path("tasks/<int:pk>/", login_required(views.task_detail), name="task_detail"),
    path("tasks/<int:pk>/delete/", login_required(views.delete_task), name="delete_task"),
    path("events/", login_required(views.event_list), name="event_list"),
    path("knowledge/whitepapers/", login_required(views.whitepaper_list), name="whitepaper_list"),
    path("knowledge/whitepapers/<int:pk>/", login_required(views.whitepaper_detail), name="whitepaper_detail"),
    path("knowledge/whitepapers/<int:pk>/delete/", login_required(views.delete_whitepaper), name="delete_whitepaper"),
    path("knowledge/glossary/", login_required(views.glossary_list), name="glossary_list"),
    path("knowledge/case-studies/", login_required(views.case_study_list), name="case_study_list"),
    path("companies/", login_required(views.company_list), name="company_list"),
    path("advisors/", login_required(views.advisor_list), name="advisor_list"),
]