from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from . import views_cbv

# URLs del Portal de Clientes
portal_patterns = [
    path('login/', views.client_login, name='client_login'),
    path('logout/', views.client_logout_view, name='client_logout'),
    path('dashboard/', views.portal_dashboard, name='portal_dashboard'),
    path('prestamo/<int:pk>/', views.portal_loan_detail, name='portal_loan_detail'),
    path('change-password/', views.client_change_password, name='client_change_password'),
    path('request-loan/', views.request_loan, name='portal_request_loan'),

    # Flujo de Reseteo de Contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='portal/password_reset_form.html'), name='client_password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='portal/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='portal/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='portal/password_reset_complete.html'), name='password_reset_complete'),
]

# Este archivo define las URLs que son específicas de la app `dashboard`.
urlpatterns = [
    path('', views.panel_informativo, name='panel_informativo'),
    path('profile/', views.profile, name='profile'),

    # --- URLs para Clientes ---
    # Muestra la tabla de clientes.
    # path('clientes/', views.client_list, name='client_list'),
    path('clientes/', views_cbv.ClientListView.as_view(), name='client_list'),
    # Muestra el formulario para añadir un nuevo cliente.
    # path('clientes/nuevo/', views.client_add, name='client_add'),
    path('clientes/nuevo/', views_cbv.ClientCreateView.as_view(), name='client_add'),
    # Muestra el formulario para editar un cliente existente.
    # path('clientes/<int:pk>/editar/', views.client_edit, name='client_edit'),
    path('clientes/<int:pk>/editar/', views_cbv.ClientUpdateView.as_view(), name='client_edit'),

    # Muestra el perfil y el historial de un cliente específico.
    path('clientes/<int:pk>/', views.client_detail, name='client_detail'),

    # --- URLs para Préstamos ---
    # Muestra el formulario para añadir un nuevo préstamo.
    path('prestamos/nuevo/', views.loan_add, name='loan_add'),
    # Muestra los detalles de un préstamo específico y su tabla de amortización.
    path('prestamos/<int:pk>/', views.loan_detail, name='loan_detail'),
    # Ruta para la versión imprimible de los detalles del préstamo
    path('prestamos/<int:pk>/imprimir/', views.loan_detail_print, name='loan_detail_print'),
    # Muestra la lista de préstamos activos.
    # path('prestamos/activos/', views.loan_list, name='loan_list'),
    path('prestamos/activos/', views_cbv.LoanListView.as_view(), name='loan_list'),
    path('prestamos/solicitudes/', views.loan_application_list, name='loan_application_list'),
    path('prestamos/solicitudes/<int:pk>/', views.loan_application_detail, name='loan_application_detail'),
    path('prestamos/solicitudes/<int:pk>/aprobar/', views.loan_application_approve, name='loan_application_approve'),
    path('prestamos/solicitudes/<int:pk>/rechazar/', views.loan_application_reject, name='loan_application_reject'),
    path('prestamos/pagados/', views.paid_loan_list, name='paid_loan_list'),

    # --- URLs para Pagos ---
    # Muestra el formulario para registrar un nuevo pago.
    path('pagos/nuevo/<int:loan_id>/', views.payment_add, name='payment_add'),
    # Ruta para la versión imprimible de un recibo de pago.
    path('pagos/recibo/', views.payment_receipt_print, name='payment_receipt_print'),

    # --- URLs para Cobros ---
    path('cobros/', views.cobros_list, name='cobros_list'),

    # --- URLs para Select2 AJAX ---
    path('search/clients/', views.search_clients, name='search_clients'),
    path('search/cuotas/', views.search_cuotas, name='search_cuotas'),

    # --- API URLs ---
    path('api/tipo-prestamo/<int:pk>/', views.get_tipo_prestamo_details, name='get_tipo_prestamo_details'),
    path('api/calculate-amortization/', views.calculate_amortization_api, name='calculate_amortization_api'),

    # --- URLs para Finanzas ---
    path('finanzas/', views.financial_details, name='financial_details'),

    # --- URLs del Portal de Clientes ---
    path('portal/', include(portal_patterns)),
]