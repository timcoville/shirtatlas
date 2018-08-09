from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from django.db.models import CharField, Model, BooleanField, DecimalField, IntegerField
from django.contrib.postgres.fields import ArrayField

import os
from decimal import *


AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME_STATIC = 'shirtatlas-static'
AWS_STORAGE_BUCKET_NAME_MEDIA = 'shirtatlas-media'

import bcrypt
import re
import boto3

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

s3 = boto3.resource('s3')



class UserManager(models.Manager):
    def create_user(self, postData):
        # Validations
        errors = []
        if len(postData['name']) < 5:
            errors.append("Name must be 5 or more characters")
        if len(postData['password']) < 8:
            errors.append("Password must be 8 or more characters")
        if postData['password'] != postData['c_password']:
            errors.append("Passwords do not match")
        if not EMAIL_REGEX.match(postData['email']):
            errors.append("Email is not valid, please try again")
        if len(User.objects.filter(email = postData['email'])):
            errors.append("Email is already registered")
        if len(postData['address']) == 0:
            errors.append("Address is required")
        if len(postData['city']) == 0:
            errors.append("City is required")
        if postData['state'] == 'Choose...':
            errors.append("State is required")
        if len(postData['zip_code']) == 0:
            errors.append("Zipcode is required")
        if len(postData['zip_code']) != 0 and len(postData['zip_code']) !=5:
            errors.append("Valid zipcode is required")    
        if len(errors) > 0:
            return { "errors" : errors }
        #Hash
        pw = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt())
        #Creating Record
        the_user = User.objects.create(
            name=postData['name'],
            address=postData['address'],
            email=postData['email'],
            city=postData['city'],
            state=postData['state'],
            zip_code=postData['zip_code'],
            password=pw)
        return { "user" : the_user }
    
    def login_user(self, postData):
        errors = ["Email or Password Invalid"]
        #Checking if user record exists
        try:
            the_user = User.objects.get(email = postData['email'])
        except:
            return { "errors" : errors }
        #Validating Password
        if bcrypt.checkpw(postData['password'].encode(), the_user.password.encode()):
            return { "user" : the_user }
        return { "errors" : errors }
    
    def update_password(self, postData):
        the_user = User.objects.get(id = postData['id'])
        if bcrypt.checkpw(postData['password'].encode(), the_user.password.encode()):    
            errors = []
            if len(postData['new_password']) < 8:
                errors.append("Password must be 8 or more characters")
            if postData['new_password'] != postData['c_password']:
                errors.append("New password does not match")
            if bcrypt.checkpw(postData['new_password'].encode(), the_user.password.encode()):   
                errors.append("New password cannot be the same as your current password") 
            if len(errors) > 0:
                return {"errors":errors}
            pw = bcrypt.hashpw(postData['new_password'].encode(), bcrypt.gensalt())
            the_user.password = pw
            the_user.save()
            return {"user": the_user}
        else:
            return {"errors": ["Current Password is not correct"]}

    def update_profile(self, postData):
        errors = []
        the_user = User.objects.get(id = postData['id'])
        if len(postData['name']) < 5:
            errors.append("Name must be 5 or more characters")
        if not EMAIL_REGEX.match(postData['email']):
            errors.append("Email is not valid, please try again")
        if len(User.objects.filter(email = postData['email'])) and the_user.email != postData['email']:
            errors.append("Email is already registered")
        if len(postData['address']) == 0:
            errors.append("Address is required")
        if len(postData['city']) == 0:
            errors.append("City is required")
        if postData['state'] == 'Choose...':
            errors.append("State is required")
        if len(postData['zip_code']) == 0:
            errors.append("Zipcode is required")
        if len(postData['zip_code']) != 0 and len(postData['zip_code']) !=5:
            errors.append("Valid zipcode is required")    
        if len(errors) > 0:
            return { "errors" : errors }
        
        the_user.name = postData['name']
        the_user.email = postData['email']
        the_user.address = postData['address']
        the_user.city = postData['city']
        the_user.state = postData['state']
        the_user.zip_code = postData['zip_code']
        the_user.save()
        return {"user": the_user}
            

class DesignManager(models.Manager):
    def edit_design(self, postData, postFiles):
        the_design = Design.objects.get(id=postData['design_id'])
        print(postFiles)
        
        new_design_file = True
        new_display_image = True
        
        try:
            design_file_type = postFiles['design_file'].content_type
        except:
            new_design_file = False
        try:
            display_image_type = postFiles['design_image'].content_type
        except:
            new_display_image = False

        errors = []
        
        if len(postData['desc']) < 10:
            errors.append("Shirt requires a description greater than 9 characters")
        if the_design.name != postData['name']:
            if len(postData['name']) == 0:
                errors.append("Shirt design requires a name")
            if len(Design.objects.filter(name__iexact = postData['name'])):
                errors.append("This name already exists, try a variation")
        if "category" in postData:
            cats = postData.getlist('category')
        else:
            cats = the_design.categories
        if len(cats) > 3:
            errors.append("Only 3 categories allowed")
        if new_design_file:
            if design_file_type != 'image/png' and design_file_type != 'image/jpg':
                errors.append('Design file must be a valid format (.png or .jpg)')
        if new_display_image:
            if display_image_type != 'image/png' and display_image_type != 'image/jpg':
                errors.append('Display image must be a valid format (.png or .jpg)')    
        if postData['price'] < 5 or postData['price'] == '':
            errors.append('Price must be greater than $4')
        if postData['licenses'] < 1 or postData['licenses'] == '':
            errors.append('Licenses must be greater than 0')
        if len(errors) > 0:
            return { "errors" : errors }
        
        if new_design_file:
            media_key = the_design.design_file
            s3.Bucket(AWS_STORAGE_BUCKET_NAME_MEDIA).put_object(Key=media_key, Body=postFiles['design_file'])

            
        if new_display_image:
            static_key = the_design.display_image
            s3.Bucket(AWS_STORAGE_BUCKET_NAME_STATIC).put_object(Key=static_key, Body=postFiles['design_image'])
        

        the_design.name = postData['name']
        the_design.desc = postData['desc']
        the_design.categories = cats
        the_design.licenses = postData['licenses']
        the_design.price = postData['price']
        the_design.save()
        
        return {'design': the_design}


    def upload_design(self, postData, postFiles):
        if "category" in postData:
            cats = postData.getlist('category')
        print(postFiles)
        try:
            design_file_name = postFiles['design_file'].name
            design_file_type = postFiles['design_file'].content_type
        except:
            design_file_name = ""
        
        try:
            design_image_name = postFiles['design_image'].name
            design_image_type = postFiles['design_image'].content_type
        except:
            design_image_name = ""

        errors = []
        if len(postData['name']) == 0:
            errors.append("Shirt design requires a name")
        if len(postData['desc']) < 10:
            errors.append("Shirt requires a description greater than 9 characters")
        if len(Design.objects.filter(name__iexact = postData['name'])):
            errors.append("This name already exists, try a variation")
        if not "category" in postData:
            errors.append("Category required")
        if "category" in postData:
            if len(cats) > 3:
                errors.append("Only 3 categories allowed")
        if len(design_file_name) == 0:
            errors.append("Design file required")    
        if len(design_file_name) != 0:
            if design_file_type != 'image/png' and design_file_type != 'image/jpg':
                errors.append('Design must be a valid format (.png or .jpg)')
        if len(design_image_name) == 0:
            errors.append("Display image required")    
        if len(design_image_name) != 0:
            if design_image_type != 'image/png' and design_image_type != 'image/jpg':
                errors.append('Design must be a valid format (.png or .jpg)')
        if postData['price'] < 5:
            errors.append('Price must be greater than $4')
        if postData['licenses'] < 1:
            errors.append('Licenses must be greater than 0')
        if len(errors) > 0:
            return { "errors" : errors }

        static_key = postData['user_id'] + "$%#" + design_image_name
        media_key = postData['user_id'] + design_file_name

        s3.Bucket(AWS_STORAGE_BUCKET_NAME_STATIC).put_object(Key=static_key, Body=postFiles['design_image'])
        s3.Bucket(AWS_STORAGE_BUCKET_NAME_MEDIA).put_object(Key=media_key, Body=postFiles['design_file'])

        the_design = Design.objects.create(
            name = postData['name'],
            desc = postData['desc'],
            display_image = static_key,
            design_file = media_key,
            price = postData['price'],
            licenses = postData['licenses'],
            categories = cats,
            designer = User.objects.get(id=postData['user_id'])
        )
        
        return {"design": the_design}

class User(models.Model):   
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=5)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    designer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Design(models.Model):
    name = models.CharField(max_length=30)
    desc = models.TextField(null=True)
    display_image = models.CharField(max_length=100)
    design_file = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    licenses = models.IntegerField(null=False)
    categories = ArrayField(
        CharField(max_length=30),
        size = 3
    )
    sales = models.IntegerField(default=0)
    on_sale = models.BooleanField(default=False)
    paused = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    designer = models.ForeignKey(User, related_name="designer_uploads")
    objects = DesignManager()

    @property
    def total_revenue(self):
        return self.price * self.sales

    def sale_price(self):
        discount = self.price * Decimal(.9)
        return format(float(discount), '.2f')

    def savings(self):
        discount = self.price * Decimal(.1)
        return format(float(discount), '.2f')


class Order(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=5)
    order_cost = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    buyer = models.ForeignKey(User, related_name="user_purchases")
    products = models.ManyToManyField(Design, related_name="products_ordered")
    