from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
import shortuuid


# Create your models here.


class User(AbstractUser):
    username = models.CharField(unique=True, max_length=100)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        email_username, mobile = self.email.split('@')
        if self.full_name == "" or self.full_name == None:
            self.full_name = email_username
        if self.username == "" or self.username == None:
            self.username = email_username
        super(User, self).save(*args, **kwargs)    
        
        
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)            
    image = models.FileField(upload_to='image', default='default/default-user.jpg', null=True, blank=True)
    full_name = models.CharField(unique=True, max_length=100, null=True, blank=True)
    bio = models.CharField(max_length=100, null=True, blank=True)
    about = models.CharField(max_length=100, null=True, blank=True)
    author = models.BooleanField(default=False)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
            self.full_name = self.user.username
        super(Profile, self).save(*args, **kwargs) 
        
        
def creat_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance) 
               
                       
def save_profile(sender, instance, **kwargs):
    instance.profile.save()             
               
post_save.connect(creat_user_profile, sender=User)   
post_save.connect(save_profile, sender=User)


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to="image", null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)    
        
    def post_count(self):
        return Post.objects.filter(category=self).count()      
            
class Post(models.Model):
    STATUS = ( 
        ("Active", "Active"), 
        ("Draft", "Draft"),
        ("Disabled", "Disabled"),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS, default="Active")
    title = models.CharField(max_length=100)
    tags = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to="image", null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    view = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="likes_user")
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Post"
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + shortuuid.uuid()[:2]
        super(Post, self).save(*args, **kwargs)
                
            
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    comment = models.TextField()
    reply = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title} - {self.name}"
    
    class Meta:
        verbose_name_plural = "Comment"
        
        
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title} - {self.user.username}"
    
    class Meta:
        verbose_name_plural = "Bookmark"


