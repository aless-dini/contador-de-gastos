from django.urls import path
from . import views

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path("", views.lista_gastos, name="gastos"),
    path("agregar/", views.agregar_gasto, name="agregar"),
    path("editar/<int:gasto_id>", views.editar_gastos, name="editar_gastos"),
    path("eliminar/<int:gasto_id>", views.eliminar_gastos, name="eliminar_gastos")
    
]