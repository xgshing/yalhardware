from django.db import models


class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    about_html = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Profile'
        verbose_name_plural = 'Company Profile'

    def __str__(self):
        return self.company_name or 'Company Profile'


class CompanyAboutImage(models.Model):
    company = models.ForeignKey(
        CompanyProfile,
        related_name='about_images',
        on_delete=models.CASCADE,
    )
    image = models.URLField(max_length=500)
    sort = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort']
