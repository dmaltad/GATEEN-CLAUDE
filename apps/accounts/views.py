from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Address, Pet
from .forms import ProfileForm, AddressForm, PetForm


@login_required
def profile_view(request):
    from django.utils import timezone

    user_plan = None
    try:
        from apps.plans.models import UserPlan
        user_plan = UserPlan.objects.filter(
            user=request.user, status='active'
        ).first()
    except Exception:
        pass

    loyalty = None
    try:
        loyalty = request.user.loyalty_account
    except Exception:
        pass

    user_appointments = []
    try:
        from apps.appointments.models import Appointment
        user_appointments = list(
            Appointment.objects
            .filter(user=request.user)
            .select_related('pet', 'user_plan__plan')
            .order_by('scheduled_at')[:6]
        )
    except Exception:
        pass

    return render(request, 'accounts/profile.html', {
        'user_plan':         user_plan,
        'loyalty':           loyalty,
        'pets':              request.user.pets.all(),
        'addresses':         request.user.addresses.all(),
        'user_appointments': user_appointments,
        'recent_orders': (
            request.user.orders
            .prefetch_related('items__product')
            .order_by('-created_at')[:5]
        ),
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def add_address(request):
    raw_next = (
        request.POST.get('next', '')
        or request.GET.get('next', '')
    ).strip()

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Endereço adicionado com sucesso!')

            # Proteção contra Open Redirect
            if raw_next and url_has_allowed_host_and_scheme(
                raw_next, allowed_hosts={request.get_host()}
            ):
                return redirect(raw_next)
            return redirect('accounts:profile')
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {
        'form': form,
        'next': raw_next,
    })


@login_required
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            messages.success(request, f'{pet.name} adicionado!')
            return redirect('accounts:profile')
    else:
        form = PetForm()
    return render(request, 'accounts/pet_form.html', {'form': form})


@login_required
def edit_pet(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, f'{pet.name} atualizado!')
            return redirect('accounts:profile')
    else:
        form = PetForm(instance=pet)
    return render(request, 'accounts/pet_form.html', {
        'form':    form,
        'pet':     pet,
        'editing': True,
    })


@login_required
def delete_pet(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        name = pet.name
        pet.delete()
        messages.success(request, f'{name} removido.')
        return redirect('accounts:profile')
    return render(request, 'accounts/pet_confirm_delete.html', {'pet': pet})

def complete_registration(request, uidb64, token):
    """
    Rota própria para walk-in clients completarem o cadastro via link de convite.
    Não depende do fluxo interno do allauth.
    """
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str

    # Decodifica UID e busca o usuário
    user = None
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    token_valid = user is not None and default_token_generator.check_token(user, token)

    if not token_valid:
        return render(request, 'accounts/complete_registration_invalid.html')

    if request.method == 'POST':
        p1 = request.POST.get('password1', '').strip()
        p2 = request.POST.get('password2', '').strip()

        if not p1:
            messages.error(request, 'Informe uma senha.')
        elif p1 != p2:
            messages.error(request, 'As senhas não conferem.')
        elif len(p1) < 8:
            messages.error(request, 'A senha deve ter pelo menos 8 caracteres.')
        else:
            user.set_password(p1)
            if hasattr(user, 'is_walk_in'):
                user.is_walk_in = False
            user.save()

            from django.contrib.auth import login as auth_login
            auth_login(
                request, user,
                backend='django.contrib.auth.backends.ModelBackend',
            )
            messages.success(
                request,
                f'Bem-vindo(a), {user.first_name}! 🐾 Seu cadastro está completo.'
            )
            return redirect('home')

    return render(request, 'accounts/complete_registration.html', {
        'target_user': user,
        'uidb64':      uidb64,
        'token':       token,
    })