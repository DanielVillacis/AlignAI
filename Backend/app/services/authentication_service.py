import jwt 
import datetime
from flask import current_app, request
from domain.models import db
from domain.entities import User
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from werkzeug.security import generate_password_hash

class AuthService:
    @staticmethod
    def register_user(data):
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return None, "Email already registered"

        # Create new user
        new_user = User(
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            provider='email'
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate tokens
        access_token = AuthService.generate_token(new_user)
        refresh_token = AuthService.generate_refresh_token(new_user)
        
        return {
            'user': new_user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, None

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return None, "Invalid credentials"
        
        # Generate tokens
        access_token = AuthService.generate_token(user)
        refresh_token = AuthService.generate_refresh_token(user)
        
        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, None
        
    @staticmethod
    def google_auth(token):
        try:
            # Validate Google token
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                os.environ.get('GOOGLE_CLIENT_ID')
            )
            
            email = idinfo['email']
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Create new user if it doesn't exist
                user = User(
                    email=email,
                    first_name=idinfo.get('given_name', ''),
                    last_name=idinfo.get('family_name', ''),
                    provider='google',
                    provider_id=idinfo['sub']
                )
                db.session.add(user)
                db.session.commit()
            elif user.provider != 'google':
                # Update existing user provider if they used a different login method before
                user.provider = 'google'
                user.provider_id = idinfo['sub']
                db.session.commit()
                
            # Generate tokens
            access_token = AuthService.generate_token(user)
            refresh_token = AuthService.generate_refresh_token(user)
            
            return {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, None
            
        except ValueError as e:
            return None, str(e)
    
    @staticmethod
    def apple_auth(identity_token):
        # Apple auth implementation
        # Requires Apple's auth library and developer account
        # This is a placeholder
        pass
    
    @staticmethod
    def refresh_auth_token(refresh_token):
        try:
            payload = jwt.decode(
                refresh_token,
                current_app.config.get('SECRET_KEY'),
                algorithms=['HS256']
            )
            
            user_id = payload['sub']
            user = User.query.get(user_id)
            
            if not user:
                return None, "Invalid user"
                
            new_token = AuthService.generate_token(user)
            return {'access_token': new_token}, None
            
        except jwt.ExpiredSignatureError:
            return None, "Refresh token expired"
        except jwt.InvalidTokenError:
            return None, "Invalid refresh token"
    
    @staticmethod
    def generate_token(user):
        payload = {
            'sub': user.id,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'is_admin': user.is_admin
        }
        
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    
    @staticmethod
    def generate_refresh_token(user):
        payload = {
            'sub': user.id,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }
        
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
        
    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(
                token,
                current_app.config.get('SECRET_KEY'),
                algorithms=['HS256']
            )
            
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"

