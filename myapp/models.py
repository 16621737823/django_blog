from django.db import models
from datetime import datetime

now = datetime.now()
time = now.strftime("%d %B %Y")

class Post(models.Model):
    postname = models.CharField(max_length=255)  # MySQL 对 VARCHAR 处理更高效
    category = models.CharField(max_length=255)
    image_path = models.CharField(max_length=500, blank=True, null=True)  # 存储图片路径
    content = models.TextField()
    time = models.CharField(default=time, max_length=100, blank=True)
    likes = models.IntegerField(null=True, blank=True, default=0)
    user_id = models.IntegerField()  # 代替 ForeignKey(User)

    def __str__(self):
        return str(self.postname)


class Comment(models.Model):
    content = models.TextField()
    time = models.CharField(default=time, max_length=100, blank=True)
    post_id = models.IntegerField()  # 代替 ForeignKey(Post)
    user_id = models.IntegerField()  # 代替 ForeignKey(User)

    def __str__(self):
        return f"{self.id}.{self.content[:20]}..."


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    subject = models.CharField(max_length=1000)
    message = models.TextField(blank=True)
