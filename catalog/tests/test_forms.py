import datetime

from django.test import TestCase

from catalog.forms import RenewBookForm
from catalog.models import Author, Book, BookInstance


class RenewBookFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(first_name="Form", last_name="Author")
        book = Book.objects.create(
            title="Form Test Book",
            author=author,
            summary="Summary",
            isbn="3333333333333",
        )
        cls.book_instance = BookInstance.objects.create(
            book=book,
            imprint="Test Imprint",
            status="o",
        )

    def test_renew_form_date_field_label(self):
        form = RenewBookForm(instance=self.book_instance)
        self.assertEqual(form.fields["due_back"].label, "New renewal date")

    def test_renew_form_date_help_text(self):
        form = RenewBookForm(instance=self.book_instance)
        self.assertIn("4 weeks", form.fields["due_back"].help_text)

    def test_renew_form_date_in_past_is_invalid(self):
        past_date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookForm(
            data={"due_back": past_date},
            instance=self.book_instance,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("due_back", form.errors)

    def test_renew_form_date_too_far_is_invalid(self):
        far_date = datetime.date.today() + datetime.timedelta(weeks=5)
        form = RenewBookForm(
            data={"due_back": far_date},
            instance=self.book_instance,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("due_back", form.errors)

    def test_renew_form_date_today_is_valid(self):
        today = datetime.date.today()
        form = RenewBookForm(
            data={"due_back": today},
            instance=self.book_instance,
        )
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max_boundary_is_valid(self):
        max_date = datetime.date.today() + datetime.timedelta(weeks=4)
        form = RenewBookForm(
            data={"due_back": max_date},
            instance=self.book_instance,
        )
        self.assertTrue(form.is_valid())

    def test_renew_form_date_in_range_is_valid(self):
        valid_date = datetime.date.today() + datetime.timedelta(weeks=2)
        form = RenewBookForm(
            data={"due_back": valid_date},
            instance=self.book_instance,
        )
        self.assertTrue(form.is_valid())
