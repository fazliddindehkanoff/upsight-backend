from django.urls import path
from .views import (
    news_list,
    news_detail,
    news_create,
    news_update,
    news_delete,
    notices_list,
    notice_detail,
    notice_create,
    notice_update,
    notice_delete,
    translations_list,
    translation_detail,
    translation_create,
    translation_update,
    translation_delete,
    information_list,
    information_detail,
    information_create,
    information_update,
    information_delete,
    information_documents_list,
    information_document_detail,
    information_document_create,
    information_document_update,
    information_document_delete,
)

urlpatterns = [
    # News endpoints
    path("news", news_list, name="news_list"),
    path("news/create", news_create, name="news_create"),
    path("news/<int:news_id>", news_detail, name="news_detail"),
    path("news/<int:news_id>/update", news_update, name="news_update"),
    path("news/<int:news_id>/delete", news_delete, name="news_delete"),
    
    # Notice endpoints
    path("notices", notices_list, name="notices_list"),
    path("notices/create", notice_create, name="notice_create"),
    path("notices/<int:notice_id>", notice_detail, name="notice_detail"),
    path("notices/<int:notice_id>/update", notice_update, name="notice_update"),
    path("notices/<int:notice_id>/delete", notice_delete, name="notice_delete"),
    
    # Translation endpoints
    path("translations", translations_list, name="translations_list"),
    path("translations/create", translation_create, name="translation_create"),
    path("translations/<int:translation_id>", translation_detail, name="translation_detail"),
    path("translations/<int:translation_id>/update", translation_update, name="translation_update"),
    path("translations/<int:translation_id>/delete", translation_delete, name="translation_delete"),
    
    # Information endpoints
    path("information", information_list, name="information_list"),
    path("information/create", information_create, name="information_create"),
    path("information/<int:information_id>", information_detail, name="information_detail"),
    path("information/<int:information_id>/update", information_update, name="information_update"),
    path("information/<int:information_id>/delete", information_delete, name="information_delete"),
    
    # Information Documents endpoints
    path("information-documents", information_documents_list, name="information_documents_list"),
    path("information-documents/create", information_document_create, name="information_document_create"),
    path("information-documents/<int:document_id>", information_document_detail, name="information_document_detail"),
    path("information-documents/<int:document_id>/update",
         information_document_update, name="information_document_update"),
    path("information-documents/<int:document_id>/delete",
         information_document_delete, name="information_document_delete"),
]