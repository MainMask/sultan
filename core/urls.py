from django.urls import path
from core.views.auth_views import login_view, logout_view
from core.views.dashboard_views import dashboard_view
from core.views.training_views import (
    training_list, training_create, training_edit,
    training_delete, training_detail, training_unlock,
)
from core.views.exercise_views import (
    exercise_list, exercise_create, exercise_edit, exercise_delete,
)
from core.views.athlete_views import (
    athlete_list, athlete_create, athlete_edit,
    athlete_detail, athlete_delete,
)
from core.views.admin_views import (
    user_list, user_create, user_edit, user_delete,
    trainer_list, trainer_create, trainer_edit, trainer_delete,
    group_list, group_create, group_edit, group_delete,
)

urlpatterns = [
    path('', dashboard_view, name='root'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # Тренировки
    path('trainings/', training_list, name='training_list'),
    path('trainings/add/', training_create, name='training_create'),
    path('trainings/<int:pk>/', training_detail, name='training_detail'),
    path('trainings/<int:pk>/edit/', training_edit, name='training_edit'),
    path('trainings/<int:pk>/delete/', training_delete, name='training_delete'),
    path('trainings/<int:pk>/unlock/', training_unlock, name='training_unlock'),

    # Упражнения
    path('exercises/', exercise_list, name='exercise_list'),
    path('exercises/add/', exercise_create, name='exercise_create'),
    path('exercises/<int:pk>/edit/', exercise_edit, name='exercise_edit'),
    path('exercises/<int:pk>/delete/', exercise_delete, name='exercise_delete'),

    # Атлеты
    path('athletes/', athlete_list, name='athlete_list'),
    path('athletes/add/', athlete_create, name='athlete_create'),
    path('athletes/<int:pk>/', athlete_detail, name='athlete_detail'),
    path('athletes/<int:pk>/edit/', athlete_edit, name='athlete_edit'),
    path('athletes/<int:pk>/delete/', athlete_delete, name='athlete_delete'),

    # Группы
    path('groups/', group_list, name='group_list'),
    path('groups/add/', group_create, name='group_create'),
    path('groups/<int:pk>/edit/', group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', group_delete, name='group_delete'),

    # Тренеры
    path('trainers/', trainer_list, name='trainer_list'),
    path('trainers/add/', trainer_create, name='trainer_create'),
    path('trainers/<int:pk>/edit/', trainer_edit, name='trainer_edit'),
    path('trainers/<int:pk>/delete/', trainer_delete, name='trainer_delete'),

    # Пользователи (admin)
    path('users/', user_list, name='user_list'),
    path('users/add/', user_create, name='user_create'),
    path('users/<int:pk>/edit/', user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', user_delete, name='user_delete'),
]
