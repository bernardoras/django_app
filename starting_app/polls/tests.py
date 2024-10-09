from django.test import TestCase

# Create your tests here.
import datetime

from django.utils import timezone

from .models import Question, Choice

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)


    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_question_str(self):
        """
        Test the string representation of a Question.
        """
        time = timezone.now()
        question = Question(question_text="Sample Question", pub_date=time)
        self.assertEqual(str(question), f"Sample Question ({time})")

    def test_choice_str(self):
        """
        Test the string representation of a Choice.
        """
        question = Question.objects.create(question_text="Sample Question", pub_date=timezone.now())
        choice = Choice.objects.create(question=question, choice_text="Sample Choice", votes=0)
        self.assertEqual(str(choice), "choice: Sample Choice")

    from django.urls import reverse

    def create_question(question_text, days):
        """
        Create a question with the given `question_text` and published the
        given number of `days` offset to now (negative for questions published
        in the past, positive for questions that have yet to be published).
        """
        time = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(question_text=question_text, pub_date=time)

from django.urls import reverse

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )

class QuestionDetailViewTests(TestCase):
    
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionIntegrationTests(TestCase):

    def test_create_and_display_question(self):
        """
        Test the entire flow of creating a question and verifying its display
        on the index page.
        """
        question = create_question(question_text="Integration Test Question", days=-1)
        
        response = self.client.get(reverse("polls:index"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Integration Test Question")
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

class QuestionDetailIntegrationTests(TestCase):
    def test_create_and_view_detail(self):
        """
        Test the flow from creating a question to viewing its detail page.
        """
        question = create_question(question_text="Detail Integration Test", days=-1)
        
        url = reverse("polls:detail", args=(question.id,))
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Integration Test")



class QuestionCreateEditIntegrationTests(TestCase):
    def test_create_and_edit_question(self):
        """
        Test the flow of creating a question and then editing it.
        """
        question = create_question(question_text="Edit Test Question", days=-1)
        
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(question.question_text, "Edit Test Question")
        
        question.question_text = "Edited Test Question"
        question.save()
        
        updated_question = Question.objects.get(id=question.id)
        self.assertEqual(updated_question.question_text, "Edited Test Question")
        
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "Edited Test Question")

class VoteViewTests(TestCase):

    def create_question_with_choices(self, question_text, days, choices):
        """
        Helper method to create a question with a given number of choices.
        `days` is used to create a pub_date offset from now.
        `choices` is a list of choice texts to be added to the question.
        """
        time = timezone.now() + timezone.timedelta(days=days)
        question = Question.objects.create(question_text=question_text, pub_date=time)
        for choice_text in choices:
            question.choice_set.create(choice_text=choice_text, votes=0)
        return question

    def test_vote_on_existing_question(self):
        """
        Test a successful vote on a question.
        """
        question = self.create_question_with_choices("Question?", -1, ["Choice 1", "Choice 2"])
        choice_id = question.choice_set.first().id  # Get the ID of the first choice
        response = self.client.post(reverse('polls:vote', args=(question.id,)), {'choice': choice_id})
        self.assertRedirects(response, reverse('polls:results', args=(question.id,)))
        # Verify the vote count increased
        question.refresh_from_db()
        selected_choice = question.choice_set.get(pk=choice_id)
        self.assertEqual(selected_choice.votes, 1)
