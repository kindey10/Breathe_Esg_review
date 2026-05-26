from pathlib import Path
from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from accounts.models import Organization, Membership
from ingestion.models import Facility, DataSource, IngestionBatch
from ingestion.parsers import (
    parse_sap_activity_batch,
    parse_utility_electricity_batch,
    parse_travel_activity_batch,
)


class Command(BaseCommand):
    help = "Seed demo organization, analyst, facilities, data sources, and demo uploads"

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
            ("PLT-BLR-01", "Bangalore Facility", "Bangalore"),
            ("PLT-CHE-01", "Chennai Facility", "Chennai"),
            ("PLT-HYD-01", "Hyderabad Facility", "Hyderabad"),
            ("PLT-MUM-01", "Mumbai Plant", "Mumbai"),
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

        sources = {
            "SAP": "SAP S/4HANA Export",
            "UTILITY": "Utility Portal Export",
            "TRAVEL": "Corporate Travel Export",
        }

        source_objects = {}

        for source_type, name in sources.items():
            source, _ = DataSource.objects.get_or_create(
                organization=organization,
                source_type=source_type,
                defaults={"name": name},
            )
            source_objects[source_type] = source


        backend_dir = Path(__file__).resolve().parents[4]
        project_root = backend_dir.parent
        sample_dir = project_root / "sample_data"
        if not sample_dir.exists():
            sample_dir = backend_dir / "sample_data"
        self.stdout.write(f"Looking for sample files in: {sample_dir}")


        demo_files = [
            (
                "SAP_ACTIVITY",
                "sap_activity_data.csv",
                source_objects["SAP"],
                parse_sap_activity_batch,
            ),
            (
                "UTILITY_ELECTRICITY",
                "utility_electricity_data.csv",
                source_objects["UTILITY"],
                parse_utility_electricity_batch,
            ),
            (
                "TRAVEL_ACTIVITY",
                "travel_activity_data.csv",
                source_objects["TRAVEL"],
                parse_travel_activity_batch,
            ),
        ]

        for dataset_type, filename, source, parser in demo_files:
            if IngestionBatch.objects.filter(
                organization=organization,
                dataset_type=dataset_type,
                original_filename=filename,
            ).exists():
                continue

            file_path = sample_dir / filename

            if not file_path.exists():
                self.stdout.write(
                    self.style.WARNING(f"Missing sample file: {file_path}")
                )
                continue

            with open(file_path, "rb") as f:
                batch = IngestionBatch.objects.create(
                    organization=organization,
                    data_source=source,
                    dataset_type=dataset_type,
                    original_file=File(f, name=filename),
                    original_filename=filename,
                    uploaded_by=user,
                    status="PROCESSING",
                )

            parser(batch)

        self.stdout.write(
            self.style.SUCCESS("Demo data and sample uploads created successfully.")
        )