from django.core.management.base import BaseCommand

from users.jobs.models import Job


class Command(BaseCommand):
    help = "Approve all jobs currently stuck in PENDING status."

    def handle(self, *args, **options):
        pending_jobs = Job.objects.filter(status=Job.STATUS_PENDING)
        count = pending_jobs.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No pending jobs found. Nothing to do."))
            return

        updated = pending_jobs.update(status=Job.STATUS_APPROVED)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully approved {updated} job(s) (was PENDING, now APPROVED).")
        )
