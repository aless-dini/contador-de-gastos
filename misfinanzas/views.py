from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Gasto
from .models import Presupuesto
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth
import json

def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"!Bienvenido {user.username}!")
            return redirect("gastos")
        else:
            messages.error(request, "Error en el registro. Verifica los datos")
    else:
        form = UserCreationForm()
        
    return render(request, "registro.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"!Bienvenido de vuelta, {username}")
                return redirect("gastos")
            else: 
                messages.error(request, "Usuario o contraseña incorrectos")
        else: 
            messages.error(request, "Usuario o contraseña incorrectos") 
    else: 
        form = AuthenticationForm()
         
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente")
    return redirect("login")

@login_required
def gastos(request):
    gastos = Gasto.objects.filter(user=request.user).order_by("-fecha")
    
    categoria = request.GET.get("categoria", "")
    if categoria:
        gastos = gastos.filter(categoria=categoria)
    
    categorias = Gasto.objects.filter(user=request.user).values_list('categoria', flat=True).distinct()
    
    periodo = request.GET.get("periodo", "")
    hoy = timezone.now().date()
    if periodo == "semana":
        gastos = gastos.filter(fecha__gte=hoy - timedelta(days=7))
    if periodo == "mes":
        gastos = gastos.filter(fecha__year=hoy.year, fecha__month=hoy.month)
    
    total = gastos.aggregate(Sum('precio'))['precio__sum'] or 0
    
    gastos_por_categoria = (
        gastos
        .values("categoria")
        .annotate(total=Sum("precio"))
        .order_by("-total")
    )
    categorias_grafico = [item["categoria"] for item in gastos_por_categoria]
    totales_categoria = [float(item["total"]) for item in gastos_por_categoria]
    
    gastos_por_mes = (
        gastos
        .annotate(mes=TruncMonth("fecha"))
        .values("mes")
        .annotate(total=Sum("precio"))
        .order_by("mes")
    )
    
    meses = [item["mes"].strftime("%B %Y") for item in gastos_por_mes]
    totales_mes = [float(item["total"]) for item in gastos_por_mes]
    
    gastos_mes = Gasto.objects.filter(
        user=request.user,
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).aggregate(Sum('precio'))['precio__sum'] or 0
    
    try:
        presupuesto = Presupuesto.objects.get(
            user=request.user,
            mes=hoy.month,
            año=hoy.year
        )
        limite = presupuesto.monto
    except Presupuesto.DoesNotExist:
        limite = 1200000
    
    # Alertas
    alerta = None
    if limite:
        porcentaje_presupuesto = (gastos_mes / float(limite)) * 100
        if porcentaje_presupuesto >= 100:
            alerta = "excedido"
        elif porcentaje_presupuesto >= 80:
            alerta = "cerca"
    
    context = {
        "gastos": gastos,
        "total": total,
        "categorias": categorias,
        "categoria_sel": categoria,
        "periodo_sel": periodo,
        "gastos_mes": gastos_mes,
        "limite": limite,
        "alerta": alerta,
        "porcentaje_presupuesto" : round(porcentaje_presupuesto, 1),
        "categorias_json": json.dumps(categorias_grafico),
        "totales_cagegoria_json": json.dumps(totales_categoria),
        "meses_json": json.dumps(meses),
        "totales_mes_json": json.dumps(totales_mes),
    }
    
    return render(request, "gastos_html", context)
@login_required
def agregar_gasto(request):
    if request.method == "POST":
        precio = request.POST["precio"]
        categoria = request.POST["categoria"]
        descripcion = request.POST["descripcion"]
        fecha = request.POST["fecha"]
        
        Gasto.objects.create(
            precio=precio,
            categoria=categoria,
            descripcion=descripcion,
            fecha=fecha,
            user=request.user
        )
        
        return redirect("gastos")
    
    return render(request, "agregar_gasto.html")

@login_required
def editar_gastos(request, gasto_id):
    gasto = get_object_or_404(Gasto, id=gasto_id, usuario=request.user)
    
    if request.method == "POST":
        precio = request.POST["precio"]
        categoria = request.POST["categoria"]
        descripcion = request.POST["descripcion"]
        fecha = request.POST["fecha"]
        gasto.save()
        messages.success(request, "Gasto actualizado correctamente")
        return redirect("gastos")
    
    return render(request, "editar_gasto.html", {"gasto": gasto})

@login_required 
def eliminar_gastos(request, gasto_id):
    gasto = get_object_or_404(Gasto, id=gasto_id, usuario=request.user)
    gasto.delete()
    messages.success(request, "Gasto eliminado correctamente")
    return redirect("gastos")
        
@login_required
def agregar_presupuesto(request):
    if request.method == "POST":
        monto = request.POST["monto"]
        mes = request.POST["mes"]
        año = request.POST["año"]
        
        if Presupuesto.objects.filter(user=request.user, mes=mes, año=año).exists():
            messages.error(request, "Ya tienes un presupuesto para ese mes")
            return redirect("agregar_presupuesto")
        
        Presupuesto.objects.create(
            user=request.user,
            monto=monto,
            mes=mes,
            año=año
        )
        messages.success(request, "Presupuesto guardado correctamente")
        return redirect(gastos)

    hoy = timezone.now().date()
    return render (request, "agregar_presupuesto.html", {
        "mes_actual": hoy.month,
        "año_actual": hoy.year,
    })