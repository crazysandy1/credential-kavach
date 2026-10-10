from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate JWT token for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email of the user to generate token for',
        )
        parser.add_argument(
            '--user-type',
            type=str,
            choices=['college', 'company'],
            help='Type of user to create if user does not exist',
        )
        parser.add_argument(
            '--org-name',
            type=str,
            help='Organization name for new user',
        )
        parser.add_argument(
            '--create',
            action='store_true',
            help='Create user if they do not exist',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output as JSON',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        user_type = options.get('user_type')
        org_name = options.get('org_name')
        create_user = options.get('create', False)
        json_output = options.get('json', False)

        if not email:
            self.stdout.write(self.style.ERROR('Email is required'))
            return

        try:
            user = User.objects.get(email=email)
            self.stdout.write(f'Found existing user: {user.email} ({user.user_type})')
        except User.DoesNotExist:
            if create_user:
                if not user_type:
                    self.stdout.write(self.style.ERROR('--user-type is required when creating new user'))
                    return
                if not org_name:
                    self.stdout.write(self.style.ERROR('--org-name is required when creating new user'))
                    return

                user = User.objects.create_user(
                    email=email,
                    username=email,
                    password='testpassword123',  # Default test password
                    user_type=user_type,
                    organization_name=org_name
                )
                self.stdout.write(self.style.SUCCESS(f'Created new user: {user.email} ({user.user_type})'))
            else:
                self.stdout.write(self.style.ERROR(f'User with email {email} not found. Use --create to create new user.'))
                return

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        if json_output:
            token_data = {
                'user_id': user.id,
                'email': user.email,
                'user_type': user.user_type,
                'organization_name': user.organization_name,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            self.stdout.write(json.dumps(token_data, indent=2))
        else:
            self.stdout.write(self.style.SUCCESS('\n=== JWT Token Generated ==='))
            self.stdout.write(f'User ID: {user.id}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'User Type: {user.user_type}')
            self.stdout.write(f'Organization: {user.organization_name}')
            self.stdout.write(f'\nAccess Token:\n{access_token}')
            self.stdout.write(f'\nRefresh Token:\n{refresh_token}')
            self.stdout.write(f'\nCurl Example:')
            self.stdout.write(f'curl -H "Authorization: Bearer {access_token}" http://localhost:8000/api/health/')
