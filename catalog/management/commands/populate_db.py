import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalog.models import Author, Genre, Language, Book, BookInstance
from faker import Faker

class Command(BaseCommand):
    help = "Populate the database with dummy data for better UI visualization."

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        self.stdout.write("Cleaning up existing data...")
        BookInstance.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()
        Genre.objects.all().delete()
        Language.objects.all().delete()

        self.stdout.write("Creating Genres...")
        genres_names = ["Science Fiction", "Fantasy", "Mystery", "Thriller", "Biography", "History", "Science", "Romance", "Poetry", "Technology"]
        genres = [Genre.objects.create(name=name) for name in genres_names]

        self.stdout.write("Creating Languages...")
        langs_names = ["English", "French", "German", "Spanish", "Japanese"]
        languages = [Language.objects.create(name=name) for name in langs_names]

        self.stdout.write("Creating Authors...")
        authors = []
        for _ in range(20):
            dob = fake.date_of_birth(minimum_age=25, maximum_age=90)
            dod = None
            if random.random() < 0.2: # 20% chance author is deceased
                dod = fake.date_between(start_date=dob, end_date="now")
            
            author = Author.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=dob,
                date_of_death=dod
            )
            authors.append(author)

        self.stdout.write("Creating Books...")
        books = []
        for _ in range(50):
            book = Book.objects.create(
                title=fake.sentence(nb_words=4).rstrip("."),
                author=random.choice(authors),
                summary=fake.paragraph(nb_sentences=5),
                isbn=fake.isbn13().replace("-", ""),
                language=random.choice(languages)
            )
            # Add 1-3 random genres
            selected_genres = random.sample(genres, random.randint(1, 3))
            book.genre.add(*selected_genres)
            books.append(book)

        self.stdout.write("Creating BookInstances...")
        status_choices = ["m", "o", "a", "r"]
        for _ in range(100):
            book = random.choice(books)
            status = random.choices(status_choices, weights=[10, 30, 50, 10], k=1)[0]
            due_back = None
            if status != "a":
                due_back = fake.date_between(start_date="-1m", end_date="+1m")
            
            BookInstance.objects.create(
                book=book,
                imprint=fake.company() + " (" + fake.year() + ")",
                status=status,
                due_back=due_back
            )

        self.stdout.write(self.style.SUCCESS("Successfully populated the database with dummy data!"))
