from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
	CaseStudyForm,
	EventForm,
	GlossaryTermForm,
	SeniorAdvisorForm,
	TargetCompanyForm,
	TaskCommentForm,
	TaskForm,
	WhitepaperCommentForm,
	WhitepaperForm,
)
from .models import CaseStudy, Event, GlossaryTerm, SeniorAdvisor, TargetCompany, Task, Whitepaper


def _percent(count, total):
	return round((count / total) * 100, 1) if total else 0


def dashboard(request):
	tasks = Task.objects.all()
	events = Event.objects.all()
	companies = TargetCompany.objects.all()
	advisors = SeniorAdvisor.objects.all()
	whitepapers = Whitepaper.objects.all()[:4]
	today = timezone.localdate()

	total_tasks = tasks.count()
	completed_tasks = tasks.filter(status=Task.Status.DONE).count()
	in_progress_tasks = tasks.filter(status=Task.Status.IN_PROGRESS).count()
	delayed_tasks = [task for task in tasks if task.is_delayed]

	status_breakdown = []
	for status, label in Task.Status.choices:
		count = tasks.filter(status=status).count()
		status_breakdown.append({"label": label, "count": count, "percent": _percent(count, total_tasks)})

	category_totals = {}
	for category, _label in Task.Category.choices:
		count = tasks.filter(category=category).count()
		if count:
			category_totals[category.replace("_", " ").title()] = count
	category_breakdown = [
		{"label": label, "count": count, "percent": _percent(count, total_tasks)}
		for label, count in category_totals.items()
	]

	upcoming_deadlines = [task for task in tasks if task.status != Task.Status.DONE and task.due_date]
	upcoming_deadlines.sort(key=lambda item: item.due_date)

	upcoming_events = events.filter(start_date__gte=today).order_by("start_date")[:5]

	context = {
		"metrics": {
			"total": total_tasks,
			"completed": completed_tasks,
			"in_progress": in_progress_tasks,
			"productivity_rate": _percent(completed_tasks, total_tasks),
			"delayed": len(delayed_tasks),
			"events": events.count(),
			"companies": companies.count(),
			"advisors": advisors.count(),
		},
		"status_breakdown": status_breakdown,
		"category_breakdown": category_breakdown,
		"upcoming_deadlines": upcoming_deadlines[:8],
		"upcoming_events": upcoming_events,
		"recent_whitepapers": whitepapers,
	}
	return render(request, "operations/dashboard.html", context)


def task_board(request):
	create_form = TaskForm(prefix="create")
	if request.method == "POST" and "create_task" in request.POST:
		create_form = TaskForm(request.POST, prefix="create")
		if create_form.is_valid():
			create_form.save()
			messages.success(request, "Iniciativa criada com sucesso.")
			return redirect("task_board")

	query = request.GET.get("q", "").strip()
	tasks = Task.objects.all()
	if query:
		tasks = tasks.filter(
			Q(title__icontains=query)
			| Q(description__icontains=query)
			| Q(owner_name__icontains=query)
			| Q(tags__icontains=query)
		)

	context = {
		"create_form": create_form,
		"query": query,
		"todo_tasks": tasks.filter(status=Task.Status.TODO),
		"in_progress_tasks": tasks.filter(status=Task.Status.IN_PROGRESS),
		"done_tasks": tasks.filter(status=Task.Status.DONE),
	}
	return render(request, "operations/task_board.html", context)


def task_detail(request, pk):
	task = get_object_or_404(Task, pk=pk)
	form = TaskForm(instance=task, prefix="edit")
	comment_form = TaskCommentForm(prefix="comment")

	if request.method == "POST":
		if "update_task" in request.POST:
			form = TaskForm(request.POST, instance=task, prefix="edit")
			if form.is_valid():
				form.save()
				messages.success(request, "Tarefa atualizada.")
				return redirect("task_detail", pk=task.pk)

		if "add_comment" in request.POST:
			comment_form = TaskCommentForm(request.POST, prefix="comment")
			if comment_form.is_valid():
				comment = comment_form.save(commit=False)
				comment.task = task
				comment.save()
				messages.success(request, "Comentario adicionado.")
				return redirect("task_detail", pk=task.pk)

		if "set_status" in request.POST:
			new_status = request.POST.get("status")
			if new_status in dict(Task.Status.choices):
				task.status = new_status
				if new_status == Task.Status.IN_PROGRESS and not task.start_date:
					task.start_date = timezone.localdate()
				if new_status == Task.Status.DONE and not task.completed_date:
					task.completed_date = timezone.localdate()
					task.progress = 100
				task.save(update_fields=["status", "start_date", "completed_date", "progress", "updated_at"])
				messages.success(request, "Status atualizado.")
				return redirect("task_detail", pk=task.pk)

	context = {
		"task": task,
		"form": form,
		"comment_form": comment_form,
		"status_choices": Task.Status.choices,
	}
	return render(request, "operations/task_detail.html", context)


def delete_task(request, pk):
	task = get_object_or_404(Task, pk=pk)
	if request.method == "POST":
		task.delete()
		messages.success(request, "Tarefa excluida.")
	return redirect("task_board")


def event_list(request):
	form = EventForm(prefix="event")
	if request.method == "POST":
		form = EventForm(request.POST, prefix="event")
		if form.is_valid():
			form.save()
			messages.success(request, "Evento cadastrado.")
			return redirect("event_list")

	query = request.GET.get("q", "").strip()
	events = Event.objects.all()
	if query:
		events = events.filter(
			Q(name__icontains=query)
			| Q(description__icontains=query)
			| Q(event_type__icontains=query)
			| Q(location__icontains=query)
		)

	return render(request, "operations/events.html", {"form": form, "events": events, "query": query})


def whitepaper_list(request):
	form = WhitepaperForm(prefix="whitepaper")
	if request.method == "POST" and "create_whitepaper" in request.POST:
		form = WhitepaperForm(request.POST, prefix="whitepaper")
		if form.is_valid():
			form.save()
			messages.success(request, "Whitepaper criado.")
			return redirect("whitepaper_list")

	query = request.GET.get("q", "").strip()
	status_filter = request.GET.get("status", "")
	whitepapers = Whitepaper.objects.all()
	if query:
		whitepapers = whitepapers.filter(
			Q(title__icontains=query)
			| Q(topic__icontains=query)
			| Q(author_name__icontains=query)
		)
	if status_filter:
		whitepapers = whitepapers.filter(status=status_filter)

	context = {
		"form": form,
		"whitepapers": whitepapers,
		"query": query,
		"status_filter": status_filter,
		"status_choices": Whitepaper.Status.choices,
	}
	return render(request, "operations/whitepapers.html", context)


def whitepaper_detail(request, pk):
	whitepaper = get_object_or_404(Whitepaper, pk=pk)
	form = WhitepaperForm(instance=whitepaper, prefix="edit")
	comment_form = WhitepaperCommentForm(prefix="comment")

	if request.method == "POST":
		if "update_whitepaper" in request.POST:
			form = WhitepaperForm(request.POST, instance=whitepaper, prefix="edit")
			if form.is_valid():
				form.save()
				messages.success(request, "Whitepaper atualizado.")
				return redirect("whitepaper_detail", pk=whitepaper.pk)

		if "add_comment" in request.POST:
			comment_form = WhitepaperCommentForm(request.POST, prefix="comment")
			if comment_form.is_valid():
				comment = comment_form.save(commit=False)
				comment.whitepaper = whitepaper
				comment.save()
				messages.success(request, "Comentario adicionado.")
				return redirect("whitepaper_detail", pk=whitepaper.pk)

	context = {
		"whitepaper": whitepaper,
		"form": form,
		"comment_form": comment_form,
	}
	return render(request, "operations/whitepaper_detail.html", context)


def delete_whitepaper(request, pk):
	whitepaper = get_object_or_404(Whitepaper, pk=pk)
	if request.method == "POST":
		whitepaper.delete()
		messages.success(request, "Whitepaper excluido.")
	return redirect("whitepaper_list")


def glossary_list(request):
	form = GlossaryTermForm(prefix="glossary")
	if request.method == "POST":
		form = GlossaryTermForm(request.POST, prefix="glossary")
		if form.is_valid():
			form.save()
			messages.success(request, "Termo adicionado ao glossario.")
			return redirect("glossary_list")

	query = request.GET.get("q", "").strip()
	terms = GlossaryTerm.objects.all()
	if query:
		terms = terms.filter(
			Q(term__icontains=query)
			| Q(definition__icontains=query)
			| Q(category__icontains=query)
			| Q(example__icontains=query)
		)

	return render(request, "operations/glossary.html", {"form": form, "terms": terms, "query": query})


def case_study_list(request):
	form = CaseStudyForm(prefix="case")
	if request.method == "POST":
		form = CaseStudyForm(request.POST, prefix="case")
		if form.is_valid():
			form.save()
			messages.success(request, "Case study criado.")
			return redirect("case_study_list")

	query = request.GET.get("q", "").strip()
	cases = CaseStudy.objects.filter(type="case_study")
	if query:
		cases = cases.filter(
			Q(title__icontains=query)
			| Q(summary__icontains=query)
			| Q(category__icontains=query)
			| Q(author__icontains=query)
		)

	return render(request, "operations/case_studies.html", {"form": form, "cases": cases, "query": query})


def company_list(request):
	form = TargetCompanyForm(prefix="company")
	if request.method == "POST":
		form = TargetCompanyForm(request.POST, prefix="company")
		if form.is_valid():
			form.save()
			messages.success(request, "Empresa cadastrada.")
			return redirect("company_list")

	query = request.GET.get("q", "").strip()
	companies = TargetCompany.objects.all()
	if query:
		companies = companies.filter(
			Q(name__icontains=query)
			| Q(industry__icontains=query)
			| Q(status__icontains=query)
			| Q(contact_person__icontains=query)
			| Q(notes__icontains=query)
		)

	return render(request, "operations/companies.html", {"form": form, "companies": companies, "query": query})


def advisor_list(request):
	form = SeniorAdvisorForm(prefix="advisor")
	if request.method == "POST":
		form = SeniorAdvisorForm(request.POST, prefix="advisor")
		if form.is_valid():
			form.save()
			messages.success(request, "Advisor cadastrado.")
			return redirect("advisor_list")

	query = request.GET.get("q", "").strip()
	advisors = SeniorAdvisor.objects.all()
	if query:
		advisors = advisors.filter(
			Q(name__icontains=query)
			| Q(expertise__icontains=query)
			| Q(company__icontains=query)
			| Q(notes__icontains=query)
		)

	return render(request, "operations/advisors.html", {"form": form, "advisors": advisors, "query": query})
