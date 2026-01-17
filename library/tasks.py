from celery import shared_task
from .models import Loan
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass


@shared_task
def check_overdue_loans():
    try:
        today = timezone.now().date()
        overdue_loans = Loan.objects.filter(
            is_returned = False,
            due_date__lt= today
        )
        notification_sent = 0
        errors = 0

        for loan in overdue_loans:
            try:
                member_email = loan.member.user.email
                book_title = loan.book.title
                days_overdue = (today - loan.due_date)

                send_mail(
                    subject="Overdue Book Reminder",
                    message=f" Hello {loan.member.user.username}, \n\n This is a reminder that your loaned book {book_title} is {days_overdue}s overdue",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[member_email],
                    fail_silently=False,
                )
                notification_sent += 1

            except Exception as e:
                errors += 1

        return{
            'status': "sucess",
            "total_overdue": overdue_loans.count(),
            'Notification_sent': notification_sent,
            "errors": errors
        }
    
    except Exception as e:
        return {"status": "error", 'message': str(e)}