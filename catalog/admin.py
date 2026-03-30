from django.contrib import admin

from .models import Author, Book, BookInstance, Genre, Language


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "date_of_birth", "date_of_death")
    fields = ["first_name", "last_name", ("date_of_birth", "date_of_death")]
    search_fields = ("last_name", "first_name")


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "display_genre")
    list_filter = ("genre", "language")
    search_fields = ("title", "author__last_name", "isbn")
    inlines = [BooksInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ("book", "status", "borrower", "due_back", "id")
    list_filter = ("status", "due_back")
    search_fields = ("book__title", "id")
    fieldsets = (
        (
            None,
            {
                "fields": ("book", "imprint", "id"),
            },
        ),
        (
            "Availability",
            {
                "fields": ("status", "due_back", "borrower"),
            },
        ),
    )
