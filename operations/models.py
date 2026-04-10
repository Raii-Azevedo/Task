from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		abstract = True


class AuthorizedEmail(TimestampedModel):
	email = models.EmailField(unique=True)
	is_active = models.BooleanField(default=True)
	notes = models.CharField(max_length=255, blank=True)

	class Meta:
		ordering = ["email"]
		verbose_name = "Authorized email"
		verbose_name_plural = "Authorized emails"

	def __str__(self):
		return self.email

	def save(self, *args, **kwargs):
		self.email = self.email.strip().lower()
		super().save(*args, **kwargs)


class Task(TimestampedModel):
	class Category(models.TextChoices):
		CHALLENGE = "challenge", "Challenge"
		NEXT_STEP = "next_step", "Next Step"
		TOOL = "tool", "Tool"
		WHITEPAPER = "whitepaper", "Whitepaper"
		INITIATIVE = "initiative", "Initiative"

	class Status(models.TextChoices):
		TODO = "To Do", "To Do"
		IN_PROGRESS = "In Progress", "In Progress"
		DONE = "Done", "Done"

	class Priority(models.TextChoices):
		HIGH = "Alta", "Alta"
		MEDIUM = "Média", "Média"
		LOW = "Baixa", "Baixa"

	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	category = models.CharField(max_length=100, choices=Category.choices, default=Category.INITIATIVE)
	subcategory = models.CharField(max_length=100, blank=True)
	status = models.CharField(max_length=50, choices=Status.choices, default=Status.TODO)
	priority = models.CharField(max_length=50, choices=Priority.choices, default=Priority.MEDIUM)
	progress = models.PositiveIntegerField(default=0)
	owner_name = models.CharField(max_length=255, blank=True)
	created_date = models.DateField(default=timezone.localdate)
	due_date = models.DateField(null=True, blank=True)
	start_date = models.DateField(null=True, blank=True)
	completed_date = models.DateField(null=True, blank=True)
	estimated_hours = models.FloatField(null=True, blank=True)
	actual_hours = models.FloatField(null=True, blank=True)
	related_initiative = models.CharField(max_length=255, blank=True)
	document_link = models.URLField(blank=True)
	notion_link = models.URLField(blank=True)
	tags = models.CharField(max_length=255, blank=True)
	notes = models.TextField(blank=True)
	target_companies = models.TextField(blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "tasks"
		ordering = ["due_date", "created_at"]

	def __str__(self):
		return self.title

	@property
	def days_left(self):
		if not self.due_date:
			return None
		return (self.due_date - timezone.localdate()).days

	@property
	def is_delayed(self):
		return self.days_left is not None and self.days_left < 0 and self.status != self.Status.DONE

	@property
	def tag_list(self):
		return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


class TaskComment(TimestampedModel):
	task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
	user_name = models.CharField(max_length=255, default="Usuário")
	text = models.TextField()

	class Meta:
		db_table = "task_comments"
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user_name}: {self.task.title}"


class Event(TimestampedModel):
	class EventType(models.TextChoices):
		CONFERENCE = "conference", "Conference"
		WEBINAR = "webinar", "Webinar"
		WORKSHOP = "workshop", "Workshop"

	name = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	event_type = models.CharField(max_length=100, choices=EventType.choices, blank=True)
	industry = models.CharField(max_length=100, blank=True)
	start_date = models.DateField(null=True, blank=True)
	end_date = models.DateField(null=True, blank=True)
	location = models.CharField(max_length=255, blank=True)
	is_virtual = models.BooleanField(default=False)
	event_link = models.URLField(blank=True)
	participants = models.TextField(blank=True)
	notes = models.TextField(blank=True)
	status = models.CharField(max_length=50, default="upcoming")

	class Meta:
		db_table = "events"
		ordering = ["start_date", "name"]

	def __str__(self):
		return self.name


class Whitepaper(TimestampedModel):
	class Status(models.TextChoices):
		DRAFT = "draft", "Draft"
		REVIEW = "review", "Review"
		PUBLISHED = "published", "Published"

	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	topic = models.CharField(max_length=255, blank=True)
	status = models.CharField(max_length=50, choices=Status.choices, default=Status.DRAFT)
	progress = models.PositiveIntegerField(default=0)
	author_name = models.CharField(max_length=255, blank=True)
	content = models.TextField(blank=True)
	document_link = models.URLField(blank=True)
	published_date = models.DateField(null=True, blank=True)
	target_audience = models.TextField(blank=True)
	tags = models.CharField(max_length=255, blank=True)

	class Meta:
		db_table = "whitepapers"
		ordering = ["-created_at"]

	def __str__(self):
		return self.title

	@property
	def tag_list(self):
		return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


class WhitepaperComment(TimestampedModel):
	whitepaper = models.ForeignKey(Whitepaper, on_delete=models.CASCADE, related_name="comments")
	user_name = models.CharField(max_length=255, default="Usuário")
	text = models.TextField()

	class Meta:
		db_table = "whitepaper_comments"
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user_name}: {self.whitepaper.title}"


class Deck(TimestampedModel):
	class Category(models.TextChoices):
		PITCH = "pitch", "Pitch"
		PROPOSAL = "proposal", "Proposal"
		REPORT = "report", "Report"
		REFERENCE = "reference", "Reference"
		OTHER = "other", "Other"

	name = models.CharField(max_length=255)
	document_link = models.URLField()
	category = models.CharField(max_length=100, choices=Category.choices, default=Category.PITCH)
	source_name = models.CharField(max_length=255, blank=True)
	tags = models.CharField(max_length=255, blank=True)
	notes = models.TextField(blank=True)

	class Meta:
		db_table = "decks"
		ordering = ["name"]

	def __str__(self):
		return self.name


class GlossaryTerm(TimestampedModel):
	class Category(models.TextChoices):
		TECHNICAL = "technical", "Technical"
		BUSINESS = "business", "Business"
		ACRONYM = "acronym", "Acronym"

	term = models.CharField(max_length=255, unique=True)
	definition = models.TextField()
	category = models.CharField(max_length=100, choices=Category.choices, blank=True)
	related_terms = models.TextField(blank=True)
	example = models.TextField(blank=True)

	class Meta:
		db_table = "glossary"
		ordering = ["term"]

	def __str__(self):
		return self.term


class CaseStudy(TimestampedModel):
	class Category(models.TextChoices):
		MANUFACTURING = "manufacturing", "Manufacturing"
		SUPPLY_CHAIN = "supply_chain", "Supply Chain"
		DIGITAL_TWIN = "digital_twin", "Digital Twin"
		IA_ML = "ia_ml", "IA / ML"
		HEALTHCARE = "healthcare", "Healthcare"

	title = models.CharField(max_length=255)
	type = models.CharField(max_length=100, default="case_study")
	category = models.CharField(max_length=100, choices=Category.choices)
	content = models.TextField(blank=True)
	summary = models.TextField()
	author = models.CharField(max_length=255, blank=True)
	tags = models.CharField(max_length=255, blank=True)
	document_link = models.URLField(blank=True)
	is_published = models.BooleanField(default=False)
	views = models.PositiveIntegerField(default=0)

	class Meta:
		db_table = "knowledge_base"
		ordering = ["-created_at"]

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		self.type = "case_study"
		super().save(*args, **kwargs)


class TargetCompany(TimestampedModel):
	name = models.CharField(max_length=255)
	industry = models.CharField(max_length=100, blank=True)
	size = models.CharField(max_length=50, blank=True)
	contact_person = models.CharField(max_length=255, blank=True)
	contact_email = models.EmailField(blank=True)
	contact_phone = models.CharField(max_length=50, blank=True)
	potential_value = models.CharField(max_length=255, blank=True)
	notes = models.TextField(blank=True)
	status = models.CharField(max_length=50, default="prospect")
	last_contact = models.DateField(null=True, blank=True)
	next_action = models.TextField(blank=True)

	class Meta:
		db_table = "target_companies"
		ordering = ["name"]

	def __str__(self):
		return self.name


class SeniorAdvisor(TimestampedModel):
	name = models.CharField(max_length=255)
	expertise = models.TextField(blank=True)
	topics = models.TextField(blank=True)
	events_participated = models.TextField(blank=True)
	company = models.CharField(max_length=255, blank=True)
	contact_info = models.TextField(blank=True)
	linkedin = models.URLField(blank=True)
	notes = models.TextField(blank=True)
	status = models.CharField(max_length=50, default="active")

	class Meta:
		db_table = "senior_advisors"
		ordering = ["name"]

	def __str__(self):
		return self.name
