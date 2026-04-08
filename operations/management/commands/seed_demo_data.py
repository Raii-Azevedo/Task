from django.core.management.base import BaseCommand

from operations.models import CaseStudy, Event, GlossaryTerm, SeniorAdvisor, TargetCompany, Whitepaper


class Command(BaseCommand):
    help = "Seed the database with TaskSync demo content."

    def handle(self, *args, **options):
        glossary_items = [
            {
                "term": "Digital Twin",
                "definition": "Réplica virtual de processos ou produtos.",
                "category": GlossaryTerm.Category.TECHNICAL,
                "example": "Usado em manufatura para simular uma linha produtiva.",
            },
            {
                "term": "Supply Chain",
                "definition": "Rede logística de produção e distribuição.",
                "category": GlossaryTerm.Category.BUSINESS,
                "example": "Planejamento de estoque e transporte com dados em tempo real.",
            },
        ]
        for item in glossary_items:
            GlossaryTerm.objects.get_or_create(term=item["term"], defaults=item)

        Event.objects.get_or_create(
            name="Industry 4.0 Summit",
            defaults={
                "event_type": Event.EventType.CONFERENCE,
                "location": "Sao Paulo",
                "description": "Conferencia focada em operacoes digitais.",
            },
        )

        Whitepaper.objects.get_or_create(
            title="Digital Operations Playbook",
            defaults={
                "topic": "Operations Strategy",
                "author_name": "TaskSync Team",
                "status": Whitepaper.Status.REVIEW,
                "progress": 65,
                "target_audience": "Leads de operacoes e estrategia.",
            },
        )

        CaseStudy.objects.get_or_create(
            title="Predictive Maintenance Rollout",
            defaults={
                "category": CaseStudy.Category.MANUFACTURING,
                "summary": "Reducao de downtime com sensores e analise preditiva.",
                "author": "Operations Lab",
                "is_published": True,
            },
        )

        TargetCompany.objects.get_or_create(
            name="Industrias ABC",
            defaults={
                "industry": "manufacturing",
                "status": "prospect",
                "contact_person": "Joao Silva",
                "notes": "Empresa com alto potencial para piloto de digital twin.",
            },
        )

        SeniorAdvisor.objects.get_or_create(
            name="Maria Santos",
            defaults={
                "expertise": "Supply chain, procurement, transformation",
                "company": "SaudeTech",
                "notes": "Atua como ponte com o ecossistema de healthcare.",
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data loaded."))