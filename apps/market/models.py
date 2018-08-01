from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from django.db.models import CharField, Model, BooleanField, DecimalField
from django.contrib.postgres.fields import ArrayField

    



import bcrypt
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')




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
    def upload_design(self, postData, postFiles):
        errors = []
        if len(postData['name']) == 0:
            errors.append("Shirt design requires a name")
        if len(postData['desc']) < 3:
            errors.append("Shirt requires a description greater than 3 characters")
        if len(Design.objects.filter(name__iexact = postData['name'])):
            errors.append("This name already exists, try a variation")
        if "category" not in postData:
            errors.append("Category required")
        if "category" in postData:
            if len(postData['category']) > 3:
                errors.append("Only 3 categories allowed")
        if len(postData['design_file']) == 0:
            errors.append("Image of shirt design required!")    
        if len(postData['design_file']) != 0:
            if ".png" not in postData['design_file'] or ".jpg" not in postData['design_file']:
                errors.append('Design must be a valid format (.png or .jpg)')
        if postData['price'] < 5:
            errors.append('Price must be greater than $5')
        if len(errors) > 0:
            return { "errors" : errors }
        
        
        return { }

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
    image = models.FileField(null=False)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)

    categories = ArrayField(
        CharField(max_length=15),
        size = 3
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    designer = models.ForeignKey(User, related_name="designer_uploads")
    objects = DesignManager()

class Spec(models.Model):
    color = models.CharField(max_length=20)
    size = models.CharField(max_length=3)
    surcharge = models.DecimalField(max_digits=3, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    design = models.ForeignKey(Design, related_name="design_specs")

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
    products = models.ManyToManyField(Spec, related_name="products_ordered")
    