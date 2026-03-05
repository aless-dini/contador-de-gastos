from django.urls import path
from . import views

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path("", views.gastos, name="gastos"),
    path("agregar_gasto/", views.agregar_gasto, name="agregar_gasto"),
    path("presupuesto/", views.agregar_presupuesto, name="presupuesto"),
    path("editar/<int:gasto_id>", views.editar_gastos, name="editar_gastos"),
    path("eliminar/<int:gasto_id>", views.eliminar_gastos, name="eliminar_gastos")   
]