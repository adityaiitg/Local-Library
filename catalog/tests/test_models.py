import datetime
import uuid

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from catalog.models import Author, Book, BookInstance, Genre, Language


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name="Fantasy")

    def test_name_label(self):
        genre = Genre.objects.get(id=1)
        field_label = genre._meta.get_field("name").verbose_name
        self.assertEqual(field_label, "name")

    def test_name_max_length(self):
        genre = Genre.objects.get(id=1)
        max_length = genre._meta.get_field("name").max_length
        self.assertEqual(max_length, 200)

    def test_str(self):
        genre = Genre.objects.get(id=1)
        self.assertEqual(str(genre), "Fantasy")


class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Language.objects.create(name="English")

    def test_str(self):
        language = Language.objects.get(id=1)
        self.assertEqual(str(language), "English")

    def test_name_unique(self):
        field = Language._meta.get_field("name")
        self.assertTrue(field.unique)


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name="John", last_name="Doe")

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        self.assertEqual(
            author._meta.get_field("first_name").verbose_name, "first name"
        )

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        self.assertEqual(
            author._meta.get_field("last_name").verbose_name, "last name"
        )

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        self.assertEqual(author._meta.get_field("date_of_death").verbose_name, "Died")

    def test_str(self):
        author = Author.objects.get(id=1)
        self.assertEqual(str(author), "Doe, John")

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        self.assertEqual(author.get_absolute_url(), f"/catalog/author/{author.id}/")

    def test_ordering(self):
        Author.objects.create(first_name="Alice", last_name="Adams")
        authors = list(Author.objects.all())
        self.assertEqual(authors[0].last_name, "Adams")

    def test_can_mark_returned_permission_exists(self):
        """Verify the can_mark_returned permission is defined."""
        from django.contrib.auth.models import Permission

        # Permission is on BookInstance model
        perm = Permission.objects.filter(codename="can_mark_returned").first()
        self.assertIsNotNone(perm)


class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_author = Author.objects.create(first_name="Jane", last_name="Smith")
        test_genre = Genre.objects.create(name="Science Fiction")
        test_language = Language.objects.create(name="English")
        test_book = Book.objects.create(
            title="Test Book Title",
            author=test_author,
            summary="A test book summary",
            isbn="1234567890123",
            language=test_language,
        )
        test_book.genre.add(test_genre)

    def test_title_label(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book._meta.get_field("title").verbose_name, "title")

    def test_summary_max_length(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book._meta.get_field("summary").max_length, 1000)

    def test_isbn_max_length(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book._meta.get_field("isbn").max_length, 13)

    def test_str(self):
        book = Book.objects.get(id=1)
        self.assertEqual(str(book), "Test Book Title")

    def test_get_absolute_url(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.get_absolute_url(), f"/catalog/book/{book.id}/")

    def test_display_genre(self):
        book = Book.objects.get(id=1)
        self.assertIn("Science Fiction", book.display_genre())


class BookInstanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_author = Author.objects.create(first_name="Jane", last_name="Smith")
        test_book = Book.objects.create(
            title="Test Book",
            author=test_author,
            summary="Summary",
            isbn="9876543210123",
        )
        BookInstance.objects.create(
            book=test_book,
            imprint="Test Imprint",
            status="a",
        )

    def test_str(self):
        instance = BookInstance.objects.first()
        self.assertIn("Test Book", str(instance))

    def test_status_default(self):
        # New instance defaults to maintenance
        author = Author.objects.first()
        book = Book.objects.first()
        new_instance = BookInstance.objects.create(
            book=book,
            imprint="Print 2024",
        )
        self.assertEqual(new_instance.status, "m")

    def test_is_overdue_when_future(self):
        instance = BookInstance.objects.first()
        instance.due_back = datetime.date.today() + datetime.timedelta(days=5)
        self.assertFalse(instance.is_overdue)

    def test_is_overdue_when_past(self):
        instance = BookInstance.objects.first()
        instance.due_back = datetime.date.today() - datetime.timedelta(days=1)
        self.assertTrue(instance.is_overdue)

    def test_is_overdue_when_no_due_date(self):
        instance = BookInstance.objects.first()
        instance.due_back = None
        self.assertFalse(instance.is_overdue)

    def test_ordering(self):
        author = Author.objects.first()
        book = Book.objects.first()
        b1 = BookInstance.objects.create(
            book=book,
            imprint="Imprint A",
            due_back=datetime.date.today() + datetime.timedelta(days=10),
        )
        b2 = BookInstance.objects.create(
            book=book,
            imprint="Imprint B",
            due_back=datetime.date.today() + datetime.timedelta(days=5),
        )
        instances = list(BookInstance.objects.filter(imprint__in=["Imprint A", "Imprint B"]))
        self.assertEqual(instances[0], b2)
