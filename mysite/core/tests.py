# tests.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Section

class SectionTestCase(TestCase):
    def test_file_upload(self):
        test_file = SimpleUploadedFile(
            "test.pdf", 
            b"file_content", 
            content_type="application/pdf"
        )
        section = Section.objects.create(
            titre="Test",
            contenu="Contenu",
            fichier=test_file
        )
        self.assertTrue(section.fichier)