from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from accounts.models import Organization, Membership
from ingestion.models import Facility, DataSource


class Command(BaseCommand):
    help = "Seed demo organization, analyst, facilities, and data sources"

    def handle(self, *args, **kwargs):
        organization, _ = Organization.objects.get_or_create(
            name="Acme Manufacturing India Pvt Ltd"
        )

        user, created = User.objects.get_or_create(
            username="kindey",
            defaults={
                "email": "kindey2004@gmail.com",
                "first_name": "Kinjal",
                "last_name": "Pandey",
            },
        )

        if created:
            user.set_password("Demo@12345")
            user.is_staff = True
            user.is_superuser = True
            user.save()

        Membership.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={"role": "ANALYST"},
        )

        facilities = [
            ("PLT-DEL-01", "Delhi Manufacturing Plant", "Delhi"),
            ("PLT-PUN-01", "Pune Assembly Facility", "Pune"),
        ]

        for code, name, city in facilities:
            Facility.objects.get_or_create(
                organization=organization,
                facility_code=code,
                defaults={
                    "facility_name": name,
                    "city": city,
                },
            )

        data_sources = [
            ("SAP", "SAP S/4HANA Export"),
            ("UTILITY", "Utility Portal Export"),
            ("TRAVEL", "Corporate Travel Platform Snapshot"),
        ]

        for source_type, name in data_sources:
            DataSource.objects.get_or_create(
                organization=organization,
                source_type=source_type,
                defaults={"name": name},
            )

        self.stdout.write(
            self.style.SUCCESS("Demo data created successfully.")
        )