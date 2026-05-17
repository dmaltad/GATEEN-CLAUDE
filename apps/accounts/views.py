from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Address, Pet
from .forms import ProfileForm, AddressForm, PetForm


@login_required
def profile_view(request):
    user_plan = None
    try:
        from apps.plans.models import UserPlan
        user_plan = UserPlan.objects.filter(user=request.user, status='active').first()
    except Exception:
        pass

    loyalty = None
    try:
        loyalty = request.user.loyalty_account
    except Exception:
        pass

    return render(request, 'accounts/profile.html', {
        'user_plan': user_plan,
        'loyalty': loyalty,
        'pets': request.user.pets.all(),
        'addresses': request.user.addresses.all(),
        'recent_orders': request.user.orders.all()[:5],
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
    next_url = request.GET.get('next') or request.POST.get('next') or 'accounts:profile'

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Endereço adicionado com sucesso!')
            # Redireciona para next (pode ser checkout)
            if next_url.startswith('/'):
                return redirect(next_url)
            return redirect(next_url)
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {
        'form': form,
        'next': next_url,
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
    from django.shortcuts import get_object_or_404
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ {pet.name} atualizado com sucesso!')
            return redirect('accounts:profile')
    else:
        form = PetForm(instance=pet)
    return render(request, 'accounts/pet_form.html', {
        'form': form,
        'pet': pet,
        'editing': True,
    })


@login_required
def delete_pet(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        name = pet.name
        pet.delete()
        messages.success(request, f'🗑 {name} removido.')
        return redirect('accounts:profile')
    return render(request, 'accounts/pet_confirm_delete.html', {'pet': pet})