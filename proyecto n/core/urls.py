from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('asientos/', views.lista_asientos, name='lista_asientos'),
    path('asientos/crear/', views.crear_asiento, name='crear_asiento'),
    path('asientos/<int:asiento_id>/', views.ver_asiento, name='ver_asiento'),
    # Reportes
    path('reportes/balance/', views.balance_comprobacion, name='balance_comprobacion'),
    path('reportes/estado-resultados/', views.estado_resultados, name='estado_resultados'),
    path('reportes/balance-general/', views.balance_general, name='balance_general'),
    path('reportes/libro-mayor/', views.libro_mayor, name='libro_mayor'),
    
    # Documentos (Importar/Exportar)
    path('importar/asientos-csv/', views.importar_asientos_csv, name='importar_asientos_csv'),
    path('exportar/asientos-csv/', views.exportar_asientos_csv, name='exportar_asientos_csv'),
    path('exportar/balance-csv/', views.exportar_balance_csv, name='exportar_balance_csv'),
    path('exportar/plantilla-csv/', views.exportar_plantilla_csv, name='exportar_plantilla_csv'),
]