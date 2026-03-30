import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from catalog.forms import RenewBookForm
from catalog.models import Author, Book, BookInstance, Genre


@login_required
def index(request):
    """View function for home page of site."""

    # Generate counts of main objects
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_available = BookInstance.objects.filter(status="a").count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()

    # Session-based visit counter
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_genres": num_genres,
        "num_visits": num_visits,
    }

    return render(request, "index.html", context=context)


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status="o")
            .order_by("due_back")
        )


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan.

    Only visible to users with can_mark_returned permission.
    """

    model = BookInstance
    permission_required = "catalog.can_mark_returned"
    template_name = "catalog/bookinstance_list_borrowed_all.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status="o").order_by("due_back")


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == "POST":
        form = RenewBookForm(request.POST, instance=book_instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("all-borrowed"))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(
            instance=book_instance,
            initial={"due_back": proposed_renewal_date},
        )

    context = {
        "form": form,
        "book_instance": book_instance,
    }

    return render(request, "catalog/book_renew_librarian.html", context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    permission_required = "catalog.add_author"


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    permission_required = "catalog.change_author"


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy("author")
    permission_required = "catalog.delete_author"


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre", "language"]
    permission_required = "catalog.add_book"


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre", "language"]
    permission_required = "catalog.change_book"


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy("books")
    permission_required = "catalog.delete_book"