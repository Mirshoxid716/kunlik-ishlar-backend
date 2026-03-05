from django.db import models

class Worker(models.Model):
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)
    age = models.IntegerField(blank=True, null=True)
    passport_id = models.CharField(max_length=50, blank=True, null=True)
    passport_photo = models.ImageField(upload_to='passport_photos/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='workers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_blacklisted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Botdan o'tgan user"
        verbose_name_plural = "Botdan o'tgan userlar"

    def __str__(self):
        return self.full_name

class Job(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    title = models.CharField(max_length=255)
    wage = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    transport = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    client_tg_username = models.CharField(max_length=100, blank=True, null=True)
    location_url = models.URLField(max_length=500, blank=True, null=True)
    required_workers = models.IntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    unical_id = models.CharField(max_length=50, unique=True)
    channel_post_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ish"
        verbose_name_plural = "Ishlar"

    def __str__(self):
        return f"{self.unical_id} - {self.title}"

class Application(models.Model):
    STATUS_CHOICES = [
        ('waiting_payment', 'To\'lov kutilmoqda'),
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    location_photo = models.ImageField(upload_to='location_photos/', blank=True, null=True)
    payment_receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Ariza"
        verbose_name_plural = "Arizalar"

    def __str__(self):
        return f"{self.worker.full_name} - {self.job.unical_id}"
