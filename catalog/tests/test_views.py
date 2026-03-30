import datetime
import uuid

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from catalog.models import Author, Book, BookInstance, Genre, Language


def create_test_user(username="testuser", password="testpassword123"):
    return User.objects.create_user(username=username, password=password)


def create_test_book():
    author = Author.objects.create(first_name="Test", last_name="Author")
    book = Book.objects.create(
        title="Test Book",
        author=author,
        summary="A test summary",
        isbn="1234567890111",
    )
    return book


class IndexViewTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("index"))
        self.assertRedirects(response, "/accounts/login/?next=/catalog/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_session_visit_counter_increments(self):
        self.client.login(username="testuser", password="testpassword123")
        self.client.get(reverse("index"))
        response = self.client.get(reverse("index"))
        self.assertEqual(response.context["num_visits"], 1)


class BookListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="booklistuser", password="testpassword123"
        )
        author = Author.objects.create(first_name="Test", last_name="Author")
        for i in range(13):
            Book.objects.create(
                title=f"Book Title {i:02d}",
                author=author,
                summary="A summary",
                isbn=f"12345678901{i:02d}"[:13],
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("books"))
        self.assertRedirects(response, "/accounts/login/?next=/catalog/books/")

    def test_logged_in_returns_200(self):
        self.client.login(username="booklistuser", password="testpassword123")
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(username="booklistuser", password="testpassword123")
        response = self.client.get(reverse("books"))
        self.assertTemplateUsed(response, "catalog/book_list.html")

    def test_pagination_is_10(self):
        self.client.login(username="booklistuser", password="testpassword123")
        response = self.client.get(reverse("books"))
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(len(response.context["book_list"]), 10)

    def test_second_page_has_remaining_books(self):
        self.client.login(username="booklistuser", password="testpassword123")
        response = self.client.get(reverse("books") + "?page=2")
        self.assertEqual(len(response.context["book_list"]), 3)


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="authorlistuser", password="testpassword123"
        )
        for i in range(5):
            Author.objects.create(first_name=f"First{i}", last_name=f"Last{i}")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("author"))
        self.assertRedirects(response, "/accounts/login/?next=/catalog/authors/")

    def test_returns_200_when_logged_in(self):
        self.client.login(username="authorlistuser", password="testpassword123")
        response = self.client.get(reverse("author"))
        self.assertEqual(response.status_code, 200)


class LoanedBooksByUserListViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="testpassword123"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="testpassword123"
        )
        author = Author.objects.create(first_name="Test", last_name="Author")
        book = Book.objects.create(
            title="My Book", author=author, summary="Summary", isbn="1111111111111"
        )
        # Create 10 instances for user1 (on loan)
        for i in range(10):
            BookInstance.objects.create(
                book=book,
                imprint="Imprint",
                due_back=datetime.date.today() + datetime.timedelta(days=i + 1),
                borrower=self.user1,
                status="o",
            )
        # Create 2 instances for user2
        for i in range(2):
            BookInstance.objects.create(
                book=book,
                imprint="Imprint",
                due_back=datetime.date.today() + datetime.timedelta(days=i + 1),
                borrower=self.user2,
                status="o",
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("my-borrowed"))
        self.assertRedirects(response, "/accounts/login/?next=/catalog/mybooks/")

    def test_only_shows_current_user_loans(self):
        self.client.login(username="user1", password="testpassword123")
        response = self.client.get(reverse("my-borrowed"))
        self.assertEqual(response.status_code, 200)
        # user1 has 10 items — all shown (paginate_by=10)
        self.assertEqual(len(response.context["bookinstance_list"]), 10)

    def test_user2_sees_only_their_books(self):
        self.client.login(username="user2", password="testpassword123")
        response = self.client.get(reverse("my-borrowed"))
        self.assertEqual(len(response.context["bookinstance_list"]), 2)


class RenewBookLibrarianViewTest(TestCase):
    def setUp(self):
        self.librarian = User.objects.create_user(
            username="librarian", password="testpassword123"
        )
        self.regular_user = User.objects.create_user(
            username="regular", password="testpassword123"
        )
        # Assign permission to librarian
        perm = Permission.objects.get(codename="can_mark_returned")
        self.librarian.user_permissions.add(perm)

        author = Author.objects.create(first_name="Test", last_name="Auth")
        book = Book.objects.create(
            title="Renew Book", author=author, summary="Summary", isbn="2222222222222"
        )
        self.book_instance = BookInstance.objects.create(
            book=book,
            imprint="Test",
            due_back=datetime.date.today() + datetime.timedelta(days=5),
            borrower=self.regular_user,
            status="o",
        )

    def test_redirect_if_not_logged_in(self):
        url = reverse("renew-book-librarian", kwargs={"pk": self.book_instance.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_403_if_no_permission(self):
        self.client.login(username="regular", password="testpassword123")
        url = reverse("renew-book-librarian", kwargs={"pk": self.book_instance.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_get_returns_form(self):
        self.client.login(username="librarian", password="testpassword123")
        url = reverse("renew-book-librarian", kwargs={"pk": self.book_instance.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_post_valid_date_redirects(self):
        self.client.login(username="librarian", password="testpassword123")
        url = reverse("renew-book-librarian", kwargs={"pk": self.book_instance.pk})
        valid_date = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(url, {"due_back": valid_date})
        self.assertRedirects(response, reverse("all-borrowed"))

    def test_post_invalid_past_date_shows_error(self):
        self.client.login(username="librarian", password="testpassword123")
        url = reverse("renew-book-librarian", kwargs={"pk": self.book_instance.pk})
        past_date = datetime.date.today() - datetime.timedelta(days=1)
        response = self.client.post(url, {"due_back": past_date})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "due_back", "Invalid date - renewal in past"
        )

    def test_post_date_too_far_shows_error(self):
        self.client.login(username="librarian", password="testpassword123")
        url = reverse("renew-book-librarian", kwargs={"pk": self.book_instance.pk})
        far_date = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(url, {"due_back": far_date})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "due_back",
            "Invalid date - renewal more than 4 weeks ahead",
        )
