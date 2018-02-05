from django.contrib import admin
import mallard_qr
from aristotle_mdr.register import register_concept


register_concept(mallard_qr.models.Question)
"""
register_concept(mallard_qr.models.QualityStatement,
    extra_fieldsets = [
            ('Data Quality Guidelines',
                {'fields': ['timeliness','accessibility','interpretability','relevance','accuracy','coherence']}),
            ('Implementation dates',
                {'fields': ['implementationStartDate','implementationEndDate']}),
    ]
)
"""
