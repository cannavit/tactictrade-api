from rest_framework.test import APITestCase
from apps.authentication.models import User
import random
import string


class TestModel(APITestCase):

    def test_create_user(self):

        # Create random name and email
        name = ''.join(random.choice(string.ascii_uppercase +
                       string.digits) for _ in range(10))
        email = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for _ in range(10)) + '@test.com'

        user = User.objects.create_user(
            username=name,
            email=email,
            password='Passw0rd!')

        self.assertIsInstance(user, User)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_verified)
        self.assertEqual(user.email, email)

    def test_create_super_user(self):

        # Create random name and email
        name = ''.join(random.choice(string.ascii_uppercase +
                       string.digits) for _ in range(10))
        email = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for _ in range(10)) + '@staff.com'

        user = User.objects.create_superuser(
            username=name,
            email=email,
            password='Passw0rd!')

        self.assertIsInstance(user, User)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_verified)
        self.assertEqual(user.email, email)

    def test_message_create_user_when_not_user_name_is_supplied(self):

        # Create random name and email
        email = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for _ in range(10)) + '@test.com'

        self.assertRaises(ValueError, User.objects.create_user, username="", email=email,
                          password='Passw0rd!')
        
        self.assertRaisesMessage(ValueError, "Users must have an username")

    def test_create_user_when_not_user_name_is_supplied(self):

        # Create random name and email
        email = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for _ in range(10)) + '@test.com'

        self.assertRaises(ValueError, User.objects.create_user, username="", email=email,
                          password='Passw0rd!')
        
    def test_create_user_when_not_user_email_is_supplied(self):

        # Create random name and email
        name = ''.join(random.choice(string.ascii_uppercase +
                       string.digits) for _ in range(10))

        self.assertRaises(ValueError, User.objects.create_user, username=name, email="",
                          password='Passw0rd!')
        
    def test_message_create_user_when_not_user_email_is_supplied(self):

        # Create random name and email
        name = ''.join(random.choice(string.ascii_uppercase +
                       string.digits) for _ in range(10))

        self.assertRaises(ValueError, User.objects.create_user, username=name, email="",
                          password='Passw0rd!')

        self.assertRaisesMessage(ValueError, "Users must have an email address")

    
    # def test_create_super_user_when_not_user_passwordd_is_supplied(self):

    #     # Create random name and email
    #     email = ''.join(random.choice(string.ascii_uppercase + string.digits)
    #                     for _ in range(10)) + '@test.com'


    #     name = ''.join(random.choice(string.ascii_uppercase +
    #                    string.digits) for _ in range(10))

    #     self.assertRaises(ValueError, User.objects.create_superuser, username=name, email=email,
    #                       password=None)