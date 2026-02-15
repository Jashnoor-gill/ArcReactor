from django.core.management.base import BaseCommand
from main_app.models import AcademicEvent, Session
from datetime import date

class Command(BaseCommand):
    help = 'Seeds academic calendar with February 2026 events'

    def handle(self, *args, **options):
        # Clear existing February 2026 events
        AcademicEvent.objects.filter(
            start_date__year=2026,
            start_date__month=2
        ).delete()

        # Get or create a session (optional - can be None)
        session = Session.objects.first()

        events = [
            {
                'title': 'Campus Safety Drill',
                'event_type': 'event',
                'start_date': date(2026, 2, 1),
                'description': 'Mandatory safety drill for all departments with evacuation briefing.',
                'venue': 'Central Quad',
            },
            {
                'title': 'Winter Break Ends',
                'event_type': 'semester_start',
                'start_date': date(2026, 2, 2),
                'description': 'Classes resume after winter break. Students return to campus.',
                'venue': 'Campus Wide',
            },
            {
                'title': 'Library Orientation Week',
                'event_type': 'event',
                'start_date': date(2026, 2, 4),
                'end_date': date(2026, 2, 7),
                'description': 'Workshops on digital resources, research databases, and citation tools.',
                'venue': 'Main Library',
            },
            {
                'title': 'Mid-Term Examination Period Begins',
                'event_type': 'exam',
                'start_date': date(2026, 2, 9),
                'end_date': date(2026, 2, 14),
                'description': 'Mid-term exams for all courses. Check your individual exam schedule.',
                'venue': 'Various Exam Halls',
            },
            {
                'title': 'Republic Day Celebration',
                'event_type': 'event',
                'start_date': date(2026, 2, 11),
                'description': 'Special assembly and cultural program to celebrate Republic Day.',
                'venue': 'Main Auditorium',
            },
            {
                'title': 'Department Council Elections',
                'event_type': 'event',
                'start_date': date(2026, 2, 12),
                'description': 'Student council elections across all departments.',
                'venue': 'Department Blocks',
            },
            {
                'title': 'Research Paper Submission Deadline',
                'event_type': 'deadline',
                'start_date': date(2026, 2, 15),
                'description': 'Final deadline for semester research paper submissions.',
            },
            {
                'title': 'Innovation Lab Open House',
                'event_type': 'event',
                'start_date': date(2026, 2, 16),
                'description': 'Hands-on demos and project showcases at the Innovation Lab.',
                'venue': 'Innovation Lab',
            },
            {
                'title': 'Career Fair 2026',
                'event_type': 'event',
                'start_date': date(2026, 2, 18),
                'end_date': date(2026, 2, 19),
                'description': 'Annual career fair with 50+ companies. Bring your resume!',
                'venue': 'Campus Grounds',
            },
            {
                'title': 'Guest Lecture by Dr. Sarah Chen',
                'event_type': 'event',
                'start_date': date(2026, 2, 20),
                'description': 'Special lecture on "AI in Healthcare" by renowned researcher Dr. Sarah Chen.',
                'venue': 'Conference Hall',
            },
            {
                'title': 'Hostel Maintenance Window',
                'event_type': 'other',
                'start_date': date(2026, 2, 22),
                'description': 'Scheduled maintenance for hostel electrical and water systems.',
                'venue': 'Hostel Blocks',
            },
            {
                'title': 'Sports Week Begins',
                'event_type': 'event',
                'start_date': date(2026, 2, 23),
                'end_date': date(2026, 2, 28),
                'description': 'Annual inter-department sports competition. Register with your department.',
                'venue': 'Sports Complex',
            },
            {
                'title': 'Summer Semester Registration Opens',
                'event_type': 'registration',
                'start_date': date(2026, 2, 25),
                'description': 'Online registration portal opens for Summer 2026 semester.',
            },
            {
                'title': 'Faculty Advising Day',
                'event_type': 'event',
                'start_date': date(2026, 2, 26),
                'description': 'One-on-one academic advising sessions for course planning.',
                'venue': 'Faculty Offices',
            },
            {
                'title': 'Project Proposal Deadline',
                'event_type': 'deadline',
                'start_date': date(2026, 2, 27),
                'description': 'Submit final year project proposals to your department heads.',
            },
        ]

        created_count = 0
        for event_data in events:
            event = AcademicEvent.objects.create(
                session=session,
                **event_data
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created: {event.title}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} events for February 2026!')
        )
